import builtins

import deprecated as _deprecated
from public import install

if not hasattr(builtins, "deprecated"):
    setattr(builtins, "deprecated", _deprecated.deprecated)

install()
