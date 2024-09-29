from os import PathLike
from pathlib import Path
from typing import Union


def get_root_dir() -> Path:
    """
    Returns the root directory of the project.

    The root directory is the directory which contains the src directory.

    :return: The root directory of the project
    """
    return Path(__file__).resolve().parent


def get_ui_dir() -> Path:
    """
    Returns the directory where the UI files are located.

    The UI files are the files with the .ui extension which are used by the UI loader to create the UI.

    :return: The directory where the UI files are located
    """
    return get_root_dir() / 'ui_file'


def get_ui_file(ui_name: str) -> Path:
    """
    Returns the path to the UI file with the given name.

    :param ui_name: The name of the UI file without the .ui extension
    :return: The path to the UI file
    """
    return get_ui_dir() / f'{ui_name}.ui'


def get_default_preference_dir() -> Path:
    """
    Returns the default directory where the preferences will be stored.

    The default directory is a directory in the user's home directory, in the 'Documents' folder,
    with the name 'DigiSModEditor'. If the directory does not exist, it will be created.

    :return: The default directory where the preferences will be stored
    """
    pref_dir = Path.home() / 'Documents' / 'DigiSModEditor'
    if not pref_dir.exists():
        pref_dir.mkdir(parents=True)
    return pref_dir


def get_project_mods_dir(root_dir: Union[PathLike, Path] = None) -> Path:
    """
    Returns the directory where the project mods are stored.

    If the root directory is not specified, the default directory will be used. The default directory
    is a directory in the user's home directory, in the 'Documents' folder, with the name
    'DigiSModEditor'. If the directory does not exist, it will be created.

    The project mods directory will be created if it does not exist.

    :param root_dir: The root directory where the project mods are stored
    :return: The directory where the project mods are stored
    """
    if root_dir is None:
        root_dir = get_default_preference_dir()
    project_dir = root_dir / 'Mods'
    if not project_dir.exists():
        project_dir.mkdir(parents=True)
    return project_dir


def get_packed_mods_dir(root_dir: Union[PathLike, Path] = None) -> Path:
    """
    Returns the directory where the packed mods are stored.

    If the root directory is not specified, the default directory will be used. The default directory
    is a directory in the user's home directory, in the 'Documents' folder, with the name
    'DigiSModEditor'. If the directory does not exist, it will be created.

    The packed mods directory will be created if it does not exist.

    :param root_dir: The root directory where the packed mods are stored
    :return: The directory where the packed mods are stored
    """
    if root_dir is None:
        root_dir = get_default_preference_dir()
    packed_mods_dir = root_dir / 'PackedMods'
    if not packed_mods_dir.exists():
        packed_mods_dir.mkdir(parents=True)
    return packed_mods_dir


def float_to_tuple(value: float) -> tuple[int, int]:
    """
    Converts a float to a tuple of two integers.

    The first element of the tuple will be the integer part of the float and the
    second element will be the fractional part of the float multiplied by 10.

    :param value: The float to convert
    :return: A tuple of two integers
    """
    integer_part = int(value)
    fractional_part = int((value - integer_part) * 10)
    return integer_part, fractional_part


def tuple_to_float(value: tuple[int, int]) -> float:
    """
    Converts a tuple of two integers to a float.

    The first element of the tuple is the integer part of the float and the
    second element is the fractional part of the float divided by 10.

    :param value: The tuple of two integers to convert
    :return: A float
    """
    return value[0] + value[1] / 10
