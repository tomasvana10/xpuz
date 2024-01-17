from pathlib import Path

class Paths:
    CONFIG_PATH = Path(__file__).resolve().parents[0] / "config.ini"
    LOCALES_PATH = Path(__file__).resolve().parents[1] / "locales"
    CWORD_IMG_LIGHT_PATH = Path(__file__).resolve().parents[1] / "assets/images/cword_img_light.png"
    CWORD_IMG_DARK_PATH = Path(__file__).resolve().parents[1] / "assets/images/cword_img_dark.png"
    CWORDS_PATH = Path(__file__).resolve().parents[0] / "cwords"
    ATTEMPTS_DB_PATH = Path(__file__).resolve().parents[0] / "data/attempts_db.json"
    

class Colour:
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
    DIFFICULTIES = ["Easy", "Medium", "Hard", "Extreme"]


class Fonts:
    TITLE_FONT = {"size": 30, "weight": "bold", "slant": "roman"}
    SUBHEADING_FONT = {"size": 23, "weight": "normal", "slant": "italic"}
    LABEL_FONT = {"size": 14, "weight": "bold", "slant": "roman"}
    BOLD_LABEL_FONT = {"size": 14, "weight": "bold", "slant": "roman"}


class LanguageReplacementsForPybabel:
    REPLACEMENTS = {
        "zh-cn": "zh",
        "zh-tw": None,
        "ht": None,
        "hmn": "hnj",
        "sm": None,
    }


class CrosswordDirections:
    ACROSS = "a"
    DOWN = "d"


class CrosswordStyle:
    EMPTY = "▮"


class CrosswordRestrictions:
    KEEP_LANGUAGES_PATTERN = r"\PL" # The opposite of \p{l} which matches characters from any language


class BaseEngStrings:
    BASE_ENG_APPEARANCES = ["light", "dark", "system"]