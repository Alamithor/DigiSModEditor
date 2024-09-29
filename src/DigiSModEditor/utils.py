from os import PathLike
from pathlib import Path
from typing import Union


def get_root_dir() -> Path:
    return Path(__file__).resolve().parent


def get_ui_dir() -> Path:
    return get_root_dir() / 'ui_file'


def get_ui_file(ui_name: str) -> Path:
    return get_ui_dir() / f'{ui_name}.ui'


def get_default_preference_dir() -> Path:
    pref_dir = Path.home() / 'Documents' / 'DigiSModEditor'
    if not pref_dir.exists():
        pref_dir.mkdir(parents=True)
    return pref_dir


def get_project_mods_dir(root_dir: Union[PathLike, Path] = None) -> Path:
    if root_dir is None:
        root_dir = get_default_preference_dir()
    default_project_dir = root_dir / 'Mods'
    if not default_project_dir.exists():
        default_project_dir.mkdir(parents=True)
    return default_project_dir


def get_packed_mods_dir(root_dir: Union[PathLike, Path] = None) -> Path:
    if root_dir is None:
        root_dir = get_default_preference_dir()
    default_packed_mods_dir = root_dir / 'PackedMods'
    if not default_packed_mods_dir.exists():
        default_packed_mods_dir.mkdir(parents=True)
    return default_packed_mods_dir


def float_to_tuple(value: float) -> tuple[int, int]:
    integer_part = int(value)
    fractional_part = int((value - integer_part) * 10)
    return integer_part, fractional_part


def tuple_to_float(value: tuple[int, int]) -> float:
    return value[0] + value[1] / 10
