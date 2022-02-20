import collections
import sys

import hobgoblin.python as python


def make(*args, _uppercase=False, _cls=None, **kwargs):
    if args:
        keys = [python.intern_friendly(k) for k in args]
        if _uppercase:
            values = [sys.intern(k.upper()) for k in keys]
        else:
            values = keys
    elif kwargs:
        keys = [python.intern_friendly(k) for k in kwargs]
        values = list(kwargs.values())
    else:
        raise TypeError("No enum members given")

    if _cls:
        values = [_cls(k, v) for k, v in zip(keys, values)]

    Enum = collections.namedtuple("Enum", keys)
    return Enum(*values)
