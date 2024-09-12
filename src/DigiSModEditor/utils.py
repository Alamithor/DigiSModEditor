from pathlib import Path


def get_root_dir() -> Path:
    return Path(__file__).resolve().parent


def get_ui_dir() -> Path:
    return get_root_dir() / 'ui_file'


def get_ui_file(ui_name: str) -> Path:
    return get_ui_dir() / f'{ui_name}.ui'
