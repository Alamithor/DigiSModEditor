from os import PathLike
from pathlib import Path
from typing import Union

from PySide6.QtGui import QStandardItemModel, QStandardItem

from . import threads


class AsukaModel(QStandardItemModel):
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

    def test_add(self, item_name, children):
        item = QStandardItem(item_name)
        for child_grp, child_list in children.items():
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
