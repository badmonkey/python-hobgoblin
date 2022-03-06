import os
import shlex
import sys
from string import Template
from typing import Dict, List, Tuple

SectionType = Dict[str, str]
ConfigType = Dict[str, SectionType]
ArgvType = List[str]


def format_argv(args=None):
    args = args or sys.argv[:]
    args[0] = os.path.basename(args[0])
    args = [f'"{x}"' if " " in x else x for x in args]
    return " ".join(args)


class AliasedArgv:
    def __init__(self):
        self.exepath: str = sys.argv[0]
        self.exename: str = os.path.basename(sys.argv[0])

        self.original: ArgvType = sys.argv[:]
        self.original[0] = self.exename

        self.aliased: ArgvType = sys.argv
        self.aliased[0] = self.exename

        self.script: Tuple[ArgvType] = ()
        self.other_tmpl: str = "*"
        self.alias_help = []

    def __str__(self):
        return format_argv(self.aliased)

    def update(self, aliases, exename=None, change_argv=False):
        update_argv_aliases(self, aliases, exename=exename, change_argv=change_argv)

    def is_changed(self):
        return any(x != y for x, y in zip(self.original, self.aliased))

    def is_script(self):
        return bool(self.script)

    def print_help(self, ctx):
        if self.alias_help:
            formatter = ctx.make_formatter()
            with formatter.section("Aliases"):
                formatter.write_dl(self.alias_help)
            print(formatter.getvalue())


class Bootstrap:
    def __init__(self):
        self.argv = AliasedArgv()

    def run(self, cmdline_group, exename: str = None, aliases: SectionType = None, **kwargs):
        context = Context(cmdline_group)

        try:
            if aliases:
                self.argv.update(aliases, exename=exename, change_argv=True)
            elif exename:
                self.argv.exename = exename
        except Exception as e:
            # make pretty again
            import traceback

            traceback.print_exc()
            sys.exit(1)

        if exename:
            kwargs.setdefault("prog_name", exename)

        if isinstance(cmdline_group, WrenchGroup):
            setattr(cmdline_group, "aliases", self.argv.alias_help)

        context.obj = self

        kwargs["parent"] = context

        print("SCRIPT", self.argv.is_script())

        # handle running multi-command sys.argv

        result = cmdline_group.main(standalone_mode=False, **kwargs)
        sys.exit(result)


def _match(pattern: ArgvType, args: ArgvType) -> Tuple[bool, ArgvType]:
    env = {}
    for term in pattern:
        if term.startswith("$"):
            if args:
                env[term[1:]] = args.pop(0)
                continue
            return False, env
        if term.startswith("?"):
            k = term[1:]
            if args:
                env[k] = args.pop(0)
            else:
                env[k] = None
            continue
        if not args or args[0] != term:
            return False, env
        args.pop(0)

    env["*"] = args
    return True, env


def _replace(tmpl: ArgvType, env) -> ArgvType:
    if not tmpl:
        return []
    output = []
    for term in tmpl:
        if term.startswith("$"):
            k = term[1:]
            if k == "*":
                raise Exception(f"'$*' is invalid")
            if k not in env:
                raise Exception(f"No value for '{term}'")
            v = env[k]
            if v:
                output.append(v)
            continue
        if term == "*":
            output.extend(env["*"])
            continue
        if "$" in term:
            t = Template(term)
            err = ""
            try:
                output.append(t.substitute(env))
                continue
            except ValueError as e1:
                err = f"{e1} of '{term}'"
            except KeyError as e2:
                err = f"Unknown variable ${str(e2)[1:-1]} in '{term}'"

            raise Exception(err)

        output.append(term)
    return output


def _strip_options(value: ArgvType) -> ArgvType:
    output = []
    for x in value:
        if x == "*" or x.startswith("-") or "=" in x or " " in x:
            return output
        output.append(x)
    return output


def _format_script(args, longdesc=None):
    if isinstance(args, tuple):
        if longdesc:
            return f"{longdesc}\n" + "\n".join([f"'{format_argv(x)}'" for x in args])
        return f"'{format_argv(args[0])}'\n..."
    return f"'{format_argv(args)}'"


def _format_alias(subst, pass_any):
    output = {}
    for k, v in subst:
        fk = _format_script(k)
        if v:
            output[fk] = _format_script(v)
            # output[fk] = _format_script(v, longdesc="Multicommand script...")
        else:
            output[fk] = "Command is ignored"
    output = sorted(output.items(), key=lambda x: x[0])
    if pass_any:
        if len(pass_any) == 1 and pass_any[0] == "*":
            output.append(("Other", f"args are forwarded unchanged"))
        else:
            output.append(("Other", _format_script(pass_any, longdesc="Multicommand script...")))
    else:
        output.append(("Other", "All other commands are ignored"))
    return output


def update_argv_aliases(
    argv: AliasedArgv, cfg: SectionType, exename: str = None, change_argv=False
) -> None:
    exename = exename or os.path.basename(sys.argv[0])
    argv.exename = exename
    argv.aliased[0] = exename

    subst = {}

    for k, v in cfg.items():
        if isinstance(v, list):
            subst[k] = (shlex.split(k), tuple(shlex.split(x) for x in v))
        else:
            subst[k] = (shlex.split(k), shlex.split(v))

    if "*" in subst:
        argv.other_tmpl = subst["*"][1]
        del subst["*"]

    subst = sorted(subst.values(), key=lambda x: len(x[0]), reverse=True)

    argv.alias_help = _format_alias(subst, argv.other_tmpl)

    newargv = False

    for k, v in subst:
        ismatch, env = _match(k, sys.argv[1:])
        if ismatch:
            if isinstance(v, tuple):
                argv.aliased = [exename]
                argv.script = tuple([exename] + _replace(x, env) for x in v)
            else:
                argv.aliased = [exename] + _replace(v, env)
                argv.script = ()
            newargv = True
            break

    if not newargv:
        if isinstance(argv.other_tmpl, tuple):
            pass
        else:
            argv.aliased = [exename] + _replace(argv.other_tmpl, {"*": sys.argv[1:]})
            argv.script = ()

    if change_argv:
        sys.argv = argv.aliased
