import os
from os import PathLike
from pathlib import Path
from typing import Union, Tuple, Dict, Generator

from PySide6.QtCore import QTimer
from PySide6.QtGui import QStandardItemModel, QStandardItem

from .. import core
from .. import threads as th
from .. import constants as const
from .. import errors as err
from .. import decorators as deco

__all__ = [
    'create_game_data_model',
    'create_dsdb_model',
    'create_project_mods_model',
]


class AsukaModel(QStandardItemModel):
    """Model which hold DSDB information, files, and folders structure"""
    def __init__(self, dir_path: Union[PathLike, Path]):
        super().__init__()
        self._root_path = Path(dir_path)
        self._src_path = Path(dir_path)

        self._queue = []

        # self._scanner_thread = None
        # self.set_scanner_thread()

        # self._timer = QTimer()
        # self._timer.setInterval(50)
        # self._timer.timeout.connect(self.process_queue)
        # self._timer.start()

    @property
    def root_path(self) -> Path: return self._root_path

    @property
    def src_path(self) -> Path: return self._src_path

    def set_scanner_thread(self):
        # TODO: move this outside, put into gui module
        if self._scanner_thread is None:
            self._scanner_thread = th.ScannerThread(self.src_path)

            self._scanner_thread.file_found.connect(self.add_to_queue)
            # self._scanner_thread.all_scan_finished.connect(self.bar)

            self._scanner_thread.start()

    def add_to_queue(self, asset_structure):
        self._queue.append(asset_structure)

    def process_queue(self):
        if self._queue:
            asset_structure = self._queue.pop(0)
            self.add_asset_item(asset_structure)

    def add_asset_item(self, asset_structure):
        for k, v in asset_structure.items():
            # asset root item
            root_item = QStandardItem(k)

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
        for row in range(self.rowCount()):
            item = self.item(row)
            if item.text() == asset_name:
                return item
        return None

    def get_files_item_by_asset_item(self, asset_item: QStandardItem) -> Generator[QStandardItem, None, None]:
        for row in range(self.rowCount()):
            item = asset_item.child(row)
            if item:
                if item.hasChildren():
                    for row_child in range(item.rowCount()):
                        child_item = item.child(row_child)
                        yield child_item

    def get_files_path_by_asset_item(self, asset_item: QStandardItem) -> Generator[Path, None, None]:
        for each_item in self.get_files_item_by_asset_item(asset_item):
            yield Path(each_item.data(const.ItemData.FILEPATH))

    def get_files_name_by_asset_item(self, asset_item: QStandardItem) -> Generator[str, None, None]:
        for each_item in self.get_files_item_by_asset_item(asset_item):
            yield each_item.data(const.ItemData.FILENAME)

    @staticmethod
    def get_asset_structure_by_asset_item(asset_item: QStandardItem) -> Dict:
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
        self._title = dir_path.parent.name
        self._author = metadata.get('author')
        self._version = metadata.get('version')
        self._category = metadata.get('category')
        self._description = description
        self._mods_info_changes = False

    @property
    def title(self) -> str: return self._title

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
            self._title = title
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
    if not core.is_dsdb_directory(dir_path):
        raise err.InvalidDSDBDirectory(f'Invalid DSDB directory: {dir_path}')
    model = AsukaModel(dir_path)
    return model


@deco.validate_directory
def create_project_mods_model(dir_path: Union[PathLike, Path]) -> AmaterasuModel:
    if not core.is_project_mods_directory(dir_path):
        raise err.InvalidProjectModsDirectory(f'Invalid project mods directory: {dir_path}')
    metadata = core.read_metadata_mods(dir_path / 'METADATA.json')
    description = core.read_description_mods(dir_path / 'DESCRIPTION.html')
    model = AmaterasuModel(dir_path / 'modfiles', metadata, description)
    return model


@deco.validate_directory
def create_game_data_model(dir_path: Union[PathLike, Path]) -> Union[AsukaModel, AmaterasuModel]:
    if core.is_dsdb_directory(dir_path):
        model = create_dsdb_model(dir_path)
    elif core.is_project_mods_directory(dir_path):
        model = create_project_mods_model(dir_path)
    else:
        raise err.InvalidGameDataDirectory(f'Invalid game data directory: {dir_path}')
    return model

