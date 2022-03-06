from collections import namedtuple

import codefresh.meta.docstring as docstring
import codefresh.more.inspect as inspect
import codefresh.utils as utils


def immutable(fields=None):
    fields = namedtuple("__tmp", fields)._fields if fields is not None else ()

    def decorator(cls):
        pure_bases = ()
        all_fields = ()
        tuple_bases = 0
        for x in cls.__bases__:
            tuple_bases += 1 if issubclass(x, tuple) else 0
            pure_bases += getattr(x, "_pure", () if isinstance(x, tuple) else (x,))
            all_fields += getattr(x, "_fields", ())
        all_fields += fields

        if tuple_bases > 1:
            raise TypeError("Immutable can't inherit from multiple Immutables")

        uniquename = inspect.unique_name(cls)

        pure_type = type(
            f"{uniquename}_PURE_",
            pure_bases,
            utils.copymerge(cls.__dict__, {"__slots__": (), "__module__": cls.__module__}),
        )

        docstring.add_docstring_line(cls, "immutable fields: {}".format(", ".join(all_fields)))

        namespace = {
            "__doc__": cls.__doc__,
            "__slots__": (),
            "__module__": cls.__module__,
            "_tuple": tuple,
            "_pure": (pure_type,),
        }

        tuple_type = namedtuple(f"{uniquename}_TUPLE_", all_fields, module=cls.__module__)

        return type(cls.__name__, (tuple_type, pure_type), namespace)

    return decorator
