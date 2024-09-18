from os import PathLike
from pathlib import Path
from typing import Union

from PySide6.QtCore import QTimer
from PySide6.QtGui import QStandardItemModel, QStandardItem

from . import threads
from .. import core


class AsukaModel(QStandardItemModel):
    """Model which hold DSDB information, files, and folders structure"""
    def __init__(self, dir_path: Union[PathLike, Path]):
        super().__init__()
        self._root_path = Path(dir_path)

        self._queue = []

        self._scanner_thread = None
        self.set_scanner_thread()

        self._timer = QTimer()
        self._timer.setInterval(50)
        self._timer.timeout.connect(self.process_queue)
        self._timer.start()

    @property
    def root_path(self) -> Path: return self._root_path

    def set_scanner_thread(self):
        if self._scanner_thread is None:
            self._scanner_thread = threads.ScannerThread(self.root_path)

            self._scanner_thread.file_found.connect(self.add_to_queue)
            # self._scanner_thread.all_scan_finished.connect(self.bar)

            self._scanner_thread.start()

    def add_to_queue(self, asset_structure):
        self._queue.append(asset_structure)

    def process_queue(self):
        if self._queue:
            asset_structure = self._queue.pop(0)
            self.test_add(asset_structure)

    def test_add(self, asset_structure):
        for k, v in asset_structure.items():
            item = QStandardItem(k)

            for child_grp, child_list in v.items():
                item_grp = QStandardItem(child_grp)
                for child_item in child_list:
                    item_grp.appendRow(QStandardItem(child_item))
                item.appendRow(item_grp)

            self.appendRow(item)


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

