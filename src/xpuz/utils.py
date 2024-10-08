"""General/specialised utility functions."""

import urllib.request as req
from configparser import ConfigParser, NoSectionError
from copy import deepcopy
from gettext import translation
from json import dump, load, loads
from math import ceil
from os import DirEntry, PathLike, listdir, mkdir, path, scandir
from platform import system
from random import randint, sample
from tkinter import messagebox, filedialog
from typing import (
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Union,
    Any,
)
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal
from urllib.error import URLError

from babel import Locale
from babel.core import UnknownLocaleError
from regex import sub
from platformdirs import user_downloads_dir
from customtkinter import CTkFrame

from xpuz.constants import (
    ACROSS,
    ATTEMPTS_DB_PATH,
    BASE_CWORDS_PATH,
    DIFFICULTIES,
    DOC_CAT_PATH,
    DOC_CFG_PATH,
    DOC_DATA_PATH,
    DOC_PATH,
    DOWN,
    EMPTY,
    LOCALES_PATH,
    NONLANGUAGE_PATTERN,
    QUALITY_MAP,
    RELEASE_API_URL,
    TEMPLATE_CFG_PATH,
    Colour,
)
from xpuz.errors import DefinitionsParsingError
from xpuz.td import CrosswordInfo
from xpuz._version import __version__


class GUIHelper:
    @staticmethod
    def _install_translations(locale: Locale) -> None:
        """Install translations from ``locale.language`` with gettext.

        Args:
            locale: The current locale object.
        """
        translation(
            "messages",
            localedir=LOCALES_PATH,
            languages=[locale.language],
            fallback=True,
        ).install()

    @staticmethod
    def confirm_with_messagebox(
        *args: Tuple[str], **kwargs: Dict[str, str]
    ) -> bool:
        """Provide confirmations to the user with tkinter messageboxes.

        Args:
            *args: Optional info messages to be included with specific messagebox
                   calls.
            **kwargs: The specific messagebox name, selected by this method's
                      `if` statements.

        Returns:
            Whether the user confirmed/pressed yes on the messagebox or not.
        """
        if "delete_cword_or_word" in kwargs:
            return messagebox.askyesno(
                _("Remove"),
                _("Are you sure you want to delete this")
                + f" {args[0]}? "
                + _("It will be lost forever!"),
            )

        if "confirm_cword_or_word_add" in kwargs:
            return messagebox.askyesno(
                _("Add or select"),
                _("Are you sure you want to add/select a")
                + f" {args[0]}? "
                + _("Your modified fields will be reset!"),
            )

        if "exiting_with_nondefault_fields" in kwargs:
            return messagebox.askyesno(
                _("Back to home"),
                _(
                    "Are you sure you want to go back to the home screen? Your "
                    "modified fields will be reset!"
                ),
            )

        if "importing_with_nondefault_fields" in kwargs:
            return messagebox.askyesno(
                _("Info"),
                _(
                    "Are you sure you want to import crosswords? Your modified "
                    "fields will be reset!"
                ),
            )

        if "exit_" in kwargs and "restart" not in kwargs:
            return messagebox.askyesno(
                _("Restart"), _("Are you sure you want to restart the app?")
            )

        if "exit_" in kwargs and "restart" in kwargs:
            return messagebox.askyesno(
                _("Exit"),
                _(
                    "Are you sure you want to exit the app? If the web app is "
                    "running, it will be terminated."
                ),
            )

        if "close" in kwargs:
            return messagebox.askyesno(
                _("Back to home"),
                _(
                    "Are you sure you want to go back to the home screen? The web "
                    "app will be terminated."
                ),
            )

    @staticmethod
    def show_messagebox(*args: Tuple[str], **kwargs: Dict[str, str]) -> None:
        """Show an error/info messagebox

        Args:
            *args: Optional error messages/details to be included with specific
                   messagebox calls.
            **kwargs: The specific messagebox name, selected by this method's
                      `if` statements.
        """
        if "same_lang" in kwargs:
            return messagebox.showerror(
                _("Error"), _("This language is already selected.")
            )

        if "same_scale" in kwargs:
            return messagebox.showerror(
                _("Error"), _("This size is already selected.")
            )

        if "same_appearance" in kwargs:
            return messagebox.showerror(
                _("Error"), _("This appearance is already selected.")
            )

        if "same_quality" in kwargs:
            return messagebox.showerror(
                _("Error"), _("This quality is already selected.")
            )

        if "crossword_exists_err" in kwargs:
            return messagebox.showerror(
                _("Error"),
                _(
                    "A crossword with this name and difficulty already exists. "
                    "Please choose a new name and/or a new difficulty."
                ),
            )

        if "no_crosswords_to_export_err" in kwargs:
            return messagebox.showerror(
                _("Error"),
                _(
                    "You have no crosswords to export. Please make some and try again."
                ),
            )

        if "export_success" in kwargs:
            return messagebox.showinfo(
                _("Info"), _("Successfully exported your crosswords.")
            )

        if "export_failure" in kwargs:
            return messagebox.showerror(
                _("Error"), _("Your crosswords could not be exported, sorry.")
            )

        if "import_success" in kwargs:
            return messagebox.showinfo(
                _("Info"),
                _("All of your crosswords were successfully imported."),
            )

        if "partial_import_success" in kwargs:
            return messagebox.showinfo(
                _("Info"),
                _("Your import could not be fully completed.")
                + "\n\n"
                + _(
                    "Crosswords with duplicate names and difficulties that were "
                    "not imported: "
                )
                + f"[{', '.join(args[0])}]."
                + "\n\n"
                + _("Invalid crosswords that were not imported: ")
                + f"[{', '.join(args[1])}].",
            )

        if "import_failure" in kwargs:
            return messagebox.showerror(
                _("Error"),
                _(
                    "The specified JSON file is invalid and cannot be processed."
                ),
            )

        if "word_exists_err" in kwargs:
            return messagebox.showerror(
                _("Error"),
                _("This word already exists. Please choose a new word."),
            )

        if "pdf_write_err" in kwargs:
            return messagebox.showerror(
                _("Error"),
                _(
                    "An error occurred while creating your PDF. Please try again."
                ),
            )

        if "pdf_write_success" in kwargs:
            if not args:
                fails_msg = ""
            else:
                disclaimer_str = _(
                    "words that could not be inserted during crossword "
                    "generation will not be included in this PDF, sorry."
                )
                fails_msg = f" {args[0]} {disclaimer_str}"
            return messagebox.showinfo(
                _("Info"),
                _("Successfully wrote PDF.") + fails_msg,
            )

        if "pdf_missing_dep" in kwargs:
            return messagebox.showerror(
                _("Error"),
                _(
                    "You are missing pycairo, which is required to perform this "
                    "operation. Please run"
                )
                + " pip install pycairo "
                + _(
                    "and install the headers for pycairo if you are not on "
                    "Windows using pycairo's Getting Started guide"
                )
                + ": https://pycairo.readthedocs.io/en/latest/getting_started.html",
            )

        if "ipuz_write_success" in kwargs:
            return messagebox.showinfo(_("Info"), _("Successfully wrote ipuz"))

        if "first_time_browser" in kwargs:
            return messagebox.showinfo(
                _("Info"),
                _(
                    "First time launch, please read: Once you have loaded a "
                    "crossword, and wish to load another one, you must first "
                    "terminate the web app. IMPORTANT: If you are on macOS, force "
                    "quitting the application (using cmd+q) while the web app is "
                    "running will prevent it from properly terminating. If you "
                    "mistakenly do this, the program will run new web apps with a "
                    "different port. Alternatively, you can manually change the "
                    "port in the program's config file. All app processes that "
                    "have not been properly terminated can be terminated through "
                    "Activity Monitor on MacOS, or, simply restart your computer "
                    "to terminate them."
                ),
            )

        if "cword_or_def_err" in kwargs:
            return messagebox.showerror(_("Error"), f"{args[0]}({args[1]})")

        if "other_gen_err" in kwargs:
            return messagebox.showerror(
                _("Error"),
                f"{args[0]}({args[1]}) - "
                + _(
                    "An unexpected error occured. Please try reinstalling the "
                    "application with"
                )
                + " pip install --force-reinstall xpuz",
            )


class BlockUtils:
    """Methods to help with manipulating block objects in both ``pages/editor.py``
    and ``pages/browser.py``.
    """

    @staticmethod
    def _match_block_query(query: str, block_name: str, category: str) -> bool:
        """Return True if any part of ``block_name`` (split into the words that
        it consists of) starts with ``query``, or if ``category`` starts with
        ``query``. All comparisons are caseless and do not regard whitespace
        (except the category, which keeps its whitespace).

        Args:
            query: A query entered by the user.
            block_name: The current block name that is being queried.
            category: The category of the current block name that is being queried.

        Returns:
            Whether the query was found in the category or block name, or not.
        """
        formatted_query = query.strip().casefold()
        return any(
            block_name_segment.strip().casefold().startswith(formatted_query)
            for block_name_segment in block_name.split(" ")
        ) or category.casefold().startswith(formatted_query)

    @classmethod
    def _put_block(cls, block: CTkFrame, side: str = "left") -> None:
        """Pack ``block`` in its parent container and append it to the available
        blocks in ``cls``.

        Args:
            block: The block instance to be packed.
            side: The side to pack the block. `"top"` for the crossword editor
                  panes, and `"left"` for the crossword browser container.
        """
        block.pack(side=side, padx=5, pady=(5, 0))
        cls.blocks.append(block)

    @classmethod
    def _remove_block(cls, block: CTkFrame) -> None:
        """Remove ``block`` from its parent container and the available blocks
        in ``cls``.

        Args:
            block: The block to remove.
        """
        block.pack_forget()
        cls.blocks.remove(block)

    @classmethod
    def _set_all(
        cls,
        func: Callable,
    ) -> None:
        """Call ``func``, passing each block in ``cls.blocks`` as parameters.
        Most often used to put or remove all of the blocks in ``cls.blocks``.

        Args:
            func: The function to perform on the block.
        """
        for block in [
            *cls.blocks
        ]:  # Must iterate over a shallow copy here, as
            # you cannot modify an array you iterate
            # over (with ``func``)
            func(block)

    @classmethod
    def _config_selectors(cls, **kwargs: Dict[str, Any]) -> None:
        """Enable or disable all the radiobutton selectors in ``cls.blocks``.

        Args:
            **kwargs: Configuration parameters.
        """
        for block in cls.blocks:
            block.rb_selector.configure(**kwargs)


def _open_file(fp: PathLike) -> None:
    """Open ``fp`` (directory) in the OS' default file explorer.

    Args:
        fp: The filepath to open.
    """
    plat: str = system()
    if plat == "Windows":
        from os import startfile

        startfile(fp)
    else:
        from os import system as os_system

        if plat == "Darwin":
            os_system("open %s" % fp)
        elif plat == "Linux":
            os_system("xdg-open %s" % fp)


def _get_saveas_filename(
    title: str, name: str, extension: str, filetypes: List[Tuple[str]]
) -> Union[str, PathLike]:
    """Get user input for a file save location.

    Args:
        title: The file explorer's titlebar text.
        name: The default file name.
        extension: The file extension.
        filetypes: Available filetypes to save the file as.
    """
    return filedialog.asksaveasfilename(
        title=title,
        defaultextension=extension,
        filetypes=filetypes,
        initialfile=name + extension,
        initialdir=user_downloads_dir(),
    )


def _get_open_filename(
    title: str, filetypes: List[Tuple[str]]
) -> Union[str, PathLike]:
    """Get user input for the location to a file that is to be opened.

    Args:
        title: The file explorer's titlebar text.
        filetypes: Available filetypes to display.
    """
    return filedialog.askopenfilename(
        title=title,
        initialdir=user_downloads_dir(),
        filetypes=filetypes,
    )


def _get_english_string(
    eng_arr: List[str], localised_arr: List[str], index_value: Union[str, int]
) -> str:
    """Find the english version of ``index_value`` by finding its index in
    ``localised_arr``, then using the resulting integer to index ``eng_arr``.
    This function assumes both arrays have the same relative order.

    Args:
        eng_arr: The default english values.
        localised_arr: The localised values.
        index_value: The position of the localised string within `localised_arr`.

    Returns:
        The english string that was indexed.
    """
    return eng_arr[localised_arr.index(index_value)]


def _check_version() -> Union[None, str]:
    """Find latest remote GitHub release if it is higher than the local
    release using the ``urllib`` module.

    Returns:
        The latest release, if it was found. Otherwise, returns `None`.
    """
    try:
        request = req.Request(RELEASE_API_URL)
        response = req.urlopen(request)
    except URLError:  # URL doesn't exist
        return None

    if response.status == 200:  # Request success
        data = loads(response.read().decode())
        local_ver = __version__.split(".")
        remote_ver = data["name"].split(".")

        # Any component of the remote semver'd tag is greater than that of the
        # local tag (MAJOR or MINOR or PATCH), meaning a new version has been
        # made, so, return the remote version.
        if any(
            int(item[0]) > int(item[1])
            for item in list(zip(remote_ver, local_ver))
        ):
            return data["name"]

    return None  # ``response.status`` wasn't 200, meaning some error occurred.


def _doc_data_routine(
    doc_callback: Optional[Callable] = None,
    local_callback: Optional[Callable] = None,
    toplevel: PathLike = DOC_PATH,
    datalevel: PathLike = DOC_DATA_PATH,
    sublevel: PathLike = DOC_CFG_PATH,
) -> bool:
    """Scan through both the package and system document directories, making
    the required folders if needed.

    Args:
        doc_callback: A function to execute if possible when scanning the system's
                      document directory to make missing files.
        local_callback: A function to execute if possible when scanning the
                        local data of the `xpuz` package to make missing files.
        toplevel: The path of the system's document directory.
        datalevel: The path to the data files within `toplevel`
        sublevel: The path to `config.ini` within `toplevel`.

    Returns:
        Whether the document data has been successfully made or not.
    """
    if not path.exists(toplevel):
        # No documents folder available. The caller might have added a func to
        # run if this happens, which will make the required folder in the package
        if local_callback:
            try:
                local_callback()  # Attempt to make the required package files
            except OSError:
                pass
        return False  # Cannot continue, as Documents do not exist

    # If the code reached this point, it means a Documents folder must exist
    if not path.exists(datalevel):  # Attempt to make the ``xpuz`` dir in Documents
        mkdir(DOC_DATA_PATH)

    if not path.exists(sublevel):  # The required sub-directory doesn't exist 
                                   # yet in Documents
        if doc_callback:
            try:
                doc_callback()  # Attempt to make the required sub-directory
                                # eg ``xpuz/user`` for user crosswords
            except OSError:
                pass

    return True  # Success, as the doc data has been made


def _check_doc_cfg_is_up_to_date() -> bool:
    """Check if the all the sections (and values of those sections) are present
    in the document config.ini file.

    Returns:
        Whether the config.ini in the system's documents directory is up-to-date
        or not.
    """
    template_cfg, doc_cfg = ConfigParser(), ConfigParser()
    template_cfg.read(TEMPLATE_CFG_PATH)
    doc_cfg.read(DOC_CFG_PATH)
    for section in template_cfg:
        if section != "DEFAULT":  # Ignore this, all keys are sectioned
            template_items = template_cfg.items(section)
            try:  # Missing section, can immediately return False
                doc_items = doc_cfg.items(section)
            except NoSectionError:
                return False
            for (
                item
            ) in template_items:  # Iterate through all template section items
                if any(  # template_item[0] or item[0] refers to the key here
                    template_item[0] not in [item[0] for item in doc_items]
                    for template_item in template_items
                ):  # This means not all sections are identical
                    return False

    return (
        True  # All checks passed, tell the caller not to update the config.ini
    )


def _make_doc_cfg() -> None:
    """Write the contents of ``template.config.ini`` into ``config.ini``, located
    in the system's document directory.
    """
    with open(TEMPLATE_CFG_PATH) as template_cfg, open(
        path.join(DOC_CFG_PATH), "w"
    ) as dest_cfg:
        dest_cfg.write(template_cfg.read())


def _update_cfg(
    cfg: ConfigParser, section: str, option: str, value: str
) -> None:
    """Update ``cfg`` at the given section, option and value, then write it
    to an available config path.

    Args:
        section: The section to update.
        option: The option to update.
        value: The value to write to `cfg[section][option]`.
    """
    cfg[section][option] = value

    fp = (
        TEMPLATE_CFG_PATH
        # If ``_doc_data_routine`` returned False, we must use the package
        # config, as the Document config doesn't exist.
        if not _doc_data_routine(doc_callback=_make_doc_cfg)
        else DOC_CFG_PATH
    )

    with open(fp, "w") as f:
        cfg.write(f)


def _read_cfg(cfg: ConfigParser) -> None:
    """Determine which config file to access (whether it is
    ``template.config.ini`` in the package or ``config.ini`` in the system
    documents directory), and write its contents to ``cfg``.

    Args:
        cfg: The config parser instance.
    """
    # Documents directory unavailable
    if not _doc_data_routine(doc_callback=_make_doc_cfg):
        return cfg.read(TEMPLATE_CFG_PATH)
    else:
        if not _check_doc_cfg_is_up_to_date():
            _make_doc_cfg()
        return cfg.read(DOC_CFG_PATH)


def _get_base_categories() -> Iterable[DirEntry]:
    """Get all the available crossword categories sorted alphabetically.

    Returns:
        All the directory entries to the available crossword categories. They
        can be sourced from both the package and the system's data.
    """
    if _doc_data_routine() and "user" in listdir(DOC_DATA_PATH):
        # It is safe to say the user category is in the Document data, so
        # retrieve all package categories except for the user category
        scanned_cats = [
            cat
            for cat in scandir(BASE_CWORDS_PATH)
            if cat.is_dir() and cat.name != "user"
        ]
        # Add on the user category direntry from the document data
        scanned_cats += [cat for cat in scandir(DOC_DATA_PATH) if cat.is_dir()]

    else:  # Retrieve ALL categories from the package data
        scanned_cats = [
            cat for cat in scandir(BASE_CWORDS_PATH) if cat.is_dir()
        ]

    return sorted(
        scanned_cats, key=lambda cat: cat.name if cat.name != "user" else "!"
    )


def _sort_crosswords_by_suffix(
    cwords: Union[List[DirEntry], List[Tuple[DirEntry, DirEntry]]],
) -> Union[List[DirEntry], List[Tuple[DirEntry, DirEntry]]]:
    """Sort an iterable container with crossword directory entries based on
    the crossword's suffix (from -easy to -extreme, if possible).

    Args:
        cwords: A list of directory entries of crosswords, or an array of
                tuples with lists of both category entries **and** crossword
                entries, if sorting all available crosswords.

    Returns:
        The unsorted crosswords if any one of them is missing a suffix, or the
        sorted crosswords in the same structure they were passed to the function.
    """
    try:
        return sorted(
            cwords,
            key=lambda cword: DIFFICULTIES.index(
                cword.name.split("-")[-1].capitalize()
                if not isinstance(cwords[0], tuple)
                # Handling an array of tuples, where tup[1] is the crossword name
                else cword[1].name.split("-")[-1].capitalize()
            ),
        )
    except ValueError:  # Don't sort ("-<difficulty>" suffix wasn't found)
        return cwords


def _get_base_crosswords(
    category: Union[DirEntry, PathLike],
    sort: bool = True,
    allow_empty_defs: bool = False,
) -> Iterable[DirEntry]:
    """Get all the available crosswords from the base crossword directory if
    they have valid ``definitions.json`` files.

    Args:
        category: The path/directory entry to the category.
        sort: Whether to sort the obtained crosswords or not.
        allow_empty_defs: Consider a crossword with no definitions to be valid
                          if it is user made.

    Returns:
        The acquired crosswords, sorted or unsorted, based on if any errors
        occurred during the sorting process.
    """
    fp: PathLike = getattr(category, "path", category)
    # Actual path can either be ``fp`` or the document category path if the requested
    # category is user and it is present in the system document data
    actual_path: PathLike = (
        DOC_CAT_PATH
        if _doc_data_routine()
        and "user" in listdir(DOC_DATA_PATH)
        and fp.endswith("user")
        else fp
    )
    crosswords = [
        cword
        for cword in scandir(actual_path)
        if cword.is_dir()
        and "definitions.json" in listdir(cword.path)
        and path.getsize(path.join(cword.path, "definitions.json")) > 0
        or (allow_empty_defs and category.endswith("user") and cword.is_dir())
    ]
    return _sort_crosswords_by_suffix(crosswords) if sort else crosswords


def _make_cword_info_json(
    fp: PathLike, cword_name: str, category: str
) -> None:
    """Make an info.json file for a given crossword, since it doesn't exist.
    Infer any required information that is not passed by the caller.

    Args:
        fp: The path to write the info to.
        cword_name: The name of the crossword.
        category: The crossword's category.
    """

    with open(path.join(fp, "info.json"), "w") as info_obj, open(
        path.join(fp, "definitions.json"), "r"
    ) as def_obj:
        total_definitions: int = len(load(def_obj))

        # Infer the difficulty and crossword name if possible
        try:
            parsed_cword_name_components: List[str] = path.basename(fp).split(
                "-"
            )
            difficulty: int = DIFFICULTIES.index(
                parsed_cword_name_components[-1].title()
            )
            adjusted_cword_name: str = " ".join(
                parsed_cword_name_components[0:-1]
            ).title()
        except Exception:
            difficulty: int = 0
            adjusted_cword_name: str = cword_name

        return dump(
            CrosswordInfo(
                total_definitions=total_definitions,
                difficulty=difficulty,
                symbol="0x2717",
                name=adjusted_cword_name,
                translated_name="",
                category=category,
            ),
            info_obj,
            indent=4,
        )


def _update_cword_info_word_count(
    fp: PathLike, info: CrosswordInfo, total_definitions: int
) -> None:
    """Update the word count in a crossword's `info.json` file if it is
    inconsistent with the amount of key-pair values in its `definitions.json`
    file.

    Args:
        fp: The toplevel of the crossword.
        info: The existing info of the crossword.
        total_definitions: The `"definitions"` key as defined in `info`.
    """
    with open(path.join(fp, "info.json"), "w") as f:
        info["total_definitions"]: int = total_definitions
        return dump(info, f, indent=4)


def _make_category_info_json(fp: PathLike, hex_: str = None) -> None:
    """Write a new info.json to a category since it does not exist in the a
    category's directory.

    Args:
        fp: The path to write the category's `info.json` file to.
        hex_: A hexadecimal colour value stored in a string, which represents
              the colour of the category's bottom tag colour.
    """
    if not hex_:
        hex_: str = "#%06X" % randint(0, 0xFFFFFF)
    with open(path.join(fp, "info.json"), "w") as f:
        return dump({"bottom_tag_colour": hex_}, f, indent=4)


def _load_attempts_db() -> Dict[str, int]:
    """Load ``attempts_db.json``, which specifies how many generation attempts
    should be conducted for a crossword based on its word count. This is
    integral to the crossword optimisation process, as crossword generation
    time scales logarithmically with word count.

    Returns:
        The attempts dictionary.
    """

    with open(ATTEMPTS_DB_PATH) as file:
        return load(file)


def _get_language_options() -> Tuple[Dict[str, str], List[str]]:
    """Gather a dictionary that maps each localised language name to its
    english acronym, and a list that contains all of the localised language
    names. This data is derived from ``LOCALES_PATH``.

    Returns:
        The localised language dictionary and the localised languages list.
    """
    localised_lang_db: Dict[str, str] = {}  # Used to retrieve the language
    # code for the selected language
    # e.x. {"አማርኛ": "am",}
    localised_langs: List[str] = []  # Used in the language selection
    # optionmenu
    # e.x. ["አማርኛ", "عربي"]

    i: int = 0
    for locale in sorted(
        [
            f.name
            for f in scandir(LOCALES_PATH)
            if f.is_dir() and "LC_MESSAGES" in listdir(f.path)
        ]
    ):
        try:
            localised_langs.append(Locale.parse(locale).language_name)
            localised_lang_db[localised_langs[i]] = locale
            i += 1
        except UnknownLocaleError:
            pass

    return [localised_lang_db, localised_langs]


def _get_colour_palette(
    appearance_mode: Union[
        Literal["Light"], Literal["Dark"], Literal["System"]
    ],
) -> Dict[str, str]:
    """Create a dictionary based on ``constants.Colour`` for the web app.

    Args:
        appearance_mode: The current tkinter appearance mode.

    Returns:
        A colour code dictionary.
    """
    sub_class = Colour.Light if appearance_mode == "Light" else Colour.Dark
    return {
        key: value
        for attr in [sub_class.__dict__, Colour.Global.__dict__]
        for key, value in attr.items()
        if key[0] != "_" or key.startswith("BUTTON")
    }


def _find_best_crossword(
    crossword: "Crossword", cls: "Crossword"
) -> "Crossword":
    """Determine the best crossword out of a amount of instantiated
    crosswords based on the largest amount of total intersections and
    smallest amount of fails.

    Args:
        crossword: The `Crossword` instance to perform the optimised creation on.
        cls: The `Crossword` class.

    Returns:
        The best `Crossword` instance that was found.
    """
    cfg: ConfigParser = ConfigParser()
    _read_cfg(cfg)
    name: str = crossword.name
    word_count: int = crossword.word_count

    attempts_db: Dict[str, int] = _load_attempts_db()
    try:
        max_attempts: int = attempts_db[str(word_count)]  # Get amount of attempts 
                                                          # based on word count
        max_attempts *= (
            QUALITY_MAP[  # Scale max attempts based on crossword quality
                cfg.get("m", "cword_quality")
            ]
        )
        max_attempts = int(ceil(max_attempts))
    except KeyError:  # Fallback to only a single generation attempt
        max_attempts = 1
    attempts: int = 0  # Track current amount of attempts
    dimensions_incremented = False

    definitions: Dict[str, str] = crossword.definitions
    dimensions: int = crossword.dimensions
    crossword.generate()
    best_crossword = (
        crossword  # Assume the best crossword is the first crossword
    )

    while attempts <= max_attempts:
        # Set ``via_find_best_crossword`` to True so dimensions are not
        # recalculated and new definitions are not sampled; only the existing
        # ones are randomised
        crossword = cls(
            name=name,
            definitions=definitions,
            word_count=word_count,
            via_find_best_crossword=True,
            dimensions=dimensions,
        )
        crossword.generate()

        # Update the new best crossword if it has more intersections than
        # the current crossword and its fails are less than or equal to the
        # current crossword's fails. Changing the fails comparison to simply
        # "less than" is too strict and results in a poor "best" crossword.
        if crossword.total_intersections > best_crossword.total_intersections:
            if crossword.fails <= best_crossword.fails:
                best_crossword = crossword

        # Increment the dimensions by 1 if there is a fail present in the current
        # crossword to minimise the chance another fail happens in the remaining
        # crosswords.
        if not dimensions_incremented and crossword.fails > 0:
            dimensions += 1
            dimensions_incremented = True

        attempts += 1

    assert best_crossword.generated
    return best_crossword


def _interpret_cword_data(
    crossword: "Crossword",
) -> Tuple[List[Tuple[int]], List[Dict[int, Tuple[str]]], List[List[int]]]:
    """Gather data to help with the templated creation of the crossword
    web application.

    Args:
        crossword: The `Crossword` instance to gather data on.

    Returns:
        The interpreted crossword data. Please view the source code below for
        more information.
    """
    starting_word_positions: List[Tuple[int]] = list(crossword.data.keys())
    # e.x. [(1, 2), (4, 6)]

    definitions_a: List[Dict[int, Tuple[str]]] = []
    definitions_d: List[Dict[int, Tuple[str]]] = []
    # e.x. [{1: ("hello", "a standard english greeting")}]"""

    starting_word_matrix: List[List[int]] = deepcopy(crossword.grid)
    # e.x.: [[1, 0, 0, 0], [[0, 0, 2, 0]] ... and so on; Each incremented
    # number is the start of a new word.

    num_label: int = (
        1  # Incremented whenever the start of a word is found;
        # used to create ``starting_word_matrix``.
    )
    for row in range(crossword.dimensions):
        for column in range(crossword.dimensions):
            if (row, column) in starting_word_positions:
                current_cword_data = crossword.data[(row, column)]

                if current_cword_data["direction"] == ACROSS:
                    definitions_a.append(
                        {
                            num_label: (
                                current_cword_data["word"],
                                current_cword_data["definition"],
                            )
                        }
                    )

                elif current_cword_data["direction"] == DOWN:
                    definitions_d.append(
                        {
                            num_label: (
                                current_cword_data["word"],
                                current_cword_data["definition"],
                            )
                        }
                    )

                starting_word_matrix[row][column] = num_label
                num_label += 1

            else:
                if crossword.grid[row][column] == EMPTY:
                    starting_word_matrix[row][column] = None
                else:
                    starting_word_matrix[row][column] = 0

    return (
        starting_word_positions,
        starting_word_matrix,
        definitions_a,
        definitions_d,
    )


def _randomise_definitions(definitions: Dict[str, str]) -> Dict[str, str]:
    """Randomises the existing definitions when attempting reinsertion,
    which prevents ``_find_best_crossword`` from favouring certain word
    groups with intrinsically higher intersections.

    Args:
        definitions: The crossword's definitions.

    Returns:
        The randomised crossword definitions.
    """
    return dict(sample(list(definitions.items()), len(definitions)))


def _verify_definitions(definitions: Dict[str, str], word_count: int) -> None:
    """Process a dictionary of definitions through statements to raise
    errors for particular edge cases in a definitions dictionary. This
    function also uses ``_format_definitions`` to randomly sample a specified
    amount of definitions from the definitions dictionary, then format
    those definitions appropriately.

    Args:
        definitions: The crossword's definitions.
        word_count: The crossword's word count.

    Raises:
        DefinitionsParsingError: If the definitions are invalid. Please view the
                                 source code below for more information.
    """
    # Required error checking
    if not definitions:
        raise DefinitionsParsingError(_("Definitions are empty"))
    if len(definitions) < 3 or word_count < 3:
        raise DefinitionsParsingError(
            _("The word count or definitions are less than 3 in length")
        )
    if len(definitions) < word_count:
        raise DefinitionsParsingError(
            _("Length of the word count is greater than the definitions")
        )
    if any("\\" in word for word in definitions.keys()):
        raise DefinitionsParsingError(_("Escape character present in word"))


def _format_definitions(
    definitions: Dict[str, str], word_count: int
) -> Dict[str, str]:
    """Randomly pick definitions from a larger sample, then prune
    everything except the language characters from the words (the keys of
    the definitions).

    Args:
        definitions: The crossword's definitions.
        word_count: The crossword's word count.

    Returns:
        The formatted crossword definitions.
    """
    # Randomly sample ``word_count`` amount of definitions
    randomly_sampled_definitions = dict(
        sample(list(definitions.items()), word_count)
    )

    # Remove all non language chars from the keys of
    # ``randomly_sampled_definitions``` (the words) and capitalise its values
    # (the clues/definitions)
    formatted_definitions = {
        sub(NONLANGUAGE_PATTERN, "", k).upper(): v
        for k, v in randomly_sampled_definitions.items()
    }

    return formatted_definitions
