from os import path
from pathlib import Path
from typing import Dict, List, Union

from regex import Pattern, compile

class Colour:
    """Global and light/dark hex colours."""

    class Global:
        BUTTON: str = "#21528C"
        BUTTON_HOVER: str = "#13385F"
        EXIT_BUTTON: str = "#ED3B4D"
        EXIT_BUTTON_HOVER: str = "#BF0013"
        GREEN_BUTTON: str = "#20D44A"
        GREEN_BUTTON_HOVER: str = "#259c41"
        BUTTON_TEXT_COLOUR: str = "#DDE3ED"
        DIFFICULTIES: List[str] = ["#089E19", "#FCBA03", "#E01C07", "#6408A6"]

    class Light:
        MAIN: str = "#C7D0D4"
        SUB: str = "#DFE8ED"
        TEXT: str = "#242424"
        TEXT_DISABLED: str = "#999999"
        WORD_FOCUS: str = "#A7D8FF"
        CELL_FOCUS: str = "#FFDA03"
        CORRECT: str = "#2f9e49"
        WRONG: str = "#FC0A2A"

    class Dark:
        MAIN: str = "#263238"
        SUB: str = "#37474F"
        TEXT: str = "#D7D6D6"
        TEXT_DISABLED: str = "#737373"
        WORD_FOCUS: str = "#5B778C"
        CELL_FOCUS: str = "#998202"
        CORRECT: str = "#25C44B"
        WRONG: str = "#D90D28"


"""Absolute paths used across the source code."""
DIR_PATH = Path(__file__).resolve().parents[0]
BASE_CFG_PATH = path.join(DIR_PATH, "config.ini")
LOCALES_PATH = path.join(DIR_PATH, "locales")
BASE_POT_PATH = path.join(LOCALES_PATH, "base.pot")
CWORD_IMG_LIGHT_PATH = path.join(
    DIR_PATH, "assets", "images", "cword_light.png"
)
CWORD_IMG_DARK_PATH = path.join(DIR_PATH, "assets", "images", "cword_dark.png")
FS_IMG_LIGHT_PATH = path.join(DIR_PATH, "assets", "images", "fs_light.png")
FS_IMG_DARK_PATH = path.join(DIR_PATH, "assets", "images", "fs_dark.png")
LOGO_PATH = path.join(DIR_PATH, "assets", "images", "logo.ico")
BASE_CWORDS_PATH = path.join(DIR_PATH, "base_cwords")
ATTEMPTS_DB_PATH = path.join(DIR_PATH, "data", "attempts_db.json")


"""Crossword-related constants."""
DIFFICULTIES: List[str] = ["Easy", "Medium", "Hard", "Extreme"]
ACROSS: str = "ACROSS"
DOWN: str = "DOWN"
EMPTY: str = "▮"
KEEP_LANGUAGES_PATTERN: Pattern = compile(r"\PL")
QUALITY_MAP: Dict[str, int] = {
    "terrible": 0.05,
    "poor": 0.25,
    "average": 0.5,
    "great": 0.7,
    "perfect": 1.05,
}
WHITESPACE_SCALAR: float = 1.9
DIMENSIONS_CONSTANT: int = 1
BASE_ENG_CWORD_QUALITIES: List[str] = [
    "terrible",
    "poor",
    "average",
    "great",
    "perfect",
]

"""Misc constants"""
DIM = (842, 595)
PAGE_MAP: Dict[str, str] = {
    "HomePage": "Crossword Puzzle",
    "BrowserPage": "Crossword Browser",
    "EditorPage": "Crossword Editor",
}
LANG_REPLACEMENTS: Dict[str, Union[str, None]] = {
    "zh-cn": "zh",
    "zh-tw": None,
    "ht": None,
    "hmn": "hnj",
    "yi": None,
    "ug": None,
    "sm": None,
    "he": None,
    "ar": None,
    "fa": None,
    "ur": None,
    "ps": None,
    "ku": None,
    "sd": None,
}
REVERSE_LANG_REPLACEMENTS = {
    value: key for key, value in LANG_REPLACEMENTS.items()
}
BASE_ENG_APPEARANCES: List[str] = ["light", "dark", "system"]
BASE_ENG_VIEWS: List[str] = ["Categorised", "Flattened"]
