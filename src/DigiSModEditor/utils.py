from pathlib import Path


def get_root_dir() -> Path:
    return Path(__file__).resolve().parent


def get_ui_dir() -> Path:
    return get_root_dir() / 'ui_file'


def get_ui_file(ui_name: str) -> Path:
    return get_ui_dir() / f'{ui_name}.ui'


def get_default_project_dir(create_if_not_exists: bool = True) -> Path:
    # user document dir
    default_dir = Path.home() / 'Documents' / 'DigiSModEditor'
    if create_if_not_exists and not default_dir.exists():
        default_dir.mkdir(parents=True)
    return default_dir


def float_to_tuple(value: float) -> tuple[int, int]:
    integer_part = int(value)
    fractional_part = int((value - integer_part) * 10)
    return integer_part, fractional_part
