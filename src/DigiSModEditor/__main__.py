import logging

from PySide6.QtWidgets import QApplication

from . import log_manager # To kick start logging
from . import gui
from . import constants as const

if __name__ == '__main__':
    logger = logging.getLogger(const.LogName.MAIN)
    logger.info('DigiSModEditor application started...')

    app = QApplication([])

    window = gui.MainWindow()
    window.show()

    app.exec()
