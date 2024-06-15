from json import load
from pprint import pformat
from os import PathLike, listdir, path
from typing import Dict, Union

from constants import BASE_CWORDS_PATH, DIFFICULTIES, LOCALES_PATH
from crossword import Crossword
from td import CrosswordInfo
from errors import CrosswordGenerationError, DefinitionsParsingError
from utils import (
    _make_cword_info_json,
    _update_cword_info_word_count,
    find_best_crossword,
)


def logger(*args, **kwargs) -> None:
    """Command-line logger for errors in crossword generation/definitions
    parsing when not using the GUI.
    """
    print(f"{args[0]}({args[1]})")


class CrosswordWrapper:
    """Wrapper to simplify both the internal and external interactions with a
    crossword and its data.

    Also contains methods to ensure the integrity of a crossword's data whenever
    it is being accessed at runtime.
    """

    helper: Union[None, object] = None  # Set to ``main.AppHelper`` at runtime
                                        # (if using the GUI)
    logger: object = logger  # Default method for issuing errors to the user

    def __init__(
        self,
        category: str,
        name: str,
        word_count: int = 0,
        *,
        language: str = "en",
        optimise: bool = True,  # Run ``utils.find_best_crossword``
        category_object: object = None,  # The category block who is the parent of
                                         # this wrapper's crossword info block
        value: int = None,
    ) -> None:
        self.category = category
        self.language = language
        self.fullname = name  # capitals-easy, for example
        self.word_count = word_count
        self.optimise = optimise

        self.crossword: Union[None, Crossword] = (
            None  # Updated when ``self.make`` is called
        )
        self.toplevel: PathLike = self._get_toplevel()
        self.total_definitions: int = len(self.definitions)
        self._validate_data()
        self.name: str = self.info["name"]  # Name with the suffix removed

        self.err_flag: bool = False  # Set to true if errors occur at runtime

        self.category_object = category_object
        self.value = value
        self.translated_name: str = self.info["translated_name"] or self.name
        self.difficulty: str = DIFFICULTIES[self.info["difficulty"]]

    def __str__(self) -> str:
        sorted_dict = dict(sorted(list(self.__dict__.items())))
        attr_names = list(sorted_dict.keys())
        attr_vals = list(sorted_dict.values())
        return str(pformat(
            {key: value for key, value in zip(attr_names, attr_vals)}, width=50)
        )

    def set_word_count(self, count: int) -> None:
        """Set this wrapper's word count. Called when the user changes their
        word count preference.
        """
        self.word_count: int = count

    def _check_info(self) -> None:
        """Ensure the info.json of this crossword's toplevel (whether that is
        the localised toplevel or the base toplevel) exists and is not empty.
        Otherwise, run a utility function to derive a new info.json from the
        existing definitions.
        """
        if (
            not path.exists(path.join(self.toplevel, "info.json"))
            or path.getsize(path.join(self.toplevel, "info.json")) <= 0
        ):
            return _make_cword_info_json(
                self.toplevel, self.fullname, self.category
            )

    def _validate_data(self) -> None:
        """Ensure a crossword's data either:
        1. Contains all the keys specified in the annotations of CrosswordInfo, or
        2. Has an identical amount of definitions in its definitions.json file
           compared to the figure specified in its info (``total_definitions``)

        Otherwise, it creates a new info.json file.
        """

        info: CrosswordInfo = self.info
        if not all(  # Say, ``total_definitions`` is not present. This picks it up
            key in info for key in CrosswordInfo.__dict__["__annotations__"]
        ):
            return _make_cword_info_json(
                self.toplevel, self.fullname, self.category
            )

        if info["total_definitions"] != self.total_definitions:
            return _update_cword_info_word_count(
                self.toplevel, info, self.total_definitions
            )

    def _get_toplevel(self) -> PathLike:
        """Return the absolute path to the base directory of a crossword.
        First, the method checks if the crossword has a localised version of
        itself present in ``locales``. If it doesn't exist, or doesn't contain
        a ``definitions.json`` file, the method will resort to the base directory
        path. There is no need to check if there is a definitions file in the
        base directory, as an instance of ``CrosswordWrapper`` is only
        instantiated for crosswords in the base crossword directory with a valid
        ``definitions.json`` file.
        """

        toplevel = path.join(
            LOCALES_PATH, self.language, "cwords", self.category, self.fullname
        )
        if (
            path.exists(toplevel)
            and "definitions.json" in listdir(toplevel)
            and path.getsize(path.join(toplevel, "definitions.json")) > 0
        ):  # Valid ``definitions.json``
            return toplevel
        else:  # Resort to base crossword toplevel
            toplevel = path.join(
                BASE_CWORDS_PATH, self.category, self.fullname
            )
            return toplevel

    def make(self) -> Union[None, Crossword]:
        """Generate a crossword, running ``utils.find_best_crossword`` if
        ``self.optimise`` is set to True (it is by default). Any errors caught
        are relayed to the main GUI through the helper attribute of
        ``CrosswordWrapper``.
        """
        help_func = getattr(
            CrosswordWrapper.helper, "show_messagebox", CrosswordWrapper.logger
        )
        try:
            self.crossword = Crossword(
                self.name, self.definitions, self.word_count
            )
            if self.optimise:
                self.crossword = find_best_crossword(self.crossword)

            return self.crossword

        except (CrosswordGenerationError, DefinitionsParsingError) as ex:
            help_func(type(ex).__name__, str(ex), cword_or_def_err=True)
            self.err_flag = True
        except Exception as ex:
            help_func(type(ex).__name__, str(ex), other_gen_err=True)
            self.err_flag = True

    @property
    def cells(self) -> str:
        return self.crossword.cells

    @property
    def definitions(self) -> Dict[str, str]:
        """Return the current definitions of the crossword."""
        with open(path.join(self.toplevel, "definitions.json")) as f:
            return load(f)

    @property
    def info(self) -> CrosswordInfo:
        """Return the current info of the crossword."""
        try:
            with open(path.join(self.toplevel, "info.json")) as f:
                return load(f)
        except Exception:  # Something is wrong with this info
            self._check_info()
            return self.info
