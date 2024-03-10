'''Constants that are used by `cword_gen.py`, `main.py`, `definitions_parser.py` and `locale_utils.py`'''

import os
from typing import Dict, List, Union
from pathlib import Path

import regex


class Paths:
    '''Absolute paths used across the source code.'''
    CONFIG_PATH = Path(__file__).resolve().parents[0] / "config.ini"
    LOCALES_PATH = Path(__file__).resolve().parents[1] / "locales"
    BASE_POT_PATH = os.path.join(LOCALES_PATH, "base.pot")
    CWORD_IMG_LIGHT_PATH = Path(__file__).resolve().parents[1] / os.path.join("assets", "images", "cword_light.png")
    CWORD_IMG_DARK_PATH = Path(__file__).resolve().parents[1] / os.path.join("assets", "images", "cword_dark.png")
    LOGO_PATH = Path(__file__).resolve().parents[1] / os.path.join("assets", "images", "logo.ico")
    BASE_CWORDS_PATH = Path(__file__).resolve().parents[0] / "base_cwords"
    ATTEMPTS_DB_PATH = Path(__file__).resolve().parents[0] / os.path.join("data", "attempts_db.json")
    

class Colour:
    '''Light, dark and global colour specifications for widgets in `main.py`.'''
    class Global:
        BUTTON = "#21528C"
        BUTTON_HOVER = "#13385F"
        EXIT_BUTTON = "#ED3B4D"
        EXIT_BUTTON_HOVER = "#BF0013"
        BUTTON_TEXT_COLOUR = "#DDE3ED"
        DIFFICULTIES: List[str] = ["#089E19", "#FCBA03", "#E01C07", "#6408A6"]
        
    class Light:
        MAIN = "#C7D0D4"
        SUB = "#DFE8ED"
        TEXT = "#242424" # From tkinter, needed for web app
        TEXT_DISABLED = "#999999"
        WORD_FOCUS = "#A7D8FF"
        CELL_FOCUS = "#FFDA03"
        CORRECT = "#20D44A"
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
    '''Generic difficulty names for crosswords. In a crossword directory's `info.json` file, they
    are specified as indexes and not strings.
    '''
    DIFFICULTIES: List[str] = ["Easy", "Medium", "Hard", "Extreme"]


class LangReplacements:
    '''See information about this class in `locale_utils.py`.'''
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


class CrosswordDirections:
    '''Constants representing words going across or down.'''
    ACROSS: str = "ACROSS"
    DOWN: str = "DOWN"


class CrosswordStyle:
    '''The value of an "empty" cell (containing no letters) in the crossword grid.'''
    EMPTY: str = "▮"


class CrosswordRestrictions:
    '''Used in `definitions_parser.py` to remove all non-language characters from the words/keys of 
    a definitions dictionary.
    '''
    KEEP_LANGUAGES_PATTERN = regex.compile(r"\PL") # The opposite of \p{l} which matches characters from any language


class DimensionsCalculation:
    '''Values that aid with scaling whitespace and providing an appropriate side length for the grid.'''
    # Decrease attributes = break everything
    # Increase attributes = wait forever to make a crossword
    WHITESPACE_SCALAR: float = 1.9
    DIMENSIONS_CONSTANT: int = 1
    

class BaseEngStrings:
    BASE_ENG_APPEARANCES: List[str] = ["light", "dark", "system"]