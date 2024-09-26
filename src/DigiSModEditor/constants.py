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
    L_PANEL = 'left_panel_ui'
    MODS_DIR_TXT = f'{L_PANEL}.mods_dir_text'
    MODS_DIR_BTN = f'{L_PANEL}.mods_dir_btn'
    MODS_DROPDOWN = f'{L_PANEL}.current_mods_dropdown'
    CREATE_MODS_BTN = f'{L_PANEL}.new_mods_btn'
    MODS_MDL = f'{L_PANEL}.mods_model'
