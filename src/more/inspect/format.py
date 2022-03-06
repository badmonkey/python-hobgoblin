import inspect as _inspect
import pprint

import codefresh.more.inspect as inspect
import codefresh.more.ospath as ospath
import codefresh.more.typing as typing


def linenumber(target):
    """ Given a python callable try and determine the source line number where it is defined """

    if hasattr(target, "__code__"):
        code = getattr(target, "__code__")
        return code.co_firstlineno

    if hasattr(target, "__func__"):
        return linenumber(getattr(target, "__func__"))

    if hasattr(target, "__call__"):
        return linenumber(getattr(target, "__call__"))

    return "??"


def simple(target):
    insttype = type(target)
    inst_longname = f"'{insttype.__module__}.{insttype.__name__}'"
    lineno = linenumber(target)
    hexid = hex(id(target))

    if hasattr(target, "__call__"):
        return f"<() object {inst_longname} at {hexid} line:{lineno}>"

    return f"<object {inst_longname} at {hexid} line:{lineno}>"


def name_of(target: typing.Any) -> str:
    try:
        t_qual = target.__qualname__
        t_mod = target.__module__

        t_longname = f"'{t_mod}.{t_qual}'"
    except Exception:  # noqa: W0703: Catch everything casue we can't narrow
        pass

    if _inspect.isbuiltin(target):
        return f"<() '__builtins__.{t_qual}'>"

    if _inspect.isfunction(target):
        lineno = linenumber(target)

        if target.__name__ == "<lambda>":
            return f"<() λ {t_longname} line:{lineno}>"

        return f"<() {t_longname} line:{lineno}>"

    if _inspect.ismethod(target):
        lineno = linenumber(target)
        t_self = name_of(target.__self__)

        return f"<() method {t_longname} of {t_self} line:{lineno}>"

    if _inspect.isclass(target):
        return pprint.pformat(target)

    return simple(target)


def caller(offset=2) -> str:
    _module, info = inspect.caller(offset)

    if info:
        func = _module.__name__ + f".{info.function}"
        fname = ospath.basename(info.filename)
        return f"{func}() from {fname}#{info.lineno}"
    return "unknown() from ?.py#?"


def print_class(cls: typing.Type, indent: str = ""):
    heading = "CLASS" if not indent else "INHERITS"
    print(f"{indent}{heading}: {cls.__module__}.{cls.__name__} {id(cls)}")
    if cls.__name__ in ("tuple", "object"):
        return
    for k, v in cls.__dict__.items():
        print(f"{indent}| VAR {k}: {type(v)}")
    for x in cls.__bases__:
        print_class(x, indent + "| ")
