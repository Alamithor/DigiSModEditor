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


def get_app_dir() -> Path:
    """
    Returns the directory where the application specific data is stored.

    The directory is a folder in the user's home directory, in the 'Documents' folder, with the name
    'DigiSModEditor'. If the directory does not exist, it will be created.

    This directory is used to store the project mods and packed mods.

    :return: The directory where the application specific data is stored
    """
    pref_dir = Path.home() / 'Documents' / 'DigiSModEditor'
    if not pref_dir.exists():
        pref_dir.mkdir(parents=True)
    return pref_dir


def get_default_project_mods_dir() -> Path:
    """
    Returns the default directory where the project mods are stored.

    The default directory is a folder in the user's home directory, in the 'Documents' folder,
    with the name 'DigiSModEditor' -> 'ProjectMods'. If the directory does not exist, it will be
    created.

    :return: The default directory where the project mods are stored
    """
    project_dir = get_app_dir() / 'ProjectMods'
    if not project_dir.exists():
        project_dir.mkdir(parents=True)
    return project_dir


def get_default_packed_mods_dir() -> Path:
    """
    Returns the default directory where the packed mods are stored.

    The default directory is a folder in the user's home directory, in the 'Documents' folder,
    with the name 'DigiSModEditor' -> 'PackedMods'. If the directory does not exist, it will be
    created.

    :return: The default directory where the packed mods are stored
    """
    packed_mods_dir = get_app_dir() / 'PackedMods'
    if not packed_mods_dir.exists():
        packed_mods_dir.mkdir(parents=True)
    return packed_mods_dir


def get_default_log_dir() -> Path:
    """
    Returns the default directory where the log files are stored.

    The default directory is a folder in the user's home directory, in the 'Documents' folder,
    with the name 'DigiSModEditor' -> 'Logs'. If the directory does not exist, it will be
    created.

    :return: The default directory where the log files are stored
    """
    log_dir = get_app_dir() / 'Logs'
    if not log_dir.exists():
        log_dir.mkdir(parents=True)
    return log_dir


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
