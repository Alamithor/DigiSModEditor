from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QVBoxLayout

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
        main_ui_file = utl.get_ui_file('main_window')
        self._ui = loader.load_ui(main_ui_file, self)

        # Create Tab
        # create_tab_ui_file = utl.get_ui_file('setup_widget')
        # create_tab_widget = loader.load_ui(create_tab_ui_file)
        # create_lay = QVBoxLayout(self._ui.setup_tab)
        # create_lay.setContentsMargins(0, 0, 0, 0)
        # create_lay.addWidget(create_tab_widget)

        # Left panel
        left_panel_ui_file = utl.get_ui_file('project_mods_widget')
        left_panel_widget = loader.load_ui(left_panel_ui_file)
        left_lay = QVBoxLayout(self._ui.left_panel)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.addWidget(left_panel_widget)

        # Asset Tab
        asset_tab_ui_file = utl.get_ui_file('game_asset_widget')
        asset_tab_widget = loader.load_ui(asset_tab_ui_file)
        asset_lay = QVBoxLayout(self._ui.asset_tab)
        asset_lay.setContentsMargins(0, 0, 0, 0)
        asset_lay.addWidget(asset_tab_widget)

        # the_path = Path(r'D:\IDrive\Project\2024\DigimonStory\original-content\DSDB')
        # self._ui.the_path.setText(str(the_path))
        #
        # self._model = models.AsukaModel(the_path)
        # self._ui.treeView.setModel(self._model)
