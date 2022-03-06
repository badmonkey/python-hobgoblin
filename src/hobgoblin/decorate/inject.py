import inspect

from decorum import Decorum

import codefresh.meta.helper as helper


class pass_this_in(Decorum):
    def init(self, assigned=None, **addvars):
        super().init(assigned=assigned)
        self.addvars = addvars

    def wraps(self, f):
        argnames = inspect.getfullargspec(f).args
        if not argnames:
            raise ValueError("decorated function needs atleast one parameter")

        this = argnames.pop(0)
        called_by = f"{f.__name__}({', '.join(argnames)})"

        helper.add_docstring_line(
            f,
            f"To call this function use `{called_by}`, "
            f"a reference to the current function is passed into `{this}` "
            f"(inserted as the first arg)",
            fill_empty=True,
        )
        if hasattr(self, "addvars"):
            context = vars(f)

            for k, v in self.addvars.items():
                name = k if k.startswith("_") else f"_{k}"
                context.setdefault(name, v)
                helper.add_docstring_line(
                    f,
                    f"Variable `{this}.{name}` (init: {v}) "
                    f"has been injected into this function",
                )
        return super().wraps(f)

    def call(self, *args, **kwargs):
        return super().call(self._wrapped, *args, **kwargs)


class inject(Decorum):
    def init(self, assigned=None, **addvars):
        super().init(assigned=assigned)
        self.addvars = addvars

    def wraps(self, f):
        if hasattr(self, "addvars"):
            context = vars(self)

            for k, v in self.addvars.items():
                name = k if k.startswith("_") else f"_{k}"
                context.setdefault(name, v)
                helper.add_docstring_line(
                    f,
                    f"Variable `{f.__name__}.{name}` (init: {v}) "
                    f"has been injected into this function",
                    fill_empty=True,
                )
        return super().wraps(f)
