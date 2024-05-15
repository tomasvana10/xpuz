"""Main module for crossword_puzzle that creates a GUI for the user to generate
a customisable crossword, as well as provides the ability to view it in a Flask
web application.
"""

from configparser import ConfigParser
from copy import deepcopy
from gettext import translation
from json import dumps, load
from os import listdir, path, scandir
from platform import system
from tkinter import Event, IntVar, messagebox
from typing import Dict, List, Tuple, Union
from webbrowser import open_new_tab

from babel import Locale, numbers
from customtkinter import (
    CTk,
    CTkButton,
    CTkFont,
    CTkFrame,
    CTkImage,
    CTkLabel,
    CTkOptionMenu,
    CTkRadioButton,
    CTkScrollableFrame,
    CTkTextbox,
    get_appearance_mode,
    set_appearance_mode,
    set_default_color_theme,
    set_widget_scaling,
)
from PIL import Image

from crossword_puzzle.constants import (
    BaseEngStrings,
    Colour,
    CrosswordDifficulties,
    CrosswordDirection,
    CrosswordStyle,
    Paths,
)
from crossword_puzzle.cword_gen import Crossword
from crossword_puzzle.cword_webapp.app import _create_app_process, terminate_app
from crossword_puzzle.utils import (
    _get_colour_palette_for_webapp,
    _get_language_options,
    _load_cword_info,
    _make_category_info_json,
    _make_cword_info_json,
    _update_config,
    find_best_crossword,
    load_definitions,
)


class Home(CTk):
    """Class that serves as a homescreen for the program, providing global
    setting configuration, exit functionality and the ability to view the
    currently available crossword puzzles.
    """

    def __init__(
        self,
        lang_info: List[Union[Dict[str, str], List[str]]],
        locale: Locale,
        cfg: ConfigParser,
    ) -> None:
        super().__init__()
        self.locale: Locale = (
            locale  # Provides localisation data to the module
        )
        self.cfg: ConfigParser = cfg  # Read from ``config.ini``

        self.localised_lang_db, self.localised_langs = lang_info
        self.protocol("WM_DELETE_WINDOW", self._exit_handler)  # Detect window
                                                               # deletion
        self.title(_("Crossword Puzzle"))
        self.geometry("840x600")
        # Only set the program icon if the user is on Windows
        if system() == "Windows":
            self.iconbitmap(Paths.LOGO_PATH)

        set_appearance_mode(self.cfg.get("m", "appearance"))
        set_default_color_theme(self.cfg.get("m", "theme"))
        set_widget_scaling(float(self.cfg.get("m", "scale")))

        self._make_fonts()
        self.generate_screen()

    def _make_fonts(self) -> None:
        self.TITLE_FONT = CTkFont(size=31, weight="bold", slant="roman")
        self.SUBHEADING_FONT = CTkFont(
            size=24, weight="normal", slant="italic"
        )
        self.TEXT_FONT = CTkFont(size=15, weight="normal", slant="roman")
        self.BOLD_TEXT_FONT = CTkFont(size=15, weight="bold", slant="roman")
        self.CATEGORY_FONT = CTkFont(size=26, weight="bold", slant="roman")
        self.CWORD_BLOCK_FONT = CTkFont(
            size=21, weight="normal", slant="roman"
        )

    def _make_containers(self) -> None:
        self.container = CTkFrame(self)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=0)
        self.container.grid_rowconfigure(0, weight=1)

        self.settings_container = CTkFrame(
            self.container,
            corner_radius=0,
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
        )

        self.cword_opts_container = CTkFrame(
            self.container,
            corner_radius=0,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )

    def _place_containers(self) -> None:
        self.container.pack(fill="both", expand=True)
        self.settings_container.grid(row=0, column=1, sticky="nsew")
        self.cword_opts_container.grid(row=0, column=0, sticky="nsew")

    def _make_content(self) -> None:
        self.l_title = CTkLabel(
            self.cword_opts_container,
            text=_("Crossword Puzzle"),
            font=self.TITLE_FONT,
        )

        self.cword_img = CTkLabel(
            self.cword_opts_container,
            text="",
            image=CTkImage(
                light_image=Image.open(Paths.CWORD_IMG_LIGHT_PATH),
                dark_image=Image.open(Paths.CWORD_IMG_DARK_PATH),
                size=(453, 154),
            ),
        )

        self.b_open_cword_browser = CTkButton(
            self.cword_opts_container,
            text=_("View crosswords"),
            command=self.open_cword_browser,
            width=175,
            height=50,
            font=self.TEXT_FONT,
        )

        self.b_close_app = CTkButton(
            self.cword_opts_container,
            text=_("Exit the app"),
            command=self._exit_handler,
            width=175,
            height=50,
            fg_color=Colour.Global.EXIT_BUTTON,
            hover_color=Colour.Global.EXIT_BUTTON_HOVER,
            font=self.TEXT_FONT,
        )

        self.l_settings = CTkLabel(
            self.settings_container,
            text=_("Global Settings"),
            font=self.SUBHEADING_FONT,
            wraplength=self.settings_container.winfo_reqwidth(),
        )

        self.l_language_opts = CTkLabel(
            self.settings_container,
            text=_("Languages"),
            font=self.BOLD_TEXT_FONT,
        )
        self.opts_language = CTkOptionMenu(
            self.settings_container,
            values=self.localised_langs,
            command=self.switch_lang,
            font=self.TEXT_FONT,
        )
        self.opts_language.set(self.locale.language_name)

        self.l_scale_opts = CTkLabel(
            self.settings_container, text=_("Size"), font=self.BOLD_TEXT_FONT
        )
        self.opts_scale = CTkOptionMenu(
            self.settings_container,
            font=self.TEXT_FONT,
            command=self.change_scale,
            values=[
                numbers.format_decimal(
                    str(round(num * 0.1, 1)), locale=self.locale
                )
                for num in range(7, 16)
            ],
        )
        self.opts_scale.set(
            numbers.format_decimal(
                self.cfg.get("m", "scale"), locale=self.locale
            )
        )

        self.appearances: List[str] = [_("light"), _("dark"), _("system")]
        self.l_appearance_opts = CTkLabel(
            self.settings_container,
            text=_("Appearance"),
            bg_color="transparent",
            font=self.BOLD_TEXT_FONT,
        )
        self.opts_appearance = CTkOptionMenu(
            self.settings_container,
            values=self.appearances,
            command=self.change_appearance,
            font=self.TEXT_FONT,
        )
        self.opts_appearance.set(_(self.cfg.get("m", "appearance")))

        self.l_appearance_opts = CTkLabel(
            self.settings_container,
            text=_("Appearance"),
            bg_color="transparent",
            font=self.BOLD_TEXT_FONT,
        )

        self.cword_qualities: List[str] = [
            _("terrible"),
            _("poor"),
            _("average"),
            _("great"),
            _("perfect"),
        ]
        self.l_cword_quality = CTkLabel(
            self.settings_container,
            text=_("Crossword Quality"),
            bg_color="transparent",
            font=self.BOLD_TEXT_FONT,
        )
        self.opts_cword_quality = CTkOptionMenu(
            self.settings_container,
            values=self.cword_qualities,
            command=self.change_crossword_quality,
            font=self.TEXT_FONT,
        )
        self.opts_cword_quality.set(_(self.cfg.get("misc", "cword_quality")))

    def _place_content(self) -> None:
        self.l_title.place(relx=0.5, rely=0.1, anchor="c")
        self.cword_img.place(relx=0.5, rely=0.35, anchor="c")
        self.b_open_cword_browser.place(relx=0.5, rely=0.65, anchor="c")
        self.b_close_app.place(relx=0.5, rely=0.76, anchor="c")
        self.l_settings.place(relx=0.5, rely=0.1, anchor="c")
        self.l_language_opts.place(relx=0.5, rely=0.21, anchor="c")
        self.opts_language.place(relx=0.5, rely=0.27, anchor="c")
        self.l_scale_opts.place(relx=0.5, rely=0.41, anchor="c")
        self.opts_scale.place(relx=0.5, rely=0.47, anchor="c")
        self.l_appearance_opts.place(relx=0.5, rely=0.61, anchor="c")
        self.opts_appearance.place(relx=0.5, rely=0.67, anchor="c")
        self.l_cword_quality.place(relx=0.5, rely=0.81, anchor="c")
        self.opts_cword_quality.place(relx=0.5, rely=0.87, anchor="c")

    def open_cword_browser(self) -> None:
        """Remove all homescreen widgets and instantiate the ``CrosswordBrowser``
        class.
        """
        self.container.pack_forget()
        self.title(_("Crossword Browser"))
        self.cword_browser: object = CrosswordBrowser(self)

    def close_cword_browser(self) -> None:
        """Remove all ``CrosswordBrowser`` widgets and regenerate the main
        screen.
        """
        self.cword_browser.pack_forget()
        self.title(_("Crossword Puzzle"))
        self.generate_screen()

    def generate_screen(self, inst=None) -> None:
        """Run the methods to create the containers and content for an instance."""
        instance = self if not inst else inst
        instance._make_containers()
        instance._place_containers()
        instance._make_content()
        instance._place_content()

    def _exit_handler(
        self, restart: bool = False, webapp_running: bool = False
    ) -> None:
        """Called when the event "WM_DELETE_WINDOW" occurs or when the the
        program must be restarted, in which case the ``restart`` default
        parameter is overridden.
        """
        # If user wants to exit/restart
        if AppHelper.confirm_with_messagebox(exit_=True, restart=restart):
            terminate_app()
            self.quit()

        if restart:  # Additionally perform a restart
            AppHelper.start_app()

    def change_appearance(self, appearance: str) -> None:
        """Ensures the user is not selecting the same appearance, then sets
        the appearance. Some list indexing is required to make the program
        compatible with non-english languages.
        """
        # Must be done because you cannot do ``set_appearance_mode("نظام")``,
        # for example
        eng_appearance_name: str = BaseEngStrings.BASE_ENG_APPEARANCES[
            self.appearances.index(appearance)
        ]
        if eng_appearance_name == self.cfg.get("m", "appearance"):
            return AppHelper.show_messagebox(same_appearance=True)

        set_appearance_mode(eng_appearance_name)
        _update_config(self.cfg, "m", "appearance", eng_appearance_name)

    def change_scale(self, scale: str) -> None:
        """Ensures the user is not selecting the same scale, then sets the scale."""
        scale = float(numbers.parse_decimal(scale, locale=self.locale))
        if scale == float(self.cfg.get("m", "scale")):
            return AppHelper.show_messagebox(same_scale=True)

        set_widget_scaling(scale)
        _update_config(self.cfg, "m", "scale", str(scale))

    def switch_lang(self, lang: str) -> None:
        """Ensures the user is not selecting the same language, then creates a
        new ``locale`` variable based on the English name of the language
        (retrieved from ``self.localised_lang_db``). The method then installs a
        new set of translations with gettext and regenerates the content of the
        GUI.
        """
        if self.localised_lang_db[lang] == self.cfg.get("m", "language"):
            return AppHelper.show_messagebox(same_lang=True)

        self.locale: Locale = Locale.parse(self.localised_lang_db[lang])
        translation(
            "messages",
            localedir=Paths.LOCALES_PATH,
            languages=[self.locale.language],
        ).install()
        _update_config(self.cfg, "m", "language", self.localised_lang_db[lang])
        self.title(_("Crossword Puzzle"))
        self.container.pack_forget()
        self.generate_screen()

    def change_crossword_quality(self, quality: str) -> None:
        """Ensures the user is not selecting the same crossword quality, then
        updates the crossword quality in ``config.ini``.
        """
        eng_quality_name: str = BaseEngStrings.BASE_ENG_CWORD_QUALITIES[
            self.cword_qualities.index(quality)
        ]
        if eng_quality_name == self.cfg.get("misc", "cword_quality"):
            return AppHelper.show_messagebox(same_quality=True)

        _update_config(self.cfg, "misc", "cword_quality", eng_quality_name)


class CrosswordBrowser(CTkFrame):
    """Provides an interface to view available crosswords, set a preference for
    the word count, generate a crossword (using ``cword_gen``) based on the
    selected parameters, and launch the crossword webapp to complete the
    generated crossword.
    """

    def __init__(self, master: Home) -> None:
        super().__init__(
            master, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.master = master

        self.pack(expand=True, fill="both")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.cword_launch_options_enabled: bool = False
        self.webapp_running: bool = False
        self.word_count_preference = IntVar()
        self.word_count_preference.set(-1)

        self.master.generate_screen(inst=self)
        self._generate_crossword_category_blocks()

        if self.master.cfg.get("misc", "cword_browser_opened") == "0":
            AppHelper.show_messagebox(first_time_opening_cword_browser=True)
            _update_config(
                self.master.cfg, "misc", "cword_browser_opened", "1"
            )

    def _make_containers(self) -> None:
        self.center_container = CTkFrame(self)

        self.info_block_container = CTkScrollableFrame(
            self.center_container,
            orientation="horizontal",
            corner_radius=0,
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            scrollbar_button_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.info_block_container.bind_all("<MouseWheel>", self._handle_scroll)

        self.button_container = CTkFrame(
            self, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )

        self.preference_container = CTkFrame(
            self, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.preference_container.grid_columnconfigure((0, 1), weight=0)

    def _place_containers(self) -> None:
        self.center_container.pack(anchor="c", expand=True, fill="x")
        self.info_block_container.pack(expand=True, fill="both")
        self.button_container.place(relx=0.725, rely=0.84, anchor="c")
        self.preference_container.place(relx=0.3, rely=0.84, anchor="c")

    def _make_content(self) -> None:
        self.l_title = CTkLabel(
            self, text=_("Crossword Browser"), font=self.master.TITLE_FONT
        )

        self.b_go_to_home = CTkButton(
            self,
            text=_("Go back"),
            command=self.go_to_home,
            width=175,
            height=50,
            fg_color=Colour.Global.EXIT_BUTTON,
            hover_color=Colour.Global.EXIT_BUTTON_HOVER,
            font=self.master.TEXT_FONT,
        )

        self.b_load_selected_cword = CTkButton(
            self.button_container,
            text=_("Load crossword"),
            height=50,
            command=self.load_selected_cword,
            state="disabled",
            font=self.master.TEXT_FONT,
        )

        self.b_open_cword_webapp = CTkButton(
            self.button_container,
            text=_("Open web app"),
            height=50,
            command=self.open_cword_webapp,
            state="disabled",
            font=self.master.TEXT_FONT,
        )

        self.b_terminate_cword_webapp = CTkButton(
            self.button_container,
            text=_("Terminate web app"),
            height=50,
            command=self.terminate_cword_webapp,
            fg_color=Colour.Global.EXIT_BUTTON,
            hover_color=Colour.Global.EXIT_BUTTON_HOVER,
            state="disabled",
            font=self.master.TEXT_FONT,
        )

        self.l_word_count_preferences = CTkLabel(
            self.preference_container,
            text=_("Word count preferences"),
            state="disabled",
            font=self.master.BOLD_TEXT_FONT,
            text_color_disabled=(
                Colour.Light.TEXT_DISABLED,
                Colour.Dark.TEXT_DISABLED,
            ),
        )

        self.opts_custom_word_count = CTkOptionMenu(
            self.preference_container,
            state="disabled",
            font=self.master.TEXT_FONT,
        )
        self.opts_custom_word_count.set(_("Select word count"))

        self.rb_max_word_count = CTkRadioButton(
            self.preference_container,
            text=f"{_('Maximum')}: ",
            variable=self.word_count_preference,
            value=0,
            state="disabled",
            corner_radius=1,
            command=lambda: self._on_word_count_rb_selection("max"),
            font=self.master.TEXT_FONT,
        )

        self.rb_custom_word_count = CTkRadioButton(
            self.preference_container,
            text=_("Custom"),
            variable=self.word_count_preference,
            value=1,
            state="disabled",
            corner_radius=1,
            command=lambda: self._on_word_count_rb_selection("custom"),
            font=self.master.TEXT_FONT,
        )

    def _place_content(self) -> None:
        self.l_title.place(relx=0.5, rely=0.1, anchor="c")
        self.b_go_to_home.place(relx=0.5, rely=0.2, anchor="c")
        self.b_load_selected_cword.grid(
            row=0, column=0, sticky="nsew", padx=7, pady=7
        )
        self.b_open_cword_webapp.grid(
            row=0, column=1, sticky="nsew", padx=7, pady=7
        )
        self.b_terminate_cword_webapp.grid(
            row=1, column=0, columnspan=2, sticky="nsew", padx=77.5, pady=7
        )
        self.l_word_count_preferences.grid(
            row=0, column=0, columnspan=2, pady=(5, 10)
        )
        self.rb_max_word_count.grid(row=1, column=0, padx=7, pady=7)
        self.rb_custom_word_count.grid(row=2, column=0, padx=7, pady=7)
        self.opts_custom_word_count.grid(row=3, column=0, padx=7, pady=7)

    def _handle_scroll(self, event: Event) -> None:
        """Scroll the center scroll frame only if the viewable width is greater
        than the scroll region. This prevents weird scroll behaviour in cases
        where the above condition is inverted.
        """
        scroll_region = self.info_block_container._parent_canvas.cget(
            "scrollregion"
        )
        viewable_width = self.info_block_container._parent_canvas.winfo_width()
        if scroll_region and int(scroll_region.split(" ")[2]) > viewable_width:
            # -1 * event.delta emulates a "natural" scrolling motion
            self.info_block_container._parent_canvas.xview(
                "scroll", -1 * event.delta, "units"
            )

    def _on_word_count_rb_selection(self, button_name: str) -> None:
        """Configure custom word count optionmenu based on radiobutton selection."""
        if button_name == "max":  # User wants max word count, don't let them
                                  # select custom word count.
            self.opts_custom_word_count.set(_("Select word count"))
            self.opts_custom_word_count.configure(state="disabled")
        else:  # User wants custom word count, don't let them select max word count.
            self.opts_custom_word_count.set(
                f"{str(numbers.format_decimal(3, locale=self.master.locale))}"
            )
            self.opts_custom_word_count.configure(state="normal")

        if not self.webapp_running:  # Only if they haven't started the web app
            self.b_load_selected_cword.configure(state="normal")

    def open_cword_webapp(self) -> None:
        """Open the crossword web app at a port read from ``self.master.cfg``."""
        self.master.cfg.read(Paths.CONFIG_PATH)
        open_new_tab(
            f"http://127.0.0.1:{self.master.cfg.get('misc', 'webapp_port')}/"
        )

    def terminate_cword_webapp(self) -> None:
        """Appropriately reconfigure the states of the GUIs buttons and terminate
        the app.
        """
        self._rollback_states()
        self.b_open_cword_webapp.configure(
            fg_color=Colour.Global.BUTTON,
            hover_color=Colour.Global.BUTTON_HOVER,
        )
        self.cword_launch_options_enabled: bool = False
        self.webapp_running: bool = False
        terminate_app()

    def _rollback_states(self) -> None:
        # User might not have selected a crossword within their category, so
        # this if condition is requried.
        if hasattr(self, "selected_category_object"):
            self.selected_category_object.b_close_category.configure(
                state="normal"
            )
            self.selected_category_object._configure_cword_blocks_state(
                "normal"
            )

        self.b_terminate_cword_webapp.configure(state="disabled")
        self.b_open_cword_webapp.configure(state="disabled")
        self._configure_cword_launch_options_state("disabled")
        self.rb_max_word_count.configure(text=f"{_('Maximum')}:")
        self.opts_custom_word_count.set(_("Select word count"))
        self.word_count_preference.set(-1)

    def _configure_cword_launch_options_state(self, state_: str) -> None:
        """Configure all the word_count preference widgets to an either an
        interactive or disabled state (interactive when selecting a crossword,
        disabled when a crossword has been loaded).
        """
        self.l_word_count_preferences.configure(state=state_)
        self.rb_max_word_count.configure(state=state_)
        self.rb_custom_word_count.configure(state=state_)
        self.opts_custom_word_count.configure(state=state_)

    def load_selected_cword(self) -> None:
        """Load the selected crossword based on the selected word count option
        (retrieved from the ``word_count_preference`` IntVar). This method then
        loads the definitions based on the current crosswords name, instantiates
        a crossword object, finds the best crossword using
        ``utils.find_best_crossword``, and launches the interactive
        web app via ``init_webapp`` using data retrieved from the crossword
        instance's attributes.

        The crossword information that this function accesses is saved whenever
        a new crossword block is selected (by the ``_on_cword_selection``
        function).
        """
        # Max word count / custom word count
        chosen_word_count: int = (
            self.cword_word_count
            if self.word_count_preference.get() == 0
            else int(self.opts_custom_word_count.get())
        )

        try:
            # Load definitions, instantiate a crossword, then find the best
            # crossword using that instance
            definitions: Dict[str, str] = load_definitions(
                self.cword_category,
                self.cword_name,
                self.master.locale.language,
            )
        except Exception as ex:
            print(f"{type(ex).__name__}: {ex}")
            return AppHelper.show_messagebox(definitions_loading_err=True)

        try:
            crossword: object = find_best_crossword(
                Crossword(
                    definitions=definitions,
                    word_count=chosen_word_count,
                    name=self.cword_name,
                )
            )
        except Exception as ex:
            print(f"{type(ex).__name__}: {ex}")
            return AppHelper.show_messagebox(cword_gen_err=True)

        # Only modify states after error checking has been conducted
        self.b_load_selected_cword.configure(state="disabled")
        self.selected_category_object.b_close_category.configure(
            state="disabled"
        )
        self.selected_category_object._configure_cword_blocks_state("disabled")
        self._configure_cword_launch_options_state("disabled")
        self.selected_category_object.selected_block.set(-1)
        self.webapp_running: bool = True

        self._init_webapp(crossword)

        self.b_open_cword_webapp.configure(
            state="normal",
            fg_color=Colour.Global.GREEN_BUTTON,
            hover_color=Colour.Global.GREEN_BUTTON_HOVER,
        )
        self.b_terminate_cword_webapp.configure(state="normal")

    def _init_webapp(self, crossword: Crossword) -> None:
        """Start the flask web app with information from the crossword and
        other interpreted data.
        """
        self._interpret_cword_data(crossword)
        colour_palette: Dict[str, str] = _get_colour_palette_for_webapp(
            get_appearance_mode()
        )
        _create_app_process(
            locale=self.master.locale,
            scaling=self.master._get_widget_scaling(),
            colour_palette=colour_palette,
            json_colour_palette=dumps(colour_palette),
            cword_data=crossword.data,
            port=self.master.cfg.get("misc", "webapp_port"),
            empty=CrosswordStyle.EMPTY,
            name=self.cword_translated_name,
            category=self.cword_category,
            difficulty=self.cword_difficulty,
            directions=[CrosswordDirection.ACROSS, CrosswordDirection.DOWN],
            # Tuples in intersections must be removed. Changing this in
            # ``cworg_gen.py`` was annoying, so it is done here instead.
            intersections=[
                list(item) if isinstance(item, tuple) else item
                for sublist in crossword.intersections
                for item in sublist
            ],
            word_count=crossword.word_count,
            failed_insertions=crossword.fails,
            dimensions=crossword.dimensions,
            starting_word_positions=self.starting_word_positions,
            starting_word_matrix=self.starting_word_matrix,
            grid=crossword.grid,
            definitions_a=self.definitions_a,
            definitions_d=self.definitions_d,
            js_err_msgs=[
                _("To perform this operation, you must first select a cell.")
            ],
        )

    def _interpret_cword_data(self, crossword: Crossword) -> None:
        """Gather data to help with the templated creation of the crossword
        web application.
        """
        self.starting_word_positions: List[Tuple[int]] = list(
            crossword.data.keys()
        )
        # e.x. [(1, 2), (4, 6)]

        self.definitions_a: List[Dict[int, Tuple[str]]] = []
        self.definitions_d = []
        # e.x. [{1: ("hello", "a standard english greeting")}]"""

        self.starting_word_matrix: List[List[int]] = deepcopy(crossword.grid)
        # e.x.: [[1, 0, 0, 0], [[0, 0, 2, 0]] ... and so on; Each incremented
        # number is the start of a new word.

        num_label: int = (
            1  # Incremented whenever the start of a word is found;  
               # used to create ``starting_word_matrix``.
        )
        for row in range(crossword.dimensions):
            for column in range(crossword.dimensions):
                if (row, column) in self.starting_word_positions:
                    current_cword_data = crossword.data[(row, column)]

                    if (
                        current_cword_data["direction"]
                        == CrosswordDirection.ACROSS
                    ):
                        self.definitions_a.append(
                            {
                                num_label: (
                                    current_cword_data["word"],
                                    current_cword_data["definition"],
                                )
                            }
                        )

                    elif (
                        current_cword_data["direction"]
                        == CrosswordDirection.DOWN
                    ):
                        self.definitions_d.append(
                            {
                                num_label: (
                                    current_cword_data["word"],
                                    current_cword_data["definition"],
                                )
                            }
                        )

                    self.starting_word_matrix[row][column] = num_label
                    num_label += 1

                else:
                    self.starting_word_matrix[row][column] = 0

    def _generate_crossword_category_blocks(self) -> None:
        """Create a variable amount of crossword category blocks based on how
        many categories are present in the base cwords directory.
        """
        self.category_block_objects: List[CrosswordCategoryBlock] = []
        i: int = 0
        for category in [
            f for f in scandir(Paths.BASE_CWORDS_PATH) if f.is_dir()
        ]:
            # Make the ``info.json`` file if it doesn't exist already
            if (
                "info.json" not in listdir(category.path)
                or path.getsize(path.join(category.path, "info.json")) <= 0
            ):
                _make_category_info_json(path.join(category.path, "info.json"))

            block = CrosswordCategoryBlock(
                self.info_block_container, self, category.name, i
            )
            block.pack(side="left", padx=5, pady=(5, 0))
            self.category_block_objects.append(block)
            i += 1

    def _on_cword_selection(
        self,
        name: str,
        translated_name: str,
        difficulty: str,
        word_count: int,
        category: str,
        category_object: object,
        value: int,
    ) -> None:
        """Called by an instance of ``CrosswordInfoBlock``, which passes the
        data for its given crossword into this method. The method then saves
        this data, deselects any previous word count radiobutton selections,
        reconfigures the values of the custom word count optionmenu to be
        compatible with the newly selected crossword, and reconfigures the
        max word count label to show the correct maximum word count.
        """
        if not self.cword_launch_options_enabled:
            self._configure_cword_launch_options_state("normal")
            self.cword_launch_options_enabled: bool = True

        self.b_load_selected_cword.configure(state="disabled")
        self.opts_custom_word_count.configure(state="disabled")
        self.word_count_preference.set(-1)
        self.opts_custom_word_count.set(_("Select word count"))

        # Always save the current crossword's data to be ready for the user to
        # load it
        self.cword_name: str = name
        self.cword_translated_name: str = translated_name
        self.cword_difficulty: str = difficulty
        self.cword_word_count: int = word_count
        self.cword_category: str = category
        self.selected_category_object: object = category_object

        self.opts_custom_word_count.configure(
            values=[
                str(numbers.format_decimal(num, locale=self.master.locale))
                for num in range(3, word_count + 1)
            ]
        )
        self.rb_max_word_count.configure(
            text=f"{_('Maximum')}: "
            f"{numbers.format_decimal(word_count, locale=self.master.locale)}"
        )
        self.rb_max_word_count.invoke()

    def go_to_home(self) -> None:
        """Removes the content of ``CrosswordBrowser`` and regenerates the
        ``Home`` classes content. This must be done outside of this class.
        """
        if self.webapp_running:
            if AppHelper.confirm_with_messagebox(go_to_home=True):
                self.terminate_cword_webapp()
            else:
                return

        self.master.close_cword_browser()


class CrosswordCategoryBlock(CTkFrame):
    """A frame containing the name of a crossword category and a buttons to
    open/close all the crosswords contained within that category. Opening a
    category block will remove all other category blocks and display only the
    crosswords within that category.
    """

    def __init__(
        self,
        container: CTkFrame,
        master: CrosswordBrowser,
        category: str,
        value: int,
    ) -> None:
        super().__init__(
            container,
            corner_radius=10,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            border_color=(Colour.Light.SUB, Colour.Dark.SUB),
            border_width=3,
        )
        self.master = master
        self.category = category
        self.value = value

        # Represents the currently selected crossword radiobutton selector
        # within the crosswords of this category (once open)
        self.selected_block = IntVar()
        self.selected_block.set(-1)

        self._make_content()
        self._place_content()

    def _make_content(self) -> None:
        self.tb_category_name = CTkTextbox(
            self,
            font=self.master.master.CATEGORY_FONT,
            wrap="word",
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            scrollbar_button_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.tb_category_name.tag_config("center", justify="center")
        self.tb_category_name.insert("end", _(self.category.title()), "center")
        self.tb_category_name.configure(state="disabled")

        self.b_view_category = CTkButton(
            self,
            font=self.master.master.TEXT_FONT,
            text=_("View"),
            command=self._view_category,
            width=65,
        )
        self.b_close_category = CTkButton(
            self,
            font=self.master.master.TEXT_FONT,
            text=_("Close"),
            command=self._close_category,
            fg_color=Colour.Global.EXIT_BUTTON,
            hover_color=Colour.Global.EXIT_BUTTON_HOVER,
            width=65,
        )
        self.bottom_colour_tag = CTkLabel(
            self,
            text="",
            fg_color=self._get_colour_tag_hex(),
            corner_radius=10,
        )

    def _place_content(self) -> None:
        self.tb_category_name.place(
            relx=0.5, rely=0.2, anchor="c", relwidth=0.9, relheight=0.231
        )
        self.b_view_category.place(relx=0.5, rely=0.5, anchor="c")
        self.bottom_colour_tag.place(
            relx=0.5, rely=0.895, anchor="c", relwidth=0.75, relheight=0.06
        )

    def _get_colour_tag_hex(self) -> str:
        """Get the hex colour of the bottom tag of this category, read from
        its ``info.json`` file."""
        with open(
            path.join(Paths.BASE_CWORDS_PATH, self.category, "info.json")
        ) as file:
            try:
                return load(file)["bottom_tag_colour"]
            except Exception:
                return "#abcdef"

    def _sort_category_content(self, arr: List[str]) -> List[str]:
        """Sort the cword content of a category by the cword suffixes (-easy
        to -extreme), if possible.
        """
        try:
            return sorted(
                arr,
                key=lambda i: CrosswordDifficulties.DIFFICULTIES.index(
                    i.name.split("-")[-1].capitalize()
                ),
            )
        except Exception:  # Could not find the "-" in the crossword name, so
                           # don't sort this category
            return arr

    def _configure_cword_blocks_state(self, state_: str) -> None:
        """Toggle the crossword info block radiobutton (for selection) to either
        "disabled" or "normal".
        """
        for block in self.cword_block_objects:
            block.rb_selector.configure(state=state_)

    def _view_category(self) -> None:
        """View all crossword info blocks for a specific category."""
        self.b_view_category.configure(state="disabled")
        # Reset crossword canvas xview so it is at the beginning
        self.master.info_block_container._parent_canvas.xview("moveto", 0.0)
        for block in self.master.category_block_objects:  # Remove all category
                                                          # blocks
            block.pack_forget()
        self.selected_block.set(-1)
        self.pack(side="left", padx=5, pady=(5, 0))  # Pack self (the selected
                                                     # category) back in

        # Create the blocks for the crosswords in the selected category
        self.cword_block_objects: List[CrosswordInfoBlock] = []
        # Gather all crossword directories with an info.json file.
        crosswords = [
            f
            for f in scandir(path.join(Paths.BASE_CWORDS_PATH, self.category))
            if f.is_dir()
            and "definitions.json" in listdir(f.path)
            and path.getsize(path.join(f.path, "definitions.json")) > 0
        ]

        i: int = 1
        for cword in self._sort_category_content(crosswords):
            # Make the ``info.json`` file if it doesn't exist already
            info_path = path.join(cword.path, "info.json")
            if not path.exists(info_path) or path.getsize(info_path) <= 0:
                _make_cword_info_json(cword.path, cword.name, self.category)

            block = CrosswordInfoBlock(
                self.master.info_block_container,
                self.master,
                cword.name,
                self.category,
                self,
                i,
            )
            block.pack(side="left", padx=5, pady=(5, 0))
            self.cword_block_objects.append(block)
            i += 1

        self.b_close_category.place(relx=0.5, rely=0.7, anchor="c")

    def _close_category(self) -> None:
        """Remove all crossword info blocks, and regenerate the category blocks."""
        self.b_view_category.configure(state="normal")
        self.b_close_category.place_forget()
        for block in self.cword_block_objects:
            block.pack_forget()
        self.pack_forget()
        self.master._generate_crossword_category_blocks()
        self.master.b_load_selected_cword.configure(state="disabled")
        self.master.terminate_cword_webapp()


class CrosswordInfoBlock(CTkFrame):
    """A frame containing a crosswords name, as well data read from its
    corresponding ``info.json`` file, including total definitions/word count,
    difficulty, and a symbol to prefix the crosswords name. A variable amount
    of these is created based on how many crosswords each category contains.
    """

    def __init__(
        self,
        container: CTkFrame,  # ``CrosswordBrowser.info_block_container``
        master: CrosswordBrowser,
        name: str,
        category: str,
        category_object: CrosswordCategoryBlock,
        value: int,  # Used for ``self.rb_selector``
    ) -> None:
        super().__init__(
            container,
            corner_radius=10,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            border_color=(Colour.Light.SUB, Colour.Dark.SUB),
            border_width=3,
        )
        self.name = name
        self.master = master
        self.category = category
        self.category_object = category_object
        self.value = value
        self.info = _load_cword_info(
            self.category, self.name, self.master.master.locale.language
        )
        self.translated_name = (
            self.info["translated_name"]
            if self.info["translated_name"]
            else self.info["name"]
        )
        self.difficulty = _(
            CrosswordDifficulties.DIFFICULTIES[self.info["difficulty"]]
        )

        self.compiled_data = {
            "name": self.name,
            "translated_name": self.translated_name,
            "difficulty": self.difficulty,
            "word_count": self.info["total_definitions"],
            "category": self.category,
            "category_object": self.category_object,
            "value": self.value,
        }

        self._make_content()
        self._place_content()

    def _make_content(self) -> None:
        self.tb_name = CTkTextbox(
            self,
            font=self.master.master.CWORD_BLOCK_FONT,
            wrap="word",
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            scrollbar_button_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.tb_name.tag_config("center", justify="center")
        self.tb_name.insert(
            "end",
            f"{chr(int(self.info['symbol'], 16))} {self.translated_name}",
            "center",
        )
        self.tb_name.configure(state="disabled")

        self.l_total_words = CTkLabel(
            self,
            font=self.master.master.TEXT_FONT,
            text=f"{_('Total words')}: "
            f"{numbers.format_decimal(self.info['total_definitions'], locale=self.master.master.locale)}",
        )

        self.l_difficulty = CTkLabel(
            self,
            font=self.master.master.TEXT_FONT,
            text=f"{_('Difficulty')}: "
            f"{_(CrosswordDifficulties.DIFFICULTIES[self.info['difficulty']])}",
        )

        self.bottom_colour_tag = CTkLabel(
            self,
            text="",
            fg_color=Colour.Global.DIFFICULTIES[self.info["difficulty"]],
            corner_radius=10,
        )

        self.rb_selector = CTkRadioButton(
            self,
            text=_("Select"),
            corner_radius=1,
            font=self.master.master.TEXT_FONT,
            variable=self.category_object.selected_block,
            value=self.value,
            command=lambda: self.master._on_cword_selection(
                **self.compiled_data
            ),
        )

    def _place_content(self) -> None:
        self.tb_name.place(
            relx=0.5, rely=0.2, anchor="c", relwidth=0.9, relheight=0.198
        )
        self.l_total_words.place(relx=0.5, rely=0.47, anchor="c")
        self.l_difficulty.place(relx=0.5, rely=0.58, anchor="c")
        self.rb_selector.place(relx=0.5, rely=0.76, anchor="c")
        self.bottom_colour_tag.place(
            relx=0.5, rely=0.9, anchor="c", relwidth=0.75, relheight=0.025
        )


class AppHelper:
    @staticmethod
    def start_app() -> None:
        """Install the translations for the language saved in ``config.ini``,
        then instantiate the ``Home`` class with the required parameters.
        """
        cfg = ConfigParser()
        cfg.read(Paths.CONFIG_PATH)

        language: str = cfg.get("m", "language")
        locale: Locale = Locale.parse(language)
        translation(
            "messages",
            localedir=Paths.LOCALES_PATH,
            languages=[locale.language],
        ).install()
        _update_config(
            cfg, "misc", "launches", str(int(cfg.get("misc", "launches")) + 1)
        )

        app = Home(_get_language_options(), locale, cfg)
        app.mainloop()

    @staticmethod
    def confirm_with_messagebox(
        exit_: bool = False, restart: bool = False, go_to_home: bool = False
    ) -> bool:
        """Provide confirmations to the user with tkinter messageboxes."""
        if exit_ and restart:
            if messagebox.askyesno(
                _("Restart"), _("Are you sure you want to restart the app?")
            ):
                return True

        if exit_ and not restart:
            if messagebox.askyesno(
                _("Exit"),
                _(
                    "Are you sure you want to exit the app? If the web app is "
                    "running, it will be terminated."
                ),
            ):
                return True

        if go_to_home:
            if messagebox.askyesno(
                _("Back to home"),
                _(
                    "Are you sure you want to go back to the home screen? The web "
                    "app will be terminated."
                ),
            ):
                return True

        return False

    @staticmethod
    def show_messagebox(
        same_lang: bool = False,
        same_scale: bool = False,
        same_appearance: bool = False,
        same_quality: bool = False,
        first_time_opening_cword_browser: bool = False,
        definitions_loading_err: bool = False,
        cword_gen_err: bool = False,
        unavailable_port: bool = False,
    ) -> None:
        """Show an error/info messagebox."""
        if same_lang:
            return messagebox.showerror(
                _("Error"), _("This language is already selected.")
            )

        if same_scale:
            return messagebox.showerror(
                _("Error"), _("This size is already selected.")
            )

        if same_appearance:
            return messagebox.showerror(
                _("Error"), _("This appearance is already selected.")
            )

        if same_quality:
            return messagebox.showerror(
                _("Error"), _("This quality is already selected.")
            )

        if first_time_opening_cword_browser:
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

        if definitions_loading_err:
            return messagebox.showerror(
                _("Error"),
                _(
                    "An error occured while loading this crossword's definitions. "
                    "Ensure that its definitions JSON file exists in the base "
                    "cwords directory. NOTE: Base crossword data is only accessed "
                    "when its translated version is not present in the locales "
                    "directory."
                ),
            )

        if cword_gen_err:
            return messagebox.showerror(
                _("Error"),
                _(
                    "An error occured in crossword generation. Please see further "
                    "information in the console"
                ),
            )


def start():
    AppHelper.start_app()


if __name__ == "__main__":
    AppHelper.start_app()
