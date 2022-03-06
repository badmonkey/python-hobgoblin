import contextlib
import functools
import weakref

import codefresh.meta.docstring as docstring


def cache_return(f):
    f._cache = None
    docstring.add_docstring_line(
        f, f"The result of {f.__name__}(...) is cached and return on future calls."
    )

    @functools.wraps(f)
    def _wrap(*pargs, **kwargs):
        if f._cache is None:
            f._cache = f(*pargs, **kwargs)
        return f._cache

    return _wrap


def cache_return_ref(f):
    f._ref = None
    docstring.add_docstring_line(
        f, f"A weakref to the result of {f.__name__}(...) is cached for future calls."
    )

    @functools.wraps(f)
    def _wrap(*pargs, **kwargs):
        obj = f._ref() if f._ref is not None else None
        if obj is None:
            obj = f(*pargs, **kwargs)
            f._ref = weakref.ref(obj)
        return obj

    return _wrap


@contextlib.contextmanager
def holding_ref(x):
    yield x
