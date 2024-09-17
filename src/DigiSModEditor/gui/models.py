from os import PathLike
from pathlib import Path
from typing import Union

from PySide6.QtGui import QStandardItemModel, QStandardItem

from . import threads
from .. import core


class AsukaModel(QStandardItemModel):
    """Model which hold DSDB information, files, and folders structure"""
    def __init__(self, dir_path: Union[PathLike, Path]):
        super().__init__()
        self._root_path = Path(dir_path)

        self._scanner_thread = None
        self.set_scanner_thread()

    @property
    def root_path(self) -> Path: return self._root_path

    def set_scanner_thread(self):
        if self._scanner_thread is None:
            self._scanner_thread = threads.ScannerThread(self.root_path)

            self._scanner_thread.file_found.connect(self.test_add)
            # self._scanner_thread.all_scan_finished.connect(self.bar)

            self._scanner_thread.start()

    def test_add(self, asset_structure):
        for k, v in asset_structure.items():
            item = QStandardItem(k)

            for child_grp, child_list in v.items():
                item_grp = QStandardItem(child_grp)
                for child_item in child_list:
                    item_grp.appendRow(QStandardItem(child_item))
                item.appendRow(item_grp)

            self.appendRow(item)

    def add_item(self, item_name: str, item_data: Union[dict], parent: QStandardItem = None):
        pass

    def find_item(self, item_path: str) -> QStandardItem:
        pass

    def update_model(self, item_name: str, item_data: Union[dict], parent: str):
        # we need to
        pass


class AmaterasuModel(AsukaModel):
    """Model which hold project mods information, files, and folders structure"""
    def __init__(self, dir_path: Union[PathLike, Path]):
        super().__init__(dir_path)


def create_game_data_model(dir_path: Union[PathLike, Path]) -> AsukaModel:
    if not core.is_dsdb_directory(dir_path):
        raise Exception('Directory does not have *.name files')
    model = AsukaModel(dir_path)
    return model


def create_project_mod_model(dir_path: Union[PathLike, Path]) -> AmaterasuModel:
    if not core.is_project_mod_directory(dir_path):
        raise Exception('Directory is not project mod directory')
    metadata = core.read_metadata_mod(dir_path / 'METADATA.json')
    model = AmaterasuModel(dir_path / 'modfiles')
    return model

