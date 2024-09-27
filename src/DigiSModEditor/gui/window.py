import logging
from os import PathLike
from pathlib import Path
from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QFileDialog, QComboBox, QLineEdit, QDoubleSpinBox,
    QSplitter, QPushButton, QToolButton, QTextEdit,
)

from . import widgets, models
from .. import utils as utl, core, constants as const, errors as err
from ..constants import UiPath as UIP

log = logging.getLogger(const.LogName.MAIN)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        try:
            loader = widgets.UiLoader()
        except Exception as e:
            raise Exception(e)
        main_ui_file = utl.get_ui_file('main_window')
        left_panel_ui_file = utl.get_ui_file('project_mods_widget')
        asset_tab_ui_file = utl.get_ui_file('game_asset_widget')

        # assign _ui attributes
        self._ui = loader.load_ui(main_ui_file, self)
        self._ui.left_panel_ui = loader.load_ui(left_panel_ui_file)
        self._ui.asset_tab_ui = loader.load_ui(asset_tab_ui_file)
        self._mods_model_data = {}

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
        self.ui(UIP.MODS_DROPDOWN).currentIndexChanged.connect(self.mods_dropdown_index_changed)
        self.ui(UIP.MODS_CREATE_BTN).clicked.connect(self.create_project_mods)
        # self.mods_info_update()
        self.populate_mods_list()

    def ui(self, ui_name: str = ''):
        if ui_name == '':
            return self._ui

        attrs = ui_name.split('.')
        ui_widget = self._ui
        for attr in attrs:
            ui_widget = getattr(ui_widget, attr, None)
            if ui_widget is None:
                raise err.WidgetNotFoundError(f"Cannot find widget {ui_name}")

        return ui_widget

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        log.info(f"Selected directory: {directory}")
        if directory:
            self._ui.left_panel_ui.mods_dir_text.setText(f"{directory}")

    def _add_mods_model(self, title: str, model: models.AmaterasuModel):
        self._mods_model_data[title] = model

    def _remove_mods_model(self, title: str):
        del self._mods_model_data[title]

    def _get_mods_model(self, title: str) -> Union[models.AmaterasuModel, None]:
        return self._mods_model_data.get(title, None)

    def _add_new_mods(self, title: str, dir_path: Union[PathLike, Path]) -> int:
        mods_dd: QComboBox = self.ui(UIP.MODS_DROPDOWN)
        index = mods_dd.count() + 1
        try:
            new_project_mods = models.create_project_mods_model(dir_path)
        except err.InvalidProjectModsDirectory as e:
            log.error(e)
            return -1

        mods_dd.insertItem(index, title)
        self._add_mods_model(title, new_project_mods)

        return index

    def populate_mods_list(self):
        root_mods_dir = Path(self.ui(UIP.MODS_DIR_TXT).text())
        mods_dd: QComboBox = self.ui(UIP.MODS_DROPDOWN)
        log.info(f'Populating mods list: {root_mods_dir}')
        mods_dd.clear()

        log.info(f'Adding default: -- New --')
        mods_dd.addItem('-- New --')
        for each_dir in root_mods_dir.iterdir():
            if each_dir.is_dir():
                log.info(f'Adding: {each_dir.name}')
                self._add_new_mods(each_dir.name, each_dir)

    def mods_dropdown_index_changed(self, index: int):
        mods_dd: QComboBox = self.ui(UIP.MODS_DROPDOWN)
        edit_btn: QToolButton = self.ui(UIP.MODS_EDIT_BTN)
        create_btn: QPushButton = self.ui(UIP.MODS_CREATE_BTN)
        meta_ui_data = {
            UIP.MODS_TITLE_TXT: '',
            UIP.MODS_AUTHOR_TXT: '',
            UIP.MODS_CAT_TXT: '',
            UIP.MODS_VER_SPN: 0.0,
            UIP.MODS_DESC_TXT: ''
        }

        mods_title = mods_dd.itemText(index)
        proj_mods_model = self._get_mods_model(mods_title)
        if proj_mods_model is None:
            # Create MODE
            read_only = False
            create_btn.setVisible(True)
            edit_btn.setVisible(False)
        else:
            # Edit Mode
            read_only = True
            create_btn.setVisible(False)
            edit_btn.setVisible(True)

            meta_ui_data[UIP.MODS_TITLE_TXT] = proj_mods_model.title
            meta_ui_data[UIP.MODS_AUTHOR_TXT] = proj_mods_model.author
            meta_ui_data[UIP.MODS_CAT_TXT] = proj_mods_model.category
            meta_ui_data[UIP.MODS_VER_SPN] = utl.tuple_to_float(proj_mods_model.version)
            meta_ui_data[UIP.MODS_DESC_TXT] = proj_mods_model.description

        for ui_path, val in meta_ui_data.items():
            wgt: Union[QLineEdit, QDoubleSpinBox, QTextEdit] = self.ui(ui_path)
            wgt.setReadOnly(read_only)

            if isinstance(wgt, QLineEdit) or isinstance(wgt, QTextEdit):
                wgt.setText(val)
            elif isinstance(wgt, QDoubleSpinBox):
                wgt.setValue(val)

    def create_project_mods(self):
        title: QLineEdit = self.ui(UIP.MODS_TITLE_TXT)
        author: QLineEdit = self.ui(UIP.MODS_AUTHOR_TXT)
        category: QLineEdit = self.ui(UIP.MODS_CAT_TXT)
        description: QTextEdit = self.ui(UIP.MODS_DESC_TXT)
        version: QDoubleSpinBox = self.ui(UIP.MODS_VER_SPN)
        dir_path: QLineEdit = self.ui(UIP.MODS_DIR_TXT)

        mods_title = title.text()
        root_dir_path = Path(dir_path.text())
        mods_dir_path = root_dir_path / mods_title

        log.info('Checking title, author, and version fields')
        if title.text() == '' or author.text() == '':
            raise err.CreateProjectModsError('Title or Author field shouldn\'t empty!')
        if version.value() < 0.1:
            raise err.CreateProjectModsError('Version should be higher than 0.0')
        if mods_dir_path.exists():
            raise err.CreateProjectModsError(f'Mods folder already exists: {mods_dir_path}')

        log.info(f'Creating new mods: {title.text()}')
        core.create_project_mods(
            dir_path = root_dir_path,
            project_name = title.text(),
            author = author.text(),
            version = utl.float_to_tuple(version.value()),
            category = category.text(),
            description = description.toPlainText()
        )

        if mods_dir_path.exists():
            mods_dd: QComboBox = self.ui(UIP.MODS_DROPDOWN)
            index = self._add_new_mods(title.text(), mods_dir_path)

            if index > 0:
                log.info(f'Added new mods: {title.text()}')
                mods_dd.setCurrentIndex(index - 1)

# TODO: dropdown list signal slot to update
# TODO: more logs in core, and gui

