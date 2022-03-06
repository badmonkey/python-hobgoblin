import click as _click


class ReadableDir(_click.Path):
    def __init__(self):
        super().__init__(exists=True, file_okay=False, resolve_path=True)


class WritableDir(_click.Path):
    def __init__(self):
        super().__init__(exists=True, file_okay=False, writable=True, resolve_path=True)


class ReadableFile(_click.Path):
    def __init__(self):
        super().__init__(exists=True, dir_okay=False, resolve_path=True)


class SaveableFile(_click.Path):
    def __init__(self):
        super().__init__(exists=False, dir_okay=False, writable=True, resolve_path=True)
