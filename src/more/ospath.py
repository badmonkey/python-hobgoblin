import os
import os.path as _ospath
import tempfile
from os.path import *  # noqa

import codefresh.more.pathlib as pathlib


def expandkw(p, **kwargs):
    try:
        return expand(p).format(**kwargs)
    except KeyError as e:
        val = str(e).strip("'")
        kwargs[val] = "{" + val + "}"


def expand(p):
    return _ospath.expanduser(_ospath.expandvars(p))


def withsep(p):
    if not p.endswith(os.sep):
        return p + os.sep
    return p


def multipath_split(p, asdir=False):
    if p is None:
        return None
    _d = lambda x: withsep(x) if asdir else lambda x: x
    if os.pathsep in p:
        return [_d(x) for x in p.split(os.pathsep)]
    return [_d(p)]


def ensure(p, touch=False):
    _isfile = not p.endswith(os.sep)
    targ = _ospath.dirname(p) if _isfile else p

    os.makedirs(targ, exist_ok=True)

    if _isfile and touch:
        pathlib.Path(p).touch()


def isempty(p):
    try:
        return (not os.listdir(p)) if _ospath.isdir(p) else True
    except os.error:
        return True


def iswritable(p):
    try:
        _isfile = not p.endswith(os.sep)
        targ = _ospath.dirname(p) if _isfile else p

        testfile = tempfile.TemporaryFile(dir=targ)
        testfile.close()

        return True
    except OSError:
        return False


def uniform(path):
    if path is None:
        return None

    # Drop trailing separator unless it's just a separator. e.g. '/' -> '/', '/foo/' -> '/foo'
    if path != os.sep and path[-1] == os.sep:
        path = path[:-1]
    return path


_PERM_TO_OCTAL_ = {"---": 0, "--x": 1, "-w-": 2, "-wx": 3, "r--": 4, "r-x": 5, "rw-": 6, "rwx": 7}


def _split(s, n):
    return s[:n], s[n:]


def perms(strperms):
    val = 0

    while strperms:
        perm, strperms = _split(strperms, 3)
        val = 8 * val + _PERM_TO_OCTAL_[perm]

    return val
