import os
import pathlib as _pathlib
import shutil
from pathlib import *  # noqa


class _PatchPath:
    def removedirs(self, delete_files=False):
        if self._closed:
            self._raise_closed()
        if delete_files:
            shutil.rmtree(self.__fspath__())
        else:
            os.removedirs(self.__fspath__())


_pathlib.Path.removedirs = _PatchPath.removedirs
