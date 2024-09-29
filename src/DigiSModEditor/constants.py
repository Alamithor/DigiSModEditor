from enum import IntEnum, StrEnum


class Pattern(StrEnum):
    # GEO = r'\.(geom)'
    # SKEL = r'\.(skel)'
    ANIM = r'(\_\w{2}\d{2}|)\.(anim)'


class ItemData(IntEnum):
    NAME = 100
    EXT = 101
    FILENAME = 102
    FILEPATH = 103


class LogName(StrEnum):
    MAIN = 'DigiSModEditor'
    THREAD = 'DigiSModEditor.threads'


class UiPath(StrEnum):
    MAIN = ''

    # Main
    PANEL_SPLIT = 'panel_splitter'

    # Left panel
    L_PANEL = 'left_panel_ui'
    # Root project dir
    PROJECT_DIR_TXT = f'{L_PANEL}.project_dir_text'
    PROJECT_DIR_BTN = f'{L_PANEL}.project_dir_btn'
    # Mods dir path
    MODS_DROPDOWN = f'{L_PANEL}.mods_dropdown'
    # Mods group
    MODS_META_GRP = f'{L_PANEL}.metadata_grpbox'
    MODS_DESC_GRP = f'{L_PANEL}.desc_grpbox'
    MODS_SAVE_GRP = f'{L_PANEL}.save_grpbox'
    # Mods metadata
    MODS_TITLE_TXT = f'{L_PANEL}.mods_title_text'
    MODS_AUTHOR_TXT = f'{L_PANEL}.mods_author_text'
    MODS_CAT_TXT = f'{L_PANEL}.mods_category_text'
    MODS_VER_SPN = f'{L_PANEL}.mods_version_dspin'
    MODS_DESC_TXT = f'{L_PANEL}.mods_description_text'
    MODS_EDIT_BTN = f'{L_PANEL}.mods_edit_btn'
    MODS_CREATE_BTN = f'{L_PANEL}.mods_create_btn'
    # Mods assets
    MODS_ASSET_TV = f'{L_PANEL}.mods_asset_tv'

    # Main tab
    # Setup tab
    SETUP_TAB = 'setup_tab_ui'
    DSDB_DIR_TXT = f'{SETUP_TAB}.dsdb_dir_text'
    DSDB_DIR_BTN = f'{SETUP_TAB}.dsdb_dir_btn'
    # Transfer tab
    TRANS_TAB = 'transfer_tab_ui'
    TRANS_SPLIT = f'{TRANS_TAB}.transfer_splitter'
    SRC_ASSET_TV = f'{TRANS_TAB}.dsdb_asset_tv'
    TRANS_SELECT_COUNTER = f'{TRANS_TAB}.transfer_selection_counter'
    TRANS_COPY_BTN = f'{TRANS_TAB}.transfer_copy_btn'
