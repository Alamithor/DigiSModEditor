import logging
import os
import time
from os import PathLike
from pathlib import Path
from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import (
    QMainWindow, QVBoxLayout, QFileDialog, QComboBox, QLineEdit, QDoubleSpinBox,
    QSplitter, QPushButton, QToolButton, QTextEdit, QTreeView, QSpinBox,
)

from . import widgets, models
from .. import utils as utl, core, constants as const, errors as err, threads as th
from ..constants import UiPath as UIP

log = logging.getLogger(const.LogName.MAIN)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DigiS Mod Editor')

        try:
            loader = widgets.UiLoader()
        except Exception as e:
            raise Exception(e)
        main_ui_file = utl.get_ui_file('main_window')
        left_panel_ui_file = utl.get_ui_file('project_mods_widget')
        setup_tab_ui_file = utl.get_ui_file('setup_widget')
        transfer_tab_ui_file = utl.get_ui_file('asset_transfer_widget')
        pack_tab_ui_file = utl.get_ui_file('pack_mods_widget')

        log.debug(f'Ui file: {main_ui_file}, exists: {main_ui_file.exists()}')
        log.debug(f'Ui file: {left_panel_ui_file}, exists: {left_panel_ui_file.exists()}')
        log.debug(f'Ui file: {setup_tab_ui_file}, exists: {setup_tab_ui_file.exists()}')
        log.debug(f'Ui file: {transfer_tab_ui_file}, exists: {transfer_tab_ui_file.exists()}')
        log.debug(f'Ui file: {pack_tab_ui_file}, exists: {pack_tab_ui_file.exists()}')

        # assign _ui attributes
        self._ui = loader.load_ui(main_ui_file, self)
        self._ui.left_panel_ui = loader.load_ui(left_panel_ui_file)
        self._ui.setup_tab_ui = loader.load_ui(setup_tab_ui_file)
        self._ui.transfer_tab_ui = loader.load_ui(transfer_tab_ui_file)
        self._ui.pack_tab_ui = loader.load_ui(pack_tab_ui_file)
        self._mods_model_data = {}
        self._asset_src_model_data = {}

        # Left panel
        left_lay = QVBoxLayout(self._ui.left_panel)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.addWidget(self._ui.left_panel_ui)

        # Setup Tab
        create_lay = QVBoxLayout(self._ui.setup_tab)
        create_lay.setContentsMargins(0, 0, 0, 0)
        create_lay.addWidget(self._ui.setup_tab_ui)

        # Transfer Tab
        transfer_lay = QVBoxLayout(self._ui.transfer_tab)
        transfer_lay.setContentsMargins(0, 0, 0, 0)
        transfer_lay.addWidget(self._ui.transfer_tab_ui)

        # Pack Tab
        pack_lay = QVBoxLayout(self._ui.pack_tab)
        pack_lay.setContentsMargins(0, 0, 0, 0)
        pack_lay.addWidget(self._ui.pack_tab_ui)

        # Rearrange splitter
        panel_split: QSplitter = self.ui(UIP.PANEL_SPLIT)
        panel_split.setSizes([1, self._ui.size().width() - 260])
        transfer_split: QSplitter = self.ui(UIP.TRANS_SPLIT)
        transfer_split.setSizes([1, self._ui.transfer_tab_ui.size().width() - 540])

        # connect left panel signals
        self.ui(UIP.PROJECT_DIR_TXT).textChanged.connect(self.populate_mods_list)
        self.ui(UIP.MODS_DROPDOWN).currentIndexChanged.connect(self.mods_dropdown_index_changed)
        self.ui(UIP.PROJECT_DIR_BTN).clicked.connect(self.browse_project_directory)
        self.ui(UIP.MODS_CREATE_BTN).clicked.connect(self.create_project_mods)
        self.ui(UIP.MODS_EDIT_BTN).toggled.connect(self.edit_project_mods)
        self.ui(UIP.PROJECT_DIR_TXT).setText(str(utl.get_default_project_mods_dir()))
        # connect setup tab signals
        self.ui(UIP.DSDB_DIR_TXT).textChanged.connect(self.populate_source_asset)
        self.ui(UIP.DSDB_DIR_BTN).clicked.connect(self.browse_dsdb_directory)
        self.ui(UIP.SETUP_PACK_DIR_BTN).clicked.connect(self.browse_packed_directory)
        self.ui(UIP.SETUP_PACK_DIR_TXT).setText(str(utl.get_default_packed_mods_dir()))
        # connect transfer tab signals
        self.ui(UIP.TRANS_COPY_BTN).clicked.connect(self.copy_src_asset_to_mods)
        # connect pack tab signals
        self.ui(UIP.PACKING_BTN).clicked.connect(self.packing_mods)
        self.ui(UIP.PACK_OPEN_DIR_BTN).clicked.connect(self.open_pack_mods_dir)

        # populate left panel
        self.populate_mods_list()

        # Dev
        # self.ui(UIP.DSDB_DIR_TXT).setText(r'D:\IDrive\Project\2024\DigimonStory\original-content\DSDB')

        # start thread
        for mods_name, data in self._mods_model_data.items():
            mods_thread = data.get('thread')
            self.scan_project_contents(mods_thread)

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

    def browse_project_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        log.info(f"Selected directory: {directory}")
        if directory:
            self.ui(UIP.PROJECT_DIR_TXT).setText(f"{directory}")

    def browse_dsdb_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select DSDB Directory")
        log.info(f"Selected directory: {directory}")
        if directory:
            if not core.is_dsdb_directory(Path(directory)):
                raise err.InvalidDSDBDirectory(f'Invalid DSDB directory: {directory}')
            self.ui(UIP.DSDB_DIR_TXT).setText(f"{directory}")

    def browse_packed_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Packed Directory")
        log.info(f"Selected directory: {directory}")
        if directory:
            self.ui(UIP.SETUP_PACK_DIR_TXT).setText(f"{directory}")

    def src_asset_selection_counter(self, top_left, bottom_right, roles):
        if Qt.CheckStateRole in roles:
            asset_src_data = self._asset_src_model_data.get('DSDB', {})
            asset_src_model: Union[models.AsukaModel, None] = asset_src_data.get('asset_model', None)
            if asset_src_model is None:
                return
            counter_ui: QSpinBox = self.ui(UIP.TRANS_SELECT_COUNTER)
            asset_src_tv: QTreeView = self.ui(UIP.SRC_ASSET_TV)

            # Change check state on selection
            selected_indexes = asset_src_tv.selectedIndexes()
            item_state = asset_src_model.itemFromIndex(top_left).checkState()
            for index in selected_indexes:
                selected_item: QStandardItem = asset_src_model.itemFromIndex(index)
                if selected_item.isCheckable():
                    selected_item.setCheckState(item_state)

            # Update checked counter
            temp_index_list = []
            for i in range(asset_src_model.invisibleRootItem().rowCount()):
                child = asset_src_model.invisibleRootItem().child(i)
                if child.checkState() == Qt.Checked:
                    temp_index_list.append(i)

            asset_src_data['checked_index_list'] = temp_index_list
            counter = len(temp_index_list)
            counter_ui.setValue(counter)
            log.info(f'Asset checked counter: {counter}')

    @staticmethod
    def scan_project_contents(scanner: th.ScannerThread):
        rescan_delay = time.time() - scanner.last_scan_time < 120 # 2 Minute
        if rescan_delay or scanner.last_scan_time == 0:
            if scanner.isRunning():
                scanner.stop()
            scanner.start()

    def _add_mods_model(self, title: str, asset_model: models.AmaterasuModel):
        new_scanner = th.ScannerThread(asset_model.src_path)
        new_data = {
            'asset_model': asset_model,
            'thread': new_scanner,
            'checked_index_list': []
        }
        new_scanner.asset_file_found.connect(asset_model.add_to_queue)

        self._mods_model_data[title] = new_data

    def _remove_mods_model(self, title: str):
        del self._mods_model_data[title]

    def _get_mods_model(self, title: str) -> Union[models.AmaterasuModel, None]:
        return self._mods_model_data.get(title, {}).get('asset_model', None)

    def _add_new_mods(self, title: str, dir_path: Union[PathLike, Path]) -> int:
        mods_dd: QComboBox = self.ui(UIP.MODS_DROPDOWN)
        index = mods_dd.count() + 1
        try:
            new_project_mods = models.create_project_mods_model(dir_path)
        except err.InvalidModsDirectory as e:
            log.error(e)
            return -1

        mods_dd.insertItem(index, title)
        self._add_mods_model(title, new_project_mods)

        return index

    def populate_mods_list(self):
        project_mods_dir = Path(self.ui(UIP.PROJECT_DIR_TXT).text())
        if not project_mods_dir.is_dir():
            raise err.InvalidDirectoryPath(f'Invalid directory path: {project_mods_dir}')

        mods_dd: QComboBox = self.ui(UIP.MODS_DROPDOWN)
        log.info(f'Populating mods list: {project_mods_dir}')
        mods_dd.clear()

        log.info(f'Adding default: -- New --')
        mods_dd.addItem('-- New --')
        for each_dir in project_mods_dir.iterdir():
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
        asset_tv: QTreeView = self.ui(UIP.MODS_ASSET_TV)

        mods_title = mods_dd.itemText(index)
        proj_mods_model = self._get_mods_model(mods_title)
        if proj_mods_model is None:
            log.info('Cannot find mods information, entering create mode')
            # Create MODE
            read_only = False
            create_btn.setVisible(True)
            edit_btn.setVisible(False)
        else:
            log.info('Mods information found, entering edit mode')
            # Edit Mode
            read_only = True
            create_btn.setVisible(False)
            edit_btn.setVisible(True)

            meta_ui_data[UIP.MODS_TITLE_TXT] = proj_mods_model.title
            meta_ui_data[UIP.MODS_AUTHOR_TXT] = proj_mods_model.author
            meta_ui_data[UIP.MODS_CAT_TXT] = proj_mods_model.category
            meta_ui_data[UIP.MODS_VER_SPN] = utl.tuple_to_float(proj_mods_model.version)
            meta_ui_data[UIP.MODS_DESC_TXT] = proj_mods_model.description

        log.info(f'Setting mods info ui data: {meta_ui_data}')
        for ui_path, val in meta_ui_data.items():
            wgt: Union[QLineEdit, QDoubleSpinBox, QTextEdit] = self.ui(ui_path)
            wgt.setReadOnly(read_only)

            if isinstance(wgt, QLineEdit) or isinstance(wgt, QTextEdit):
                wgt.setText(val)
            elif isinstance(wgt, QDoubleSpinBox):
                wgt.setValue(val)

        log.info(f'Set mods asset model: {proj_mods_model}')
        asset_tv.setModel(proj_mods_model)

    def create_project_mods(self):
        title: QLineEdit = self.ui(UIP.MODS_TITLE_TXT)
        author: QLineEdit = self.ui(UIP.MODS_AUTHOR_TXT)
        category: QLineEdit = self.ui(UIP.MODS_CAT_TXT)
        description: QTextEdit = self.ui(UIP.MODS_DESC_TXT)
        version: QDoubleSpinBox = self.ui(UIP.MODS_VER_SPN)
        dir_path: QLineEdit = self.ui(UIP.PROJECT_DIR_TXT)

        mods_title = title.text()
        root_dir_path = Path(dir_path.text())
        mods_dir_path = root_dir_path / mods_title

        log.info('Checking title, author, version fields and project, mods directory')
        if not root_dir_path.exists():
            raise err.CreateProjectModsError(f'Project directory doesn\'t exists: {root_dir_path}')
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

    def edit_project_mods(self, checked: bool):
        edit_btn: QToolButton = self.ui(UIP.MODS_EDIT_BTN)
        mods_dd: QComboBox = self.ui(UIP.MODS_DROPDOWN)
        # title_txt: QLineEdit = self.ui(UIP.MODS_TITLE_TXT)
        author_txt: QLineEdit = self.ui(UIP.MODS_AUTHOR_TXT)
        category_txt: QLineEdit = self.ui(UIP.MODS_CAT_TXT)
        version_spn: QDoubleSpinBox = self.ui(UIP.MODS_VER_SPN)
        description_txt: QTextEdit = self.ui(UIP.MODS_DESC_TXT)
        meta_ui_data = [
            # title_txt,
            author_txt,
            category_txt,
            version_spn,
            description_txt
        ]

        mods_title = mods_dd.currentText()
        proj_mods_model = self._get_mods_model(mods_title)
        if proj_mods_model is None:
            raise err.EditProjectModsInfoError(f'Cannot find mods information: {mods_title}')

        if checked:
            log.info('Editing mods metadata and description')
            edit_btn.setText('Save Changes')
            read_only = False
        else:
            log.info('Saving mods metadata and description')
            read_only = True
            try:
                # proj_mods_model.set_title(title_txt.text())
                proj_mods_model.set_author(author_txt.text())
                proj_mods_model.set_category(category_txt.text())
                proj_mods_model.set_version(utl.float_to_tuple(version_spn.value()))
                proj_mods_model.set_description(description_txt.toPlainText())
                proj_mods_model.save_information()
            except err.EditProjectModsInfoError as e:
                log.error(e)
                return -1

            edit_btn.setText('Edit Mods Info')

        for wgt in meta_ui_data:
            wgt.setReadOnly(read_only)

    def populate_source_asset(self):
        dsdb_txt: QLineEdit = self.ui(UIP.DSDB_DIR_TXT)
        dsdb_dir: Path = Path(dsdb_txt.text())
        if not dsdb_dir.is_dir():
            raise err.InvalidDirectoryPath(f'Invalid directory path: {dsdb_dir}')

        dsdb_model = models.create_dsdb_model(dsdb_dir)
        new_scanner = th.ScannerThread(dsdb_model.src_path)
        new_data = {
            'asset_model': dsdb_model,
            'thread': new_scanner,
            'checked_index_list': [],
        }
        new_scanner.asset_file_found.connect(dsdb_model.add_to_queue)
        self.scan_project_contents(new_scanner)

        self.ui(UIP.SRC_ASSET_TV).setModel(dsdb_model)
        dsdb_model.dataChanged.connect(self.src_asset_selection_counter)

        self._asset_src_model_data['DSDB'] = new_data

    def copy_src_asset_to_mods(self):
        src_data = self._asset_src_model_data.get('DSDB', {})
        src_model: Union[models.AsukaModel, None] = src_data.get('asset_model', None)
        if src_model is None:
            raise err.CopyAssetError('Cannot find source asset information')

        mods_dd: QComboBox = self.ui(UIP.MODS_DROPDOWN)
        mods_title = mods_dd.currentText()
        tgt_data = self._mods_model_data.get(mods_title, {})
        tgt_model: Union[models.AmaterasuModel, None] = tgt_data.get('asset_model', None)
        if tgt_model is None:
            raise err.CopyAssetError(f'Cannot find mods information: {mods_title}')

        selection_checked_list = src_data.get('checked_index_list', [])
        for i in selection_checked_list:
            src_item: QStandardItem = src_model.invisibleRootItem().child(i)
            # for file_name in src_model.get_files_name_by_asset_item(src_item):
            #     copy_result = core.copy_asset_file(src_model.src_path, tgt_model.src_path, file_name)
            #     log.info(copy_result.message)

            for file_path in src_model.get_files_path_by_asset_item(src_item):
                src_dir = file_path.parent
                file_name = file_path.name
                tgt_dir = tgt_model.src_path / src_dir.relative_to(src_model.src_path)
                copy_result = core.copy_asset_file(src_dir, tgt_dir, file_name)
                log.info(copy_result.message)

            src_structure = src_model.get_asset_structure_by_asset_item(src_item)
            tgt_model.add_asset_item(src_structure)

            src_item.setCheckState(Qt.Unchecked)

    def packing_mods(self):
        mods_dd: QComboBox = self.ui(UIP.MODS_DROPDOWN)
        mods_title = mods_dd.currentText()
        tgt_data = self._mods_model_data.get(mods_title, {})
        tgt_model: Union[models.AmaterasuModel, None] = tgt_data.get('asset_model', None)
        if tgt_model is None:
            raise err.CopyAssetError(f'Cannot find mods information: {mods_title}')

        pack_dir_ui: QLineEdit = self.ui(UIP.SETUP_PACK_DIR_TXT)
        pack_dir_path = Path(pack_dir_ui.text())
        if not pack_dir_path.is_dir():
            raise err.InvalidDirectoryPath(f'Invalid directory path: {pack_dir_path}')

        core.pack_project_mods(tgt_model.root_path, pack_dir_path, f'{mods_title}.zip')

    def open_pack_mods_dir(self):
        pack_dir_ui: QLineEdit = self.ui(UIP.SETUP_PACK_DIR_TXT)
        pack_dir_path = Path(pack_dir_ui.text())
        if not pack_dir_path.is_dir():
            raise err.InvalidDirectoryPath(f'Invalid directory path: {pack_dir_path}')

        log.info(f'Opening directory: {pack_dir_path}')
        os.startfile(pack_dir_path)


# TODO: more logs in core, and gui
# TODO: duplicate code need to be addressed
# TODO: doesn't support mods title change
# TODO: user pop up dialog error or warning
# FIXME: when you browse directory, you need to compare old path and new path.
#  then flush model datas, before that stop all scanner first.

