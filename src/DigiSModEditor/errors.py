class BaseDigiSException(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class CopyAssetError(BaseDigiSException):
    """Raised if copying asset fails."""


class InvalidDirectoryPath(BaseDigiSException):
    """Raised when the specified path is not a directory."""


class InvalidDSDBDirectory(BaseDigiSException):
    # """Raised if DSDB directory is invalid."""
    """Raised when the specified directory is not valid DSDB directory."""
    def __init__(self, message: str):
        info = 'The directory does not contain any valid *.name file.'
        self.message = f'{message}. {info}'


class InvalidProjectModsDirectory(BaseDigiSException):
    """Raised when the specified directory is not valid project mods directory."""
    def __init__(self, message: str):
        info = 'The directory does not contain a valid METADATA.json file and modfiles subdirectory.'
        self.message = f'{message}. {info}'


class InvalidGameDataDirectory(BaseDigiSException):
    """Raised when the specified directory is not a valid game data directory (either Project mods or DSDB)."""
    def __init__(self, message: str):
        info = 'The directory is not a valid game data directory (either Project mods or DSDB).'
        self.message = f'{message}. {info}'


class WidgetNotFoundError(BaseDigiSException):
    """Raised if widget is not found."""


class CreateProjectModsError(BaseDigiSException):
    """Raised if creating project mods fails."""


class EditProjectModsInfoError(BaseDigiSException):
    """Raised if editing project mods information fails."""
