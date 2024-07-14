from json import load
from os import PathLike, listdir, path
from pprint import pformat
from typing import Dict, Optional, Union

from xpuz.constants import (
    BASE_CWORDS_PATH,
    DIFFICULTIES,
    DOC_CAT_PATH,
    LOCALES_PATH,
)
from xpuz.crossword import Crossword
from xpuz.errors import CrosswordGenerationError, DefinitionsParsingError
from xpuz.td import CrosswordInfo
from xpuz.utils import (
    _find_best_crossword,
    _make_cword_info_json,
    _update_cword_info_word_count,
)


class CrosswordWrapper:
    """Wrapper to simplify both the internal and external interactions with a
    crossword and its data.

    Also contains methods to ensure the integrity of a crossword's data whenever
    it is being accessed at runtime.
    """

    helper: Union[None, object] = None  # Set to ``main.GUIHelper`` at runtime
                                        # (if using the GUI)
    logger: object = lambda *args, **kwargs: print(f"{args[0]}({args[1]})") 

    def __init__(
        self,
        category: str,
        name: str,
        word_count: int = 0,
        *,
        language: str = "en",
        optimise: bool = True,  # Run ``utils._find_best_crossword``
        category_object: Optional[object] = None,
        value: int = None,
    ) -> None:
        self.category = category
        self.language = language
        self.fullname = name  # capitals-easy, for example
        self.word_count = word_count
        self.optimise = optimise

        self.crossword: Union[None, Crossword] = None
        self.toplevel: PathLike = self._get_toplevel()
        self.total_definitions: int = len(self.definitions)
        self._validate_data()
        self.name: str = self.info["name"]  # Name with the suffix removed

        self.err_flag: bool = False  # Set to true if errors occur at runtime

        self.category_object = category_object
        self.value = value
        self.translated_name: str = self.info["translated_name"] or self.name
        self.difficulty: str = DIFFICULTIES[self.info["difficulty"]]
        self.translated_difficulty = _(self.difficulty)
        self.display_name: str = f"{self.translated_name} ({_(self.difficulty)})"

    def __str__(self) -> str:
        sorted_dict = dict(sorted(list(self.__dict__.items())))
        attr_names = list(sorted_dict.keys())
        attr_vals = list(sorted_dict.values())
        return str(
            pformat(
                {key: value for key, value in zip(attr_names, attr_vals)},
                width=50,
            )
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
        """Minimise runtime errors by ensuring the integrity of this crossword's
        info.json file.
        """

        info: CrosswordInfo = self.info
        if not all(  # Pick up missing attributes
            key in info for key in CrosswordInfo.__dict__["__annotations__"]
        ):
            return _make_cword_info_json(
                self.toplevel, self.fullname, self.category
            )

        # All attributes are present, but the word count may be inaccurate.
        if info["total_definitions"] != self.total_definitions:
            return _update_cword_info_word_count(
                self.toplevel, info, self.total_definitions
            )

    def _get_toplevel(self) -> PathLike:
        """Find the absolute path to the toplevel of a crossword
        (e.g <pkg_path>/locales/geography/capitals-easy).

        The path returned will be in 1 of 3 locations:
        1. Locales directory (if it is found),
        2. Base crossword directory (if not localised version is present),
        3. The system's document directory (if it is available and the crossword
           belongs to the "user" category).
        """

        toplevel = path.join(  # Assume there is a localised version available
            LOCALES_PATH, self.language, "cwords", self.category, self.fullname
        )
        if (  # 1
            path.exists(toplevel)
            and "definitions.json" in listdir(toplevel)
            and path.getsize(path.join(toplevel, "definitions.json")) > 0
        ):
            return toplevel
        else:
            toplevel = path.join(  # 2
                BASE_CWORDS_PATH, self.category, self.fullname
            )
            if not path.exists(toplevel):
                toplevel = path.join(DOC_CAT_PATH, self.fullname)  # 3
            return toplevel

    def make(self) -> Union[None, Crossword]:
        """Generate a crossword, running ``utils._find_best_crossword`` if
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
            if self.optimise:  # Also find the best crossword
                self.crossword = _find_best_crossword(
                    self.crossword, Crossword
                )

            return self.crossword

        except (CrosswordGenerationError, DefinitionsParsingError) as ex:
            help_func(type(ex).__name__, str(ex), cword_or_def_err=True)
            self.err_flag = True
        except Exception as ex:
            help_func(type(ex).__name__, str(ex), other_gen_err=True)
            self.err_flag = True
        return None

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
