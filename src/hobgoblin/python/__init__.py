import keyword
import sys


@public
def isfriendlyident(name):
    if name and name.isidentifier() and not keyword.iskeyword(name) and not name.startswith("_"):
        return True
    return False


@public
def intern_friendly(name):
    if isfriendlyident(name):
        return sys.intern(str(name))
    raise ValueError(f"{name} must be an identifier, not a keyword, and not start with '_'")
