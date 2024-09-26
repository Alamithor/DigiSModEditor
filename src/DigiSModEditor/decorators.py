from os import PathLike
from pathlib import Path
from functools import wraps

from . import errors as err


def validate_directory(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            dir_path = args[0]
        except:
            dir_path = kwargs.get('dir_path')

        if not isinstance(dir_path, (Path, PathLike)):
            raise TypeError(f"{dir_path} must be a Path or PathLike object")
        if not dir_path.is_dir():
            raise err.InvalidDirectoryPath(f'Invalid directory path: {dir_path}')
        return func(*args, **kwargs)
    return wrapper
