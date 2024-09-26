from pathlib import Path

from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QFileDialog

from . import widgets, models
from .. import utils as utl
from ..constants import UiPath as UIP


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        try:
            loader = widgets.UiLoader()
        except Exception as err:
            raise Exception(err)
        main_ui_file = utl.get_ui_file('main_window')
        left_panel_ui_file = utl.get_ui_file('project_mods_widget')
        asset_tab_ui_file = utl.get_ui_file('game_asset_widget')

        self._ui = loader.load_ui(main_ui_file, self)
        self._ui.left_panel_ui = loader.load_ui(left_panel_ui_file)
        self._ui.asset_tab_ui = loader.load_ui(asset_tab_ui_file)

        # Create Tab
        # create_tab_ui_file = utl.get_ui_file('setup_widget')
        # create_tab_widget = loader.load_ui(create_tab_ui_file)
        # create_lay = QVBoxLayout(self._ui.setup_tab)
        # create_lay.setContentsMargins(0, 0, 0, 0)
        # create_lay.addWidget(create_tab_widget)

        # Left panel
        left_lay = QVBoxLayout(self._ui.left_panel)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.addWidget(self._ui.left_panel_ui)

        # Asset Tab
        asset_lay = QVBoxLayout(self._ui.asset_tab)
        asset_lay.setContentsMargins(0, 0, 0, 0)
        asset_lay.addWidget(self._ui.asset_tab_ui)

        self.ui(UIP.MODS_DIR_TXT).setText(str(utl.get_default_project_dir()))
        self.ui(UIP.MODS_DIR_BTN).clicked.connect(self.browse_directory)

    def ui(self, ui_name: str = ''):
        if ui_name == '':
            return self._ui

        attrs = ui_name.split('.')
        ui_widget = self._ui
        for attr in attrs:
            ui_widget = getattr(ui_widget, attr, None)
            if ui_widget is None:
                raise Exception(f"Cannot find widget {ui_name}")

        return ui_widget

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self._ui.left_panel_ui.mods_dir_text.setText(f"{directory}")
