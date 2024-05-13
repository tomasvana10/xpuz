"""General/specialised utility functions to aid ``main`` and ``cword_gen``."""

from __future__ import annotations

from configparser import ConfigParser
from json import dump, load
from math import ceil
from os import path, scandir
from random import randint
from typing import Dict, Union

from babel import Locale

from crossword_puzzle.constants import Colour, CrosswordDifficulties, CrosswordQuality, Paths


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
    localised_lang_db: Dict[str, str] = dict()  # Used to retrieve the language
                                                # code for the selected language
                                                # e.x. {"አማርኛ": "am",}
    localised_langs: Dict[str, str] = list()  # Used in the language selection
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
) -> Dict[str, Union[str, int]]:
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


def _get_colour_palette_for_webapp(appearance_mode: str) -> Dict[str, str]:
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
    cfg: ConfigParser = ConfigParser()
    cfg.read(Paths.CONFIG_PATH)
    name: str = crossword.name
    word_count: int = crossword.word_count

    attempts_db: Dict[str, int] = _load_attempts_db()
    try:
        max_attempts: int = attempts_db[str(word_count)]  # Get amount of attempts
                                                          # based on word count
        max_attempts *= CrosswordQuality.QUALITY_MAP[  # Scale max attempts based
            # on crossword quality
            cfg.get("misc", "cword_quality")
        ]
        max_attempts = int(ceil(max_attempts))
    except KeyError:  # Fallback to only a single generation attempt
        max_attempts = 1
    attempts: int = 0  # Track current amount of attempts

    reinsert_definitions: Dict[str, str] = crossword.definitions
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
) -> Dict[str, str]:
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


def _load_attempts_db() -> Dict[str, int]:
    """Load ``attempts_db.json``, which specifies how many generation attempts
    should be conducted for a crossword based on its word count. This is
    integral to the crossword optimisation process, as crossword generation
    time scales logarithmically with word count.
    """

    with open(Paths.ATTEMPTS_DB_PATH) as file:
        return load(file)


def _make_cword_info_json(path_, cword_name, category) -> None:
    """Make an info.json file for a given crossword since it does not exist.
    Makes it easier for the end-user to make their own crossword if they
    really want to.
    """

    with open(path.join(path_, "info.json"), "w") as info_obj, open(
        path.join(path_, "definitions.json"), "r"
    ) as def_obj:
        total_definitions: int = len(load(def_obj))

        # Infer the difficulty and crossword name if possible
        try:
            parsed_cword_name_components = path.basename(path_).split("-")
            difficulty: int = CrosswordDifficulties.DIFFICULTIES.index(
                parsed_cword_name_components[-1].title()
            )
            adjusted_cword_name = "-".join(parsed_cword_name_components[0:-1])
        except Exception:
            difficulty: int = 0
            adjusted_cword_name = cword_name

        return dump(
            {
                "total_definitions": total_definitions,
                "difficulty": difficulty,
                "symbol": "0x2717",
                "name": adjusted_cword_name,
                "translated_name": "",
                "category": category,
            },
            info_obj,
            indent=4,
        )


def _make_category_info_json(path_) -> None:
    """Write a new info.json to a category since it does not exist in the a
    category's directory.
    """
    hex_ = "#%06X" % randint(0, 0xFFFFFF)
    with open(path_, "w") as f:
        return dump({"bottom_tag_colour": hex_}, f, indent=4)
