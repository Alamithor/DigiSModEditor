from enum import StrEnum


class Pattern(StrEnum):
    # GEO = r'\.(geom)'
    # SKEL = r'\.(skel)'
    ANIM = r'(\_\w{2}\d{2}|)\.(anim)'
