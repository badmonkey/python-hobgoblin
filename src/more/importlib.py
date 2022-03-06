import importlib as _importlib
import pkgutil
from importlib import *  # noqa


def subpackages(package):
    if isinstance(package, str):
        package = _importlib.import_module(package)
        yield package

    for _, name, is_pkg in pkgutil.walk_packages(package.__path__):
        if name.startswith("test_") or name.endswith("_test"):
            continue

        full_name = package.__name__ + "." + name
        subpack = _importlib.import_module(full_name)
        yield subpack

        if is_pkg:
            yield from subpackages(subpack)


def import_submodules(package):
    return [x.__name__ for x in subpackages(package)]
