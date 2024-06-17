"""Main module for crossword_puzzle that creates a GUI for the user to generate
a customisable crossword, as well as provides the ability to view it in a Flask
web application.
"""

from configparser import ConfigParser

from babel import Locale

from crossword_puzzle.base import Base
from crossword_puzzle.constants import BASE_CFG_PATH
from crossword_puzzle.utils import GUIHelper, _get_language_options


def start() -> None:
    cfg: ConfigParser = ConfigParser()
    cfg.read(BASE_CFG_PATH)
    locale: Locale = Locale.parse(cfg.get("m", "language"))
    GUIHelper._install_translations(locale)
    app: Base = Base(locale=locale, lang_info=_get_language_options(), cfg=cfg)
    app.mainloop()


if __name__ == "__main__":
    start()
