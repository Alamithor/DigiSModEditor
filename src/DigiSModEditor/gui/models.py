import logging
import os
from os import PathLike
from pathlib import Path
from typing import Union, Tuple, Dict, Generator

from PySide6.QtCore import QTimer
from PySide6.QtGui import QStandardItemModel, QStandardItem

from .. import core
from .. import constants as const
from .. import errors as err
from .. import decorators as deco

__all__ = [
    'create_game_data_model',
    'create_dsdb_model',
    'create_project_mods_model',
]

log = logging.getLogger(const.LogName.MAIN)


class AsukaModel(QStandardItemModel):
    """Model which hold DSDB information, files, and folders structure"""
    def __init__(self, dir_path: Union[PathLike, Path]):
        super().__init__()
        self._root_path = Path(dir_path)
        self._src_path = Path(dir_path)

        self._queue = []

        self._timer = QTimer()
        self._timer.setInterval(50)
        self._timer.timeout.connect(self.process_queue)
        self._timer.start()

    @property
    def root_path(self) -> Path: return self._root_path

    @property
    def src_path(self) -> Path: return self._src_path

    def add_to_queue(self, asset_structure):
        """
        Add asset structure to the queue for processing.

        :param asset_structure: A dictionary where the top level keys are the asset names.
                                The values are dictionaries where the keys are the asset group names and the values are lists of asset file names.
        """
        log.debug(f'Add to queue: {asset_structure}')
        self._queue.append(asset_structure)

    def process_queue(self):
        """
        Process asset structure queue. If the queue is not empty, it will take the first item and add it to the model.

        This method is connected to a QTimer with 50ms interval.
        """
        if self._queue:
            asset_structure = self._queue.pop(0)
            log.debug(f'Process queue: {self._queue}')
            self.add_asset_item(asset_structure)

    def add_asset_item(self, asset_structure):
        """
        Add a new asset item to the model.

        The asset item is a hierarchical structure of QStandardItem.
        The root item is the asset name.
        The children of the root item are the asset group names.
        The children of the group items are the asset file names.

        The asset file items have the following data:

            - const.ItemData.NAME: The name of the asset file without extension
            - const.ItemData.EXT: The extension of the asset file
            - const.ItemData.FILENAME: The full name of the asset file
            - const.ItemData.FILEPATH: The full path of the asset file

        :param asset_structure: A dictionary where the top level keys are the asset names.
                                The values are dictionaries where the keys are the asset group names and the values are lists of asset file names.
        """
        for k, v in asset_structure.items():
            # asset root item
            root_item = QStandardItem(k)
            root_item.setCheckable(True)

            for child_grp, child_list in v.items():
                # asset group item
                group_item = QStandardItem(child_grp)
                for child_item in child_list:
                    name, ext = os.path.splitext(child_item)
                    # asset files item
                    file_item = QStandardItem(child_item)
                    file_item.setData(name, const.ItemData.NAME)
                    file_item.setData(ext, const.ItemData.EXT)
                    file_item.setData(child_item, const.ItemData.FILENAME)
                    file_item.setData(os.path.join(self.src_path, child_item), const.ItemData.FILEPATH)
                    group_item.appendRow(file_item)
                root_item.appendRow(group_item)

            self.appendRow(root_item)

    def find_item_by_name(self, asset_name: str) -> Union[QStandardItem, None]:
        """
        Find a QStandardItem with the given asset name.

        Iterate through all the root items and check if the text of each item matches the given asset name.
        If a match is found, return the item. Otherwise, return None.

        :param asset_name: The name of the asset to find
        :return: The QStandardItem with the given asset name, or None if not found
        """
        for row in range(self.rowCount()):
            item = self.item(row)
            if item.text() == asset_name:
                return item
        return None

    def get_files_item_by_asset_item(self, asset_item: QStandardItem) -> Generator[QStandardItem, None, None]:
        """
        Get the QStandardItem of all asset files under the given asset item.

        This will iterate through all the children of the given asset item and yield the QStandardItem of each file if it has children.
        The yielded item is a QStandardItem which contains the file name, extension, file path, etc. in its data role.

        :param asset_item: The asset item to get the files from
        :return: A generator of all asset file QStandardItem
        """
        for row in range(self.rowCount()):
            item = asset_item.child(row)
            if item:
                if item.hasChildren():
                    for row_child in range(item.rowCount()):
                        child_item = item.child(row_child)
                        yield child_item

    def get_files_path_by_asset_item(self, asset_item: QStandardItem) -> Generator[Path, None, None]:
        """
        Get the paths of all asset files under the given asset item.

        :param asset_item: The asset item to get the files from
        :return: A generator of all asset file paths
        """
        for each_item in self.get_files_item_by_asset_item(asset_item):
            yield Path(each_item.data(const.ItemData.FILEPATH))

    def get_files_name_by_asset_item(self, asset_item: QStandardItem) -> Generator[str, None, None]:
        """
        Get the names of all asset files under the given asset item.

        :param asset_item: The asset item to get the files from
        :return: A generator of all asset file names
        """
        for each_item in self.get_files_item_by_asset_item(asset_item):
            yield each_item.data(const.ItemData.FILENAME)

    @staticmethod
    def get_asset_structure_by_asset_item(asset_item: QStandardItem) -> Dict:
        """
        Get asset structure by asset item.

        The asset structure is a dictionary where the top level keys are the asset names.
        The values are dictionaries where the keys are the asset group names and the values are lists of asset file names.

        The structure is as follows:
        {
            'asset_name': {
                'group_name': ['file1', 'file2', ...]
            }
        }

        :param asset_item: The asset item to get the structure from
        :return: The asset structure as a dictionary
        """
        result = {}
        if asset_item.hasChildren():
            result[asset_item.text()] = {}
            for row_group in range(asset_item.rowCount()):
                item_grp = asset_item.child(row_group)
                result[item_grp.text()] = [item_grp.child(row).text() for row in range(item_grp.rowCount())]
        return result


class AmaterasuModel(AsukaModel):
    """Model which hold project mods information, files, and folders structure"""
    def __init__(self, dir_path: Union[PathLike, Path], metadata: dict, description: str):
        super().__init__(dir_path)
        self._root_path = dir_path.parent
        self._name = metadata.get('name')
        self._author = metadata.get('author')
        self._version = metadata.get('version')
        self._category = metadata.get('category')
        self._description = description
        self._mods_info_changes = False

    @property
    def title(self) -> str: return self._name

    @property
    def author(self) -> str: return self._author

    @property
    def version(self) -> Tuple[int, int]: return self._version

    @property
    def category(self) -> str: return self._category

    @property
    def description(self) -> str: return self._description

    def set_title(self, title: str):
        if title == '':
            raise err.EditProjectModsInfoError('Title shouldn\'t empty!')
        if title != self.title:
            self._name = title
            self._mods_info_changes = True

    def set_author(self, author: str):
        if author == '':
            raise err.EditProjectModsInfoError('Author shouldn\'t empty!')
        if author != self.author:
            self._author = author
            self._mods_info_changes = True

    def set_version(self, version: Tuple[int, int]):
        if version[0] < 0 or version[1] < 0:
            raise err.EditProjectModsInfoError('Version should be higher than 0.0')
        if version != self.version:
            self._version = version
            self._mods_info_changes = True

    def set_category(self, category: str):
        if category == '':
            raise err.EditProjectModsInfoError('Category shouldn\'t empty!')
        if category != self.category:
            self._category = category
            self._mods_info_changes = True

    def set_description(self, description: str):
        if description == '':
            raise err.EditProjectModsInfoError('Description shouldn\'t empty!')
        if description != self.description:
            self._description = description
            self._mods_info_changes = True

    def save_information(self):
        if self._mods_info_changes:
            core.write_metadata_mods(self.author, self.version, self.category, self.root_path)
            core.write_description_mods(self.description, self.root_path)


@deco.validate_directory
def create_dsdb_model(dir_path: Union[PathLike, Path]) -> AsukaModel:
    """
    Creates an AsukaModel from a DSDB directory.

    Given a directory path that is a valid DSDB directory,
    creates an AsukaModel object from the metadata and description information
    in the directory.

    :param dir_path: The directory path of the DSDB directory
    :return: An AsukaModel object containing the DSDB metadata and description
    :raises err.InvalidDSDBDirectory: If the directory path is not a valid DSDB directory
    """
    if not core.is_dsdb_directory(dir_path):
        raise err.InvalidDSDBDirectory(f'Invalid DSDB directory: {dir_path}')
    model = AsukaModel(dir_path)
    return model


@deco.validate_directory
def create_project_mods_model(dir_path: Union[PathLike, Path]) -> AmaterasuModel:
    """
    Creates an AmaterasuModel from a project mods directory.

    Given a directory path that is a valid project mods directory,
    creates an AmaterasuModel object from the metadata and description
    information in the directory.

    :param dir_path: The directory path of the project mods directory
    :return: An AmaterasuModel object containing the project mods metadata and description
    :raises err.InvalidProjectModsDirectory: If the directory path is not a valid project mods directory
    """
    if not core.is_project_mods_directory(dir_path):
        raise err.InvalidModsDirectory(f'Invalid project mods directory: {dir_path}')
    metadata = core.read_metadata_mods(dir_path / 'METADATA.json')
    description = core.read_description_mods(dir_path / 'DESCRIPTION.html')
    model = AmaterasuModel(dir_path / 'modfiles', metadata, description)
    return model


@deco.validate_directory
def create_game_data_model(dir_path: Union[PathLike, Path]) -> Union[AsukaModel, AmaterasuModel]:
    """
    Creates an AsukaModel or AmaterasuModel from a game data directory.

    Given a directory path that is a valid DSDB directory or a valid project mods directory,
    creates an AsukaModel or AmaterasuModel object from the metadata and description information
    in the directory.

    :param dir_path: The directory path of the game data directory
    :return: An AsukaModel or AmaterasuModel object containing the game data metadata and description
    :raises err.InvalidGameDataDirectory: If the directory path is not a valid DSDB directory nor a valid project mods directory
    """
    if core.is_dsdb_directory(dir_path):
        model = create_dsdb_model(dir_path)
    elif core.is_project_mods_directory(dir_path):
        model = create_project_mods_model(dir_path)
    else:
        raise err.InvalidGameDataDirectory(f'Invalid game data directory: {dir_path}')
    return model

