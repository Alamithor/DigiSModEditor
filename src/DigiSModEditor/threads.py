import os
import logging
import time

from PySide6.QtCore import QThread, Signal

from . import core
from . import constants as const

log = logging.getLogger(const.LogName.THREAD)


class ScannerThread(QThread):
    scan_finished = Signal()
    asset_file_found = Signal(dict)
    data_file_found = Signal(dict)

    def __init__(self, dir_path):
        super().__init__()
        self._dir_path = dir_path
        self._last_scan_time = 0
        self._stop = False

    @property
    def dir_path(self): return self._dir_path

    @property
    def last_scan_time(self) -> float: return self._last_scan_time

    def stop(self):
        self._stop = True

    def run(self):
        self._last_scan_time = time.time()

        log.info(f'Start scanning: {self.dir_path}')
        for root, dirs, files in os.walk(self.dir_path):
            if self._stop:
                log.info('Stop scanning')
                break

            if files:
                files_text = ''
                name_list = [o for o in files if o.endswith('.name')]
                if name_list:
                    files_text = ';'.join(files)

                for name in name_list:
                    if self._stop:
                        log.info('Stop scanning')
                        break

                    asset_files = core.get_asset_related_files(name, files_text)
                    if asset_files:
                        ast_file_path = os.path.join(root, name)
                        log.info(f'Found asset file: {ast_file_path}')

                        self.asset_file_found.emit(asset_files)

        if not self._stop:
            self.scan_finished.emit()


