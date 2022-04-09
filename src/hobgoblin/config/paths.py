
import more.enum as enum
import os
from more.ospath import expand
from more.typing import Iterator, Tuple
from more.pathlib import Path
import glob


ConfigDomain = enum.IntEnum('ConfigDomain', "project user system")
ConfigFormat = enum.StrEnum('ConfigFormat', "any yaml ini")
ConfigFindStrategy = enum.IntEnum('ConfigFindStrategy', "all first only_one")
ConfigGlobList = Iterator[Tuple[str, ConfigFormat]]
ConfigPathList = Iterator[Tuple[Path, ConfigFormat]]


_SUPPORTED = [(".yml", ConfigFormat.yaml),
              (".yaml", ConfigFormat.yaml),
              (".ini", ConfigFormat.ini)]


def _project_config(toolname: str):
    paths = [(f"{toolname}.any", ConfigFormat.any),
             (f".project/{toolname}.any", ConfigFormat.any),
             ("setup.cfg", ConfigFormat.ini),
             ("project.any", ConfigFormat.any),
             (".projectrc", ConfigFormat.ini),
             (f".venv/{toolname}.ini", ConfigFormat.any)]
    return paths


def _user_config(toolname: str):
    paths = [(f"~/.config/{toolname}.any", ConfigFormat.any),
             (f"~/.{toolname}.any", ConfigFormat.any),
             (f"~/.{toolname}rc", ConfigFormat.ini),
             (f"/opt/$USER/{toolname}.any", ConfigFormat.any)]
    return paths


def _system_config(toolname: str):
    paths = []
    return paths


def get_candidates(toolname: str, what: ConfigDomain) -> ConfigGlobList:
    def _replace_suffix(s: str, suffix: str) -> str:
        return str(Path(s).with_suffix(suffix))

    match what:
        case ConfigDomain.project:
            configs = _project_config(toolname)
        case ConfigDomain.user:
            configs = _user_config(toolname)
        case ConfigDomain.system:
            configs = _system_config(toolname)

    for p, t in configs:
        p = expand(p)
        if t == ConfigFormat.any:
            for new_suffix, new_t in _SUPPORTED:
                yield (_replace_suffix(p, new_suffix), new_t)
        else:
            yield (p, t)


def find_config(toolname: str,
                what: ConfigDomain = ConfigDomain.user,
                strategy: ConfigFindStrategy = ConfigFindStrategy.all) -> ConfigPathList:
    first_path = None
    cwd = Path.cwd()
    for guess_p, t in get_candidates(toolname, what):
        print("DBG", guess_p, t)
        for p in glob.iglob(guess_p, recursive=True):
            p = Path(p)
            if p.is_file() and os.access(p, os.R_OK):
                yield (p, t)

                match strategy:
                    case ConfigFindStrategy.first:
                        return
                    case ConfigFindStrategy.only_one:
                        if first_path:
                            raise RuntimeError(f"Multiple configs found: {first_path} and {p}")
                        else:
                            first_path = p
                    case _:
                        pass
