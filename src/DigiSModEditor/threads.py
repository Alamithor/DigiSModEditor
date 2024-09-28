import os
import logging

from PySide6.QtCore import QThread, Signal

from . import core
from . import constants as const

logger = logging.getLogger(const.LogName.THREAD)


class ScannerThread(QThread):
    all_scan_finished = Signal()
    asset_file_found = Signal(dict)
    data_file_found = Signal(dict)

    def __init__(self, dir_path):
        super().__init__()
        self._dir_path = dir_path

    @property
    def dir_path(self): return self._dir_path

    def run(self):
        for root, dirs, files in os.walk(self.dir_path):
            if files:
                files_text = ''
                name_list = [o for o in files if o.endswith('.name')]
                if name_list:
                    files_text = ';'.join(files)

                for name in name_list:
                    asset_files = core.get_asset_related_files(name, files_text)
                    if asset_files:
                        ast_file_path = os.path.join(root, name)
                        logger.info(f'Found asset file: {ast_file_path}')

                        self.asset_file_found.emit(asset_files)

        self.all_scan_finished.emit()


