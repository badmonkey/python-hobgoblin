import sys as _sys

import hobgoblin.python as python


# usage
# define module atom values
#
# from hobgoblin.atom import name1, name2
#


def __getattr__(name):
    if name.startswith("__"):
        if name not in globals():
            raise AttributeError(f"No {name} in {__name__}")

    name = python.intern_friendly(name)
    if name not in globals():
        globals()[name] = name

    return globals()[name]
