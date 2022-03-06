import inspect as _inspect
from inspect import *  # noqa

import codefresh.more.typing as typing


def find_new(cls):
    """ Search mro for a __new__ function """

    for x in _inspect.getmro(cls):
        f = getattr(x, "__new__", None)
        if f:
            return f, x.__name__
    return None, None


def class_by_name(cls: str) -> typing.Type:
    """ Convert fully qualified class name into a class object """

    parts = cls.split(".")
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def unique_name(cls: typing.Type) -> str:
    return f"{cls.__qualname__}".replace(".<locals>", "").replace(".", "_")


def caller(offset=3, ignore=None):
    ignore = ignore or ("decorum", "codefresh")
    callstack = _inspect.stack()

    for info in callstack[offset:]:
        frame = info.frame
        _module = _inspect.getmodule(frame)

        if _module is None:
            break

        if info.function == "__enter__":
            continue

        name = _module.__name__
        for x in ignore:
            if name.startswith(f"{x}."):
                continue

        return _module, info
    return None, None


def caller_module(offset=3, ignore=None):
    _module, _ = caller(offset, ignore)

    if _module:
        return _module.__name__
    return None


def caller_package(offset=3, ignore=None):
    _module, _ = caller(offset, ignore)

    if _module:
        return _module.__name__.split(".")[0]
    return None
