from pathlib import Path

from PySide6.QtWidgets import QMainWindow

from . import widgets, models
from .. import utils as utl
from .. import constants as const


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        try:
            loader = widgets.UiLoader()
        except Exception as err:
            raise Exception(err)
        ui_file = utl.get_ui_file('main')
        self._ui = loader.load_ui(ui_file, self)

        the_path = Path(r'D:\IDrive\Project\2024\DigimonStory\original-content\DSDB')
        self._ui.the_path.setText(str(the_path))

        self._model = models.AsukaModel(the_path)
        self._ui.treeView.setModel(self._model)
