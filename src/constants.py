'''Constants that are used by `cword_gen.py`, `main.py`, `definitions_parser.py` and `locale_utils.py`'''

from pathlib import Path

class Paths:
    '''Absolute paths used across the source code.'''
    CONFIG_PATH = Path(__file__).resolve().parents[0] / "config.ini"
    LOCALES_PATH = Path(__file__).resolve().parents[1] / "locales"
    CWORD_IMG_LIGHT_PATH = Path(__file__).resolve().parents[1] / "assets/images/cword_img_light.png"
    CWORD_IMG_DARK_PATH = Path(__file__).resolve().parents[1] / "assets/images/cword_img_dark.png"
    CWORDS_PATH = Path(__file__).resolve().parents[0] / "cwords"
    ATTEMPTS_DB_PATH = Path(__file__).resolve().parents[0] / "data/attempts_db.json"
    

class Colour:
    '''Light, dark and global colour specifications for widgets in `main.py`.'''
    class Global:
        EXIT_BUTTON = "#ED3B4D"
        EXIT_BUTTON_HOVER = "#BF0013"
        
    class Light:
        MAIN = "#B0BEC5"
        SUB = "#CFD8DC"
        TEXT_DISABLED = "#999999"

    class Dark:
        MAIN = "#263238"
        SUB = "#37474F"
        TEXT_DISABLED = "#737373"


class CrosswordDifficulties:
    '''Generic difficulty names for crosswords. In a crossword directory's `info.json` file, they
    are specified as indexes and not strings.
    '''
    DIFFICULTIES = ["Easy", "Medium", "Hard", "Extreme"]


class Fonts:
    '''Font size, weight and slant specifications for GUI text in `main.py`.'''
    TITLE_FONT = {"size": 30, "weight": "bold", "slant": "roman"}
    SUBHEADING_FONT = {"size": 23, "weight": "normal", "slant": "italic"}
    LABEL_FONT = {"size": 14, "weight": "bold", "slant": "roman"}
    BOLD_LABEL_FONT = {"size": 14, "weight": "bold", "slant": "roman"}


class LanguageReplacementsForPybabel:
    '''See information about this class in `locale_utils.py`.'''
    REPLACEMENTS = {
        "zh-cn": "zh",
        "zh-tw": None,
        "ht": None,
        "hmn": "hnj",
        "sm": None,
    }
    
''' Right to left scripts, can have translations but not for the crossword.
"he": None,
"ar": None,
"fa": None,
"ur": None,
"ps": None,
"ku": None,
"sd": None,
'''


class CrosswordDirections:
    '''Constants representing words going across or down. Used extensively in conditional statements
    and functions in `cword_gen.py`.
    '''
    ACROSS = "a"
    DOWN = "d"


class CrosswordStyle:
    '''The value of an "empty" cell (containing no letters) in the crossword grid.'''
    EMPTY = "▮"


class CrosswordRestrictions:
    '''Used in `definitions_parser.py` to remove all non-language characters from the words/keys of 
    a definitions dictionary.
    '''
    KEEP_LANGUAGES_PATTERN = r"\PL" # The opposite of \p{l} which matches characters from any language


class DimensionsCalculation:
    '''Values that aid with scaling whitespace and providing an appropriate side length for the grid.'''
    # Decrease attributes = break everything
    # Increase attributes = wait forever to make a crossword
    WHITESPACE_SCALAR = 1.85
    DIMENSIONS_CONSTANT = 1
    

class BaseEngStrings:
    BASE_ENG_APPEARANCES = ["light", "dark", "system"]