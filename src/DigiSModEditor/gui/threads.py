from PySide6.QtCore import Qt, QThread, Signal

from .. import core


class ScannerThread(QThread):
    all_scan_finished = Signal()
    file_found = Signal(dict)

    def __init__(self, dir_path):
        super().__init__()
        self._dir_path = dir_path

    @property
    def dir_path(self): return self._dir_path

    def run(self):
        for asset_structure in core.traverse_asset_files(self.dir_path):
            self.file_found.emit(asset_structure)

