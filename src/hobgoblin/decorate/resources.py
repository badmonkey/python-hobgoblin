import pkg_resources
from decorum import Decorum

import codefresh.more.inspect as inspect


class resource(Decorum):
    """
    @resource('data/file')
    @resource('data/file', package='somepackage')
    """

    def init(self, filepath, *args, package=None, **kwargs):
        package = inspect.find_caller_package() if package is None else package
        if package is None:
            raise Exception("Unable to find package")

        self.package = package
        self.filepath = filepath

        return super().init(*args, **kwargs)

    def call(self, *args, **kwargs):
        return super().call(pkg_resources.resource_stream(self.package, self.filepath))
