from pathlib import Path
from typing import Union

from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QFileDialog, QComboBox, QLineEdit, QDoubleSpinBox,
    QSplitter, QPushButton, QToolButton, QTextEdit,
)

from . import widgets, models
from .. import utils as utl, core, constants
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

        # assign _ui attributes
        self._ui = loader.load_ui(main_ui_file, self)
        self._ui.left_panel_ui = loader.load_ui(left_panel_ui_file)
        self._ui.asset_tab_ui = loader.load_ui(asset_tab_ui_file)

        self._ui.left_panel_ui.mods_model = QStandardItemModel()

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

        # Rearrange splitter
        splitter: QSplitter = self.ui(UIP.SPLITTER)
        splitter.setSizes([1, self._ui.size().width() - 260])

        self.ui(UIP.MODS_DIR_TXT).setText(str(utl.get_default_project_dir()))
        self.ui(UIP.MODS_DIR_BTN).clicked.connect(self.browse_directory)
        self.ui(UIP.MODS_DROPDOWN).setModel(self.ui(UIP.MODS_MDL))
        self.populate_mods_list()
        self.mods_info_update()
        self.ui(UIP.MODS_CREATE_BTN).clicked.connect(self.create_project_mods)

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

    def populate_mods_list(self):
        root_mods_dir = Path(self.ui(UIP.MODS_DIR_TXT).text())
        the_model: QStandardItemModel = self.ui(UIP.MODS_MDL)
        the_model.clear()

        empty_item = QStandardItem('-- New --')
        empty_item.setData('', constants.ItemData.FILEPATH)
        the_model.appendRow(empty_item)

        for each_dir in root_mods_dir.iterdir():
            if each_dir.is_dir():
                if core.is_project_mods_directory(each_dir):
                    item = QStandardItem(each_dir.name)
                    item.setData(each_dir, constants.ItemData.FILEPATH)

                    the_model.appendRow(item)

    def mods_info_update(self):
        mods_dd: QComboBox = self.ui(UIP.MODS_DROPDOWN)
        edit_btn: QToolButton = self.ui(UIP.MODS_EDIT_BTN)
        create_btn: QPushButton = self.ui(UIP.MODS_CREATE_BTN)
        meta_ui_list = [
            UIP.MODS_TITLE_TXT,
            UIP.MODS_AUTHOR_TXT,
            UIP.MODS_CAT_TXT,
            UIP.MODS_VER_SPN,
            UIP.MODS_DESC_TXT
        ]

        mods_dir_path = mods_dd.currentData(constants.ItemData.FILEPATH)
        if mods_dir_path == '':
            # Create MODE
            read_only = False
            create_btn.setVisible(True)
            edit_btn.setVisible(False)
        else:
            # Edit Mode
            read_only = True
            create_btn.setVisible(False)
            edit_btn.setVisible(True)

        for ui_path in meta_ui_list:
            wgt: Union[QLineEdit, QDoubleSpinBox] = self.ui(ui_path)
            wgt.setReadOnly(read_only)

    def create_project_mods(self):
        title: QLineEdit = self.ui(UIP.MODS_TITLE_TXT)
        author: QLineEdit = self.ui(UIP.MODS_AUTHOR_TXT)
        category: QLineEdit = self.ui(UIP.MODS_CAT_TXT)
        description: QTextEdit = self.ui(UIP.MODS_DESC_TXT)
        version: QDoubleSpinBox = self.ui(UIP.MODS_VER_SPN)
        dir_path: QLineEdit = self.ui(UIP.MODS_DIR_TXT)

        # Check title, author, and version
        if title.text() == '' or author.text() == '':
            raise Exception('Title or Author field shouldn\'t empty!')
        if version.value() < 0.1:
            raise Exception('Version should be higher than 0.0')

        core.create_project_mods(
            dir_path = Path(dir_path.text()),
            project_name = title.text(),
            author = author.text(),
            version = utl.float_to_tuple(version.value()),
            category = category.text(),
            description = description.toPlainText()
        )

# TODO: rearrange tab order between version and category
# TODO: dropdown list signal slot to update
# TODO: more logs in core, and gui

