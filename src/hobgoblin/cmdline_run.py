from contextlib import contextmanager
import subprocess
import shlex
from pathlib import Path
import os


def _match_all(s):
    return True

class _format_raw:
    def item(self, s):
        return s
    def wrap(self, ls):
        return ls


class Run:
    def __init__(self, cwd = None):
        self.cwd = cwd or Path.cwd()

    def command(self, cmdline: str, *, quiet=True):
        output = subprocess.DEVNULL if quiet else None
        subprocess.run(shlex.split(cmdline),
                       check=True,
                       stdout=output,
                       stderr=output)

    def capture(self, cmdline) -> str:
        result = subprocess.run(shlex.split(cmdline),
                                check=True,
                                capture_output=True,
                                text=True)

        return result.stdout.expandtabs().rstrip("\n")

    def script(self, cmdline) -> str:
        result = subprocess.run(cmdline,
                                shell=True,
                                check=True,
                                capture_output=True,
                                text=True)

        return result.stdout.expandtabs().rstrip("\n")

    def filter(self, cmdline, *, filter = None, format = None):
        filter = filter or _match_all
        format = format or _format_raw()

        result = subprocess.run(shlex.split(cmdline),
                                check=True,
                                capture_output=True,
                                text=True)

        result = result.stdout.expandtabs()

        return format.wrap([format.item(l) for l in result.splitlines() if l and filter(l)])


@contextmanager
def push_working_dir(newCwd: Path):
    if newCwd:
        old = Path.cwd()
        os.chdir(newCwd)
        yield Run(newCwd)
        os.chdir(old)
    else:
        yield Run(Path.cwd())


def python_in_directory(func, dest: Path, *args, **kwargs):
    with push_working_dir(dest) as run:
        return func(run, *args, **kwargs)

def command(cmdline: str, *, cwd: Path=None, **kwargs):
    with push_working_dir(cwd) as run:
        run.command(cmdline, **kwargs)

def capture(cmdline, *, cwd: Path=None) -> str:
    with push_working_dir(cwd) as run:
        return run.capture(cmdline)

def script(cmdline, *, cwd: Path=None) -> str:
    with push_working_dir(cwd) as run:
        return run.script(cmdline)

def filter(cmdline, *, cwd: Path=None, **kwargs):
    with push_working_dir(cwd) as run:
        return run.filter(cmdline, **kwargs)



def columns(*args):
    class _fmt(Format):
        def item(self, s):
            p = s.split()
            return tuple(p[i] for i in args)

        def collection(self, ls):
            return ls

    return _fmt()

def asdict(key, value):
    class _fmt(Format):
        def item(self, s):
            p = s.split()
            return (p[key], p[value])

        def collection(self, ls):
            return dict(ls)

    return _fmt()

def namevalue():
    class _fmt(Format):
        def item(self, s):
            p = s.split("=")
            return (p[0], p[1])

        def collection(self, ls):
            return dict(ls)

    return _fmt()
