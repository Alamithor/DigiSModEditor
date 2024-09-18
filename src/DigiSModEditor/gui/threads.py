import os

from PySide6.QtCore import QThread, Signal

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
        for root, dirs, files in os.walk(self.dir_path):
            if files:
                files_text = ';'.join(files)
                name_list = [o for o in files if o.endswith('.name')]

                for name in name_list:
                    asset_files = core.get_asset_related_files(name, files_text)

                    self.file_found.emit(asset_files)


