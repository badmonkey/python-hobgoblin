import click as _click
from click import *  # noqa
from click_didyoumean import DYMGroup
from click_help_colors import HelpColorsCommand, HelpColorsGroup

theme = {
    "help.headers": "yellow",
    "help.options": None,
    "help.group.headers": "yellow",
    "help.group.options": "green",
    "help.cmd.headers": "yellow",
    "help.cmd.options": "blue",
    "help.cmd.aliases": "blue",  # todo
}


def _color(*names):
    for x in names:
        if x in theme and theme[x]:
            return theme[x]
    return None


def current_obj():
    ctx = _click.get_current_context()
    return ctx.obj if ctx else None


def fail(code: int = 1):
    _click.get_current_context().exit(code=code)


def exit(code: int = 0):  # noqa:W0622
    _click.get_current_context().exit(code=code)


class CodefreshGroup(DYMGroup, HelpColorsGroup, _click.Group):
    def format_help(self, ctx, formatter):
        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter)
        self.format_options(ctx, formatter)
        self.format_aliases(ctx, formatter)
        self.format_epilog(ctx, formatter)

    def format_aliases(self, ctx, formatter):
        if hasattr(self, "aliases"):
            helpdata = getattr(self, "aliases")
            if not helpdata:
                return
            with formatter.section("Aliases"):  # uses options_color
                formatter.write_dl(helpdata)


class CodefreshCommand(HelpColorsCommand, _click.Command):
    pass


def group(name=None, **attrs):  # noqa
    attrs.setdefault("cls", CodefreshGroup)
    attrs.setdefault("help_headers_color", _color("help.group.headers", "help.headers"))
    attrs.setdefault("help_options_color", _color("help.group.options", "help.options"))
    return _click.group(name, **attrs)


def command(name=None, **attrs):  # noqa
    attrs.setdefault("cls", CodefreshCommand)
    attrs.setdefault("help_headers_color", _color("help.cmd.headers", "help.headers"))
    attrs.setdefault("help_options_color", _color("help.cmd.options", "help.options"))
    # attrs.setdefault("help_aliases_color", _color("help.cmd.aliases"))
    return _click.command(name, **attrs)
