from PySide6.QtWidgets import QApplication

from . import gui

if __name__ == '__main__':
    app = QApplication([])

    window = gui.MainWindow()
    window.show()

    app.exec()
