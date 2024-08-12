"""Constant values used across the source code, defining values such as paths
and colour values for both the GUI and the web application.

Attributes:
    DIR_PATH: Path to the toplevel of `xpuz`.
    TEMPLATE_CFG_PATH: Path to template `config.ini` file.
    DOC_PATH: Path to the system's documents directory or equivalent.
    DOC_DATA_PATH: Path to the `xpuz` folder within the system's documents directory.
    DOC_CAT_PATH: Path to the `user` folder within the `xpuz` folder.
    DOC_CFG_PATH: Path to the `config.ini` file within the `xpuz` folder.
    LOCALES_PATH: Path to the package's locales folder.
    BASE_POT_PATH: Path to the package's translation template file.
    ASSETS_PATH: Path to the package's `assets` folder.
    IMAGES_PATH: Path to the package's `image` folder, located within `assets`. 
    BASE_CWORDS_PATH: Path to the package's base crosswords folder.
    ATTEMPTS_DB_PATH: Path to the `attempts_db.json` file for crossword optimisation.
    DIFFICULTIES: Crossword difficulties.
    ACROSS: Representation of a word going right to left.
    DOWN: Representation of a word going top to bottom.
    EMPTY: Representation of a void cell in the crossword grid.
    NONLANGUAGE_PATTERN: Regex pattern to filter out non-language characters.
    QUALITY_MAP: Mapping of crossword quality descriptors to a float value, 
        which is used to scale how many optimisation attempts are undergone to 
        make a crossword with that quality.
    WHITESPACE_SCALAR: A value to scale the whitespace present in a crossword grid.
    DIMENSIONS_CONSTANT: A value that is added to the final grid dimension
        calculation after applying `math.ceil`.
    PDF_WIDTH: PDF A4 width.
    PDF_HEIGHT: PDF A4 height.
    PDF_MARGIN: PDF A4 margin.
    FONTSIZE_DIR_TITLE: Font size of the title for the 'Across' or 'Down'
        columns in a PDF.
    FONTSIZE_DEF: Clue font size.
    PAGE_DEF_MAX: How many clues can fit on a page.
    DIM: Standard tkinter GUI dimensions
    EDITOR_DIM: Dimensions for the crossword editor within the tkinter GUI.
    LANG_REPLACEMENTS: Mapping of google translate language codes to their
        respective `Babel` language codes. `None` if they do not exist, otherwise,
        a string representing the `Babel`-correct code.
    
    
    
"""

from os import path
from pathlib import Path, PosixPath, WindowsPath
from typing import Dict, List, Union

from platformdirs import user_documents_dir
from regex import Pattern, compile


class Colour:
    """Hex colour specification for both the GUI and the web app."""

    class Global:
        """Global hex colours."""

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
        """Light mode hex colours."""

        MAIN: str = "#C7D0D4"
        SUB: str = "#DFE8ED"
        TEXT: str = "#242424"
        TEXT_DISABLED: str = "#999999"
        WORD_FOCUS: str = "#A7D8FF"
        CELL_FOCUS: str = "#FFDA03"
        CORRECT: str = "#2f9e49"
        WRONG: str = "#FC0A2A"

    class Dark:
        """Dark mode hex colours."""

        MAIN: str = "#263238"
        SUB: str = "#37474F"
        TEXT: str = "#D7D6D6"
        TEXT_DISABLED: str = "#737373"
        WORD_FOCUS: str = "#5B778C"
        CELL_FOCUS: str = "#998202"
        CORRECT: str = "#25C44B"
        WRONG: str = "#D90D28"


# Absolute paths used across the source code.
DIR_PATH: Union[PosixPath, WindowsPath] = Path(__file__).resolve().parents[0]
TEMPLATE_CFG_PATH: str = path.join(DIR_PATH, "template.config.ini")
DOC_PATH: str = user_documents_dir()
DOC_DATA_PATH: str = path.join(DOC_PATH, "xpuz")
DOC_CAT_PATH: str = path.join(DOC_DATA_PATH, "user")
DOC_CFG_PATH: str = path.join(DOC_DATA_PATH, "config.ini")
LOCALES_PATH: str = path.join(DIR_PATH, "locales")
BASE_POT_PATH: str = path.join(LOCALES_PATH, "base.pot")
ASSETS_PATH: str = path.join(DIR_PATH, "assets")
IMAGES_PATH: str = path.join(ASSETS_PATH, "images")
CWORD_IMG_LIGHT_PATH: str = path.join(IMAGES_PATH, "cword_light.png")
CWORD_IMG_DARK_PATH: str = path.join(IMAGES_PATH, "cword_dark.png")
FS_IMG_LIGHT_PATH: str = path.join(IMAGES_PATH, "fs_light.png")
FS_IMG_DARK_PATH: str = path.join(IMAGES_PATH, "fs_dark.png")
EXPORT_IMG_PATH: str = path.join(IMAGES_PATH, "export.png")
IMPORT_IMG_PATH: str = path.join(IMAGES_PATH, "import.png")
EXPORT_DIS_IMG_PATH: str = path.join(IMAGES_PATH, "export_dis.png")
IMPORT_DIS_IMG_PATH: str = path.join(IMAGES_PATH, "import_dis.png")
FOLDER_IMG_PATH: str = path.join(IMAGES_PATH, "folder.png")
FOLDER_DIS_IMG_PATH: str = path.join(IMAGES_PATH, "folder_dis.png")
WIN_LOGO_PATH: str = path.join(IMAGES_PATH, "logo.ico")
LINUX_LOGO_PATH: str = "@" + path.join(IMAGES_PATH, "logo.xbm")
BASE_CWORDS_PATH: str = path.join(DIR_PATH, "base_cwords")
ATTEMPTS_DB_PATH: str = path.join(DIR_PATH, "data", "attempts_db.json")


# Crossword-related constants.
DIFFICULTIES: List[str] = ["Easy", "Medium", "Hard", "Extreme"]
ACROSS: str = "ACROSS"
DOWN: str = "DOWN"
EMPTY: str = "\u25ae"
NONLANGUAGE_PATTERN: Pattern = compile(r"\PL")
QUALITY_MAP: Dict[str, float] = {
    "terrible": 0.05,
    "poor": 0.25,
    "average": 0.5,
    "great": 0.7,
    "perfect": 1.05,
}
WHITESPACE_SCALAR: float = 1.9
DIMENSIONS_CONSTANT: int = 1


# PDF-related constants
PDF_WIDTH: int = 3508
PDF_HEIGHT: int = 2480
PDF_MARGIN: int = 150
FONTSIZE_DIR_TITLE: int = 100
FONTSIZE_DEF: int = 40
PAGE_DEF_MAX: int = 25


# Base english strings
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
BASE_ENG_EXPORTS: List[str] = ["PDF", "ipuz"]


# Misc constants
PYPI_URL: str = "https://pypi.org/project/xpuz/"
RELEASE_API_URL: str = (
    "https://api.github.com/repos/tomasvana10/xpuz/releases/latest"
)
PROJECT_URL: str = "https://github.com/tomasvana10/xpuz"
DIM: Tuple[int, int] = (900, 650)
EDITOR_DIM: Tuple[int, int] = (1125, 600)
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
REVERSE_LANG_REPLACEMENTS: Dict[Union[str, None], str] = {
    value: key for key, value in LANG_REPLACEMENTS.items()
}
