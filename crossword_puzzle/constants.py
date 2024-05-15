from os import path
from pathlib import Path
from typing import Dict, List, Union

from regex import compile as compile_


class Paths:
    """Absolute paths used across the source code."""

    DIR_PATH = Path(__file__).resolve().parents[0]
    CONFIG_PATH = path.join(DIR_PATH, "config.ini")
    LOCALES_PATH = path.join(DIR_PATH, "locales")
    BASE_POT_PATH = path.join(LOCALES_PATH, "base.pot")
    CWORD_IMG_LIGHT_PATH = path.join(
        DIR_PATH, "assets", "images", "cword_light.png"
    )
    CWORD_IMG_DARK_PATH = path.join(
        DIR_PATH, "assets", "images", "cword_dark.png"
    )
    LOGO_PATH = path.join(DIR_PATH, "assets", "images", "logo.ico")
    BASE_CWORDS_PATH = path.join(DIR_PATH, "base_cwords")
    ATTEMPTS_DB_PATH = path.join(DIR_PATH, "data", "attempts_db.json")


class Colour:
    """Light, dark and global colour specifications for widgets in ``main.py``."""

    class Global:
        BUTTON = "#21528C"
        BUTTON_HOVER = "#13385F"
        EXIT_BUTTON = "#ED3B4D"
        EXIT_BUTTON_HOVER = "#BF0013"
        GREEN_BUTTON = "#20D44A"
        GREEN_BUTTON_HOVER = "#259c41"
        BUTTON_TEXT_COLOUR = "#DDE3ED"
        DIFFICULTIES: List[str] = ["#089E19", "#FCBA03", "#E01C07", "#6408A6"]

    class Light:
        MAIN = "#C7D0D4"
        SUB = "#DFE8ED"
        TEXT = "#242424"  # From tkinter, needed for web app
        TEXT_DISABLED = "#999999"
        WORD_FOCUS = "#A7D8FF"
        CELL_FOCUS = "#FFDA03"
        CORRECT = "#2f9e49"
        WRONG = "#FC0A2A"

    class Dark:
        MAIN = "#263238"
        SUB = "#37474F"
        TEXT = "#D7D6D6"
        TEXT_DISABLED = "#737373"
        WORD_FOCUS = "#5B778C"
        CELL_FOCUS = "#998202"
        CORRECT = "#25C44B"
        WRONG = "#D90D28"


class CrosswordDifficulties:
    """Generic difficulty names for crosswords. In a crossword directory's
    ``info.json`` file, they are specified as indexes and not strings.
    """

    DIFFICULTIES: List[str] = ["Easy", "Medium", "Hard", "Extreme"]


class LangReplacements:
    """See information about this class in ``_locale_utils.py``."""

    REPLACEMENTS: Dict[str, Union[str, None]] = {
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
    REVERSE = {value: key for key, value in REPLACEMENTS.items()}


class CrosswordDirection:
    """Constants representing words going across or down."""

    ACROSS: str = "ACROSS"
    DOWN: str = "DOWN"


class CrosswordStyle:
    """The value of an "empty" cell (containing no letters) in the crossword
    grid.
    """

    EMPTY: str = "▮"


class CrosswordRestrictions:
    """Used in ``definitions_parser.py`` to remove all non-language characters
    from the words/keys of a definitions dictionary.
    """

    KEEP_LANGUAGES_PATTERN = compile_(r"\PL")  # The opposite of \p{l} which
                                               # matches characters from any
                                               # language


class CrosswordQuality:
    QUALITY_MAP: Dict[int, str] = {
        "terrible": 0.05,
        "poor": 0.25,
        "average": 0.5,
        "great": 0.7,
        "perfect": 1.05,
    }


class DimensionsCalculation:
    """Values that aid with scaling whitespace and providing an appropriate
    side length for the grid. Do not modify.
    """

    WHITESPACE_SCALAR: float = 1.9
    DIMENSIONS_CONSTANT: int = 1


class BaseEngStrings:
    BASE_ENG_APPEARANCES: List[str] = ["light", "dark", "system"]
    BASE_ENG_CWORD_QUALITIES: List[str] = [
        "terrible",
        "poor",
        "average",
        "great",
        "perfect",
    ]
