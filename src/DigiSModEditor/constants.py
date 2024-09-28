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
    SPLITTER = 'panel_splitter'

    # Left panel
    L_PANEL = 'left_panel_ui'
    # Mods dir path
    MODS_DIR_TXT = f'{L_PANEL}.mods_dir_text'
    MODS_DIR_BTN = f'{L_PANEL}.mods_dir_btn'
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
