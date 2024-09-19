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

