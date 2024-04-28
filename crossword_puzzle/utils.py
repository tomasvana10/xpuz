"""General/specialised utility functions to aid ``main`` and ``cword_gen``."""

from __future__ import annotations

from configparser import ConfigParser
from json import load
from os import path, scandir

from babel import Locale

from crossword_puzzle.constants import Colour, Paths


def _update_config(
    cfg: ConfigParser, section: str, option: str, value: str
) -> None:
    """Update ``cfg`` at the given section, option and value, then write it
    to ``config.ini``.
    """
    cfg[section][option] = value

    with open(Paths.CONFIG_PATH, "w") as f:
        cfg.write(f)


def _get_language_options() -> None:
    """Gather a dictionary that maps each localised language name to its
    english acronym, and a list that contains all of the localised language
    names. This data is derived from ``Paths.LOCALES_PATH``."""
    localised_lang_db: dict[str, str] = dict()  # Used to retrieve the language
    # code for the selected language
    # e.x. {"አማርኛ": "am",}
    localised_langs: dict[str, str] = list()  # Used in the language selection
    # optionmenu
    # e.x. ["አማርኛ", "عربي"]

    i: int = 0
    for locale in sorted(
        [f.name for f in scandir(Paths.LOCALES_PATH) if f.is_dir()]
    ):
        localised_langs.append(Locale.parse(locale).language_name)
        localised_lang_db[localised_langs[i]] = locale
        i += 1

    return [localised_lang_db, localised_langs]


def _load_cword_info(
    category: str, name: str, language: str = "en"
) -> dict[str, str | int]:
    """Load the ``info.json`` file for a crossword. Called by an instance
    of ``main.CrosswordInfoBlock``.
    """
    path_ = path.join(
        Paths.LOCALES_PATH, language, "cwords", category, name, "info.json"
    )
    if not path.exists(path_):  # Fallback to base crossword info
        path_ = path.join(Paths.BASE_CWORDS_PATH, category, name, "info.json")
    with open(path_) as file:
        return load(file)


def _get_colour_palette_for_webapp(appearance_mode: str) -> dict[str, str]:
    """Create a dictionary based on ``constants.Colour``for the web app."""
    sub_class = Colour.Light if appearance_mode == "Light" else Colour.Dark
    return {
        key: value
        for attr in [sub_class.__dict__, Colour.Global.__dict__]
        for key, value in attr.items()
        if key[0] != "_" or key.startswith("BUTTON")
    }


def find_best_crossword(crossword: Crossword) -> Crossword:
    """Determine the best crossword out of a amount of instantiated
    crosswords based on the largest amount of total intersections and
    smallest amount of fails.
    """
    name: str = crossword.name
    word_count: int = crossword.word_count

    attempts_db: dict[str, int] = _load_attempts_db()
    try:
        max_attempts: int = attempts_db[
            str(word_count)
        ]  # Get amount of attempts
        # based on word count
    except KeyError:  # Fallback to only a single generation attempt
        max_attempts = 1
    attempts: int = 0  # Track current amount of attempts

    reinsert_definitions: dict[str, str] = crossword.definitions
    crossword.generate()
    best_crossword = (
        crossword  # Assume the best crossword is the first crossword
    )

    from crossword_puzzle.cword_gen import Crossword

    while attempts <= max_attempts:
        # Setting the "retry" param to True will make the Crossword class
        # only randomise the definitions it is given, not sample new random
        # ones, for reasons explained in the ``_randomise_definitions``
        # method.
        crossword = Crossword(
            name=name,
            definitions=reinsert_definitions,
            word_count=word_count,
            retry=True,
        )
        crossword.generate()

        # Update the new best crossword if it has more intersections than
        # the current crossword and its fails are less than or equal to the
        # current crossword's fails. Changing the fails comparison to simply
        # "less than" is too strict and results in a poor "best" crossword.
        if (
            crossword.total_intersections > best_crossword.total_intersections
        ) and (crossword.fails <= best_crossword.fails):
            best_crossword = crossword
        attempts += 1

    assert best_crossword.generated
    return best_crossword


def load_definitions(
    category: str,
    name: str,
    language: str = "en",
) -> dict[str, str]:
    """Load a definitions json for a given crossword."""
    # Attempt to access the localised crossword
    path_ = path.join(
        Paths.LOCALES_PATH,
        language,
        "cwords",
        category,
        name,
        "definitions.json",
    )
    if not path.exists(path_):  # Fallback to the base crossword
        path_ = path.join(
            Paths.BASE_CWORDS_PATH, category, name, "definitions.json"
        )

    with open(path_) as file:
        return load(file)


def _load_attempts_db() -> dict[str, int]:
    """Load ``attempts_db.json``, which specifies how many generation attempts
    should be conducted for a crossword based on its word count. This is
    integral to the crossword optimisation process, as crossword generation
    time scales logarithmically with word count.
    """
    with open(Paths.ATTEMPTS_DB_PATH) as file:
        return load(file)
