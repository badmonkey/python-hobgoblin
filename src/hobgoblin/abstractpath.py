import posixpath as _posixpath
from posixpath import *  # noqa


def _update_(g):
    names = [
        "exists",
        "lexists",
        "expanduser",
        "getatime",
        "getmtime",
        "getctime",
        "getsize",
        "isfile",
        "isdir",
        "islink",
        "ismount",
        "sameopenfile",
        "samestat",
        "defpath",
        "devnull",
        "_update_",
    ]
    for f in names:
        del g[f]

    names = ["realpath", "relpath"]

    for f in names:
        rf = f"_replace_{f}"
        g[f] = g[rf]
        del g[rf]


def _replace_realpath(p):
    return _posixpath.normpath(p)


def _replace_relpath(p, start=None):
    return _posixpath.relpath(p, start or _posixpath.sep)


_update_(globals())
