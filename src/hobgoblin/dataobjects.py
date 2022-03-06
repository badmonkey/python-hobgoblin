import pprint


class objectdict(dict):
    """ A dictionary where elements can be access via class member syntax """

    def __init__(self, *args, **kwargs):
        fields = set(getattr(self, "_fields", [])) | set(args)
        indict = {x: None for x in fields}

        fields |= set(kwargs.keys())
        indict.update(kwargs)

        self._fields = tuple(fields)
        for name in self._fields:
            self.setdefault(name)

        super().__init__(self)
        self.update(indict)
        self.__initialised = True

    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError(f"No such attribute: {name}")

    def __setattr__(self, name, value):
        if "_objectdict__initialised" not in self.__dict__:
            return self.__setattr_init__(name, value)
        name, value = self.__setattr_process__(name, value)
        self[name] = value
        return value

    def __setattr_init__(self, name, value):
        return dict.__setattr__(self, name, value)

    def __setattr_process__(self, name, value):
        return name, value

    def __delattr__(self, name):
        if name in self:
            del self[name]

    def __str__(self):
        return pprint.pformat(self)
