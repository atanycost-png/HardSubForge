"""Sistema de temas e estilos do HardSubForge."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional
from PySide6.QtGui import QColor


class Color:
    """Paleta de cores do tema escuro."""

    BG_DARKEST = "#0D1117"
    BG_DARK = "#161B22"
    BG_MEDIUM = "#21262D"
    BG_LIGHT = "#30363D"
    BG_CARD = "#1C2128"

    BORDER = "#30363D"
    BORDER_HOVER = "#58A6FF"
    BORDER_FOCUS = "#1F6FEB"

    TEXT_PRIMARY = "#E6EDF3"
    TEXT_SECONDARY = "#8B949E"
    TEXT_MUTED = "#484F58"

    PRIMARY = "#1F6FEB"
    PRIMARY_HOVER = "#388BFD"
    PRIMARY_DARK = "#1158C7"

    SUCCESS = "#238636"
    SUCCESS_HOVER = "#2EA043"
    SUCCESS_BG = "#1B3925"

    DANGER = "#DA3633"
    DANGER_HOVER = "#F85149"
    DANGER_BG = "#3D1F1F"

    WARNING = "#D29922"
    WARNING_BG = "#3D2E00"

    INFO = "#58A6FF"
    INFO_BG = "#0C2D6B"

    LOG_BG = "#0D1117"
    LOG_TEXT = "#7EE787"

    PROGRESS_BG = "#21262D"
    PROGRESS_CHUNK = "#1F6FEB"


@dataclass(frozen=True)
class Spacing:
    """Constantes de espaçamento."""

    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32


@dataclass(frozen=True)
class Radius:
    """Constantes de arredondamento."""

    SM = 4
    MD = 8
    LG = 12
    XL = 16
    PILL = 999
