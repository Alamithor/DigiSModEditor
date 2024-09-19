import os
from os import PathLike
from pathlib import Path
from typing import Union, Tuple, List

from PySide6.QtCore import QTimer
from PySide6.QtGui import QStandardItemModel, QStandardItem

from . import threads
from .. import core, const


class AsukaModel(QStandardItemModel):
    """Model which hold DSDB information, files, and folders structure"""
    def __init__(self, dir_path: Union[PathLike, Path]):
        super().__init__()
        self._root_path = Path(dir_path)
        self._src_path = Path(dir_path)

        self._queue = []

        self._scanner_thread = None
        self.set_scanner_thread()

        self._timer = QTimer()
        self._timer.setInterval(50)
        self._timer.timeout.connect(self.process_queue)
        self._timer.start()

    @property
    def root_path(self) -> Path: return self._root_path

    @property
    def src_path(self) -> Path: return self._src_path

    def set_scanner_thread(self):
        if self._scanner_thread is None:
            self._scanner_thread = threads.ScannerThread(self.src_path)

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

    def get_file_items_by_asset_item(self, asset_item: QStandardItem) -> List[QStandardItem]:
        for row in range(self.rowCount()):
            item = asset_item.child(row)
            if item:
                if item.hasChildren():
                    for row_child in range(item.rowCount()):
                        child_item = item.child(row_child)
                        yield child_item

    def get_files_path_by_asset_item(self, asset_item: QStandardItem) -> List[Path]:
        for each_item in self.get_file_items_by_asset_item(asset_item):
            yield Path(each_item.data(const.ItemData.FILEPATH))


class AmaterasuModel(AsukaModel):
    """Model which hold project mods information, files, and folders structure"""
    def __init__(self, dir_path: Union[PathLike, Path], metadata: dict):
        super().__init__(dir_path)
        self._root_path = dir_path.parent
        self._author = metadata.get('author')
        self._version = metadata.get('version')
        self._category = metadata.get('category')

    @property
    def author(self) -> str: return self._author

    @property
    def version(self) -> Tuple[int, int]: return self._version

    @property
    def category(self) -> str: return self._category


def create_game_data_model(dir_path: Union[PathLike, Path]) -> AsukaModel:
    if not core.is_dsdb_directory(dir_path):
        raise FileNotFoundError('Directory does not have *.name files')
    model = AsukaModel(dir_path)
    return model


def create_project_mod_model(dir_path: Union[PathLike, Path]) -> AmaterasuModel:
    if not core.is_project_mod_directory(dir_path):
        raise FileNotFoundError('Directory is not project mod directory')
    metadata = core.read_metadata_mod(dir_path / 'METADATA.json')
    model = AmaterasuModel(dir_path / 'modfiles', metadata)
    return model

