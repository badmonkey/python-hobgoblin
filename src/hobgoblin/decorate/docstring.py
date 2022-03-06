from decorum import Decorum

import codefresh.dataobjects as dataobjects


def add_docstring_line(f, text, newline=True, bullet="*", bracket=None, fill_empty=False, **kwargs):
    if f is not None:
        if f.__doc__ is None:
            if not fill_empty:
                f.__doc__ = text
                return
            f.__doc__ = f"No docstring for {f.__name__}"

        if newline:
            f.__doc__ += "\n"
        else:
            f.__doc__ += " "

        text = text[:]

        if bracket:
            text = f"{bracket[0]}{text}{bracket[1]}"

        if bullet:
            text = f"{bullet} {text}"

        f.__doc__ += text


class Notes(metatype.DataObject):
    def __setattr_process__(self, name, value):
        def decorator(f):
            add_docstring_line(f, value, fill_empty=True)
            return f

        return name, decorator

    def __call__(self, text, **kwargs):
        def decorator(f):
            add_docstring_line(f, text, fill_empty=True, **kwargs)
            return f

        return decorator


note = Notes()


class note_not_working(Decorum):
    """ Add a note to the end of a functions __doc__ string """

    def init(self, addendum, *args, **kwargs):
        print("DOCSTRING", addendum)
        super().init(*args, **kwargs)
        self.__doc__ = "Dingus"

    def wraps(self, f):
        print("self.__doc__", self.__doc__)
        print("f.__doc__", f.__doc__)
        return super().wraps(f)
