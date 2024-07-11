from os import path
from pathlib import Path
from typing import Dict, List, Union

from platformdirs import user_documents_dir
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
        LINK: str = "#5688c7"
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
TEMPLATE_CFG_PATH = path.join(DIR_PATH, "template.config.ini")
DOC_PATH = user_documents_dir()
DOC_DATA_PATH = path.join(DOC_PATH, "xpuz")
DOC_CAT_PATH = path.join(DOC_DATA_PATH, "user")
DOC_CFG_PATH = path.join(DOC_DATA_PATH, "config.ini")
LOCALES_PATH = path.join(DIR_PATH, "locales")
BASE_POT_PATH = path.join(LOCALES_PATH, "base.pot")
ASSETS_PATH = path.join(DIR_PATH, "assets")
IMAGES_PATH = path.join(ASSETS_PATH, "images")
CWORD_IMG_LIGHT_PATH = path.join(IMAGES_PATH, "cword_light.png")
CWORD_IMG_DARK_PATH = path.join(IMAGES_PATH, "cword_dark.png")
FS_IMG_LIGHT_PATH = path.join(IMAGES_PATH, "fs_light.png")
FS_IMG_DARK_PATH = path.join(IMAGES_PATH, "fs_dark.png")
EXPORT_IMG_PATH = path.join(IMAGES_PATH, "export.png")
IMPORT_IMG_PATH = path.join(IMAGES_PATH, "import.png")
FOLDER_IMG_PATH = path.join(IMAGES_PATH, "folder.png")
WIN_LOGO_PATH = path.join(IMAGES_PATH, "logo.ico")
LINUX_LOGO_PATH = "@" + path.join(IMAGES_PATH, "logo.xbm")
BASE_CWORDS_PATH = path.join(DIR_PATH, "base_cwords")
ATTEMPTS_DB_PATH = path.join(DIR_PATH, "data", "attempts_db.json")


"""Crossword-related constants."""
DIFFICULTIES: List[str] = ["Easy", "Medium", "Hard", "Extreme"]
ACROSS: str = "ACROSS"
DOWN: str = "DOWN"
EMPTY: str = "\u25AE"
NONLANGUAGE_PATTERN: Pattern = compile(r"\PL")
QUALITY_MAP: Dict[str, int] = {
    "terrible": 0.05,
    "poor": 0.25,
    "average": 0.5,
    "great": 0.7,
    "perfect": 1.05,
}
WHITESPACE_SCALAR: float = 1.9
DIMENSIONS_CONSTANT: int = 1


"""PDF-related constants"""
PDF_WIDTH = 3508
PDF_HEIGHT = 2480
PDF_MARGIN = 150
FONTSIZE_DIR_TITLE = 100
FONTSIZE_DEF = 40
PAGE_DEF_MAX = 25


"""Base english strings"""
BASE_ENG_CWORD_QUALITIES: List[str] = [
    "terrible",
    "poor",
    "average",
    "great",
    "perfect",
]
BASE_ENG_APPEARANCES: List[str] = ["light", "dark", "system"]
BASE_ENG_BROWSER_VIEWS: List[str] = ["Categorised", "Flattened"]
BASE_ENG_APP_VIEWS: List[str] = ["Browser", "Embedded"]


"""Misc constants"""
PYPI_URL = "https://pypi.org/project/xpuz/"
RELEASE_API_URL = (
    "https://api.github.com/repos/tomasvana10/xpuz/releases/latest"
)
DIM = (900, 650)
EDITOR_DIM = (1125, 600)
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
