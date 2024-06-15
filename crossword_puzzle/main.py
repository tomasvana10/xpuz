"""Main module for crossword_puzzle that creates a GUI for the user to generate
a customisable crossword, as well as provides the ability to view it in a Flask
web application.
"""

from __future__ import annotations

from configparser import ConfigParser
from gettext import translation
from json import dumps, load
from os import listdir, path, PathLike
from platform import system
from tkinter import Event, IntVar, messagebox
from typing import Dict, List, Union
from uuid import uuid4
from webbrowser import open_new_tab

from babel import Locale, numbers
from PIL import Image

from constants import (
    ACROSS,
    BASE_ENG_APPEARANCES,
    BASE_ENG_CWORD_QUALITIES,
    PAGE_MAP,
    CONFIG_PATH,
    CWORD_IMG_DARK_PATH,
    CWORD_IMG_LIGHT_PATH,
    DOWN,
    EMPTY,
    LOCALES_PATH,
    LOGO_PATH,
    Colour,
)
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
from cword_webapp.app import _create_app, _terminate_app
from utils import (
    BlockUtils,
    _get_base_crosswords,
    _get_colour_palette_for_webapp,
    _get_crossword_categories,
    _get_language_options,
    _interpret_cword_data,
    _make_category_info_json,
    _sort_crosswords_by_suffix,
    _update_config,
)
from wrappers import CrosswordWrapper


class Addons:
    """Convenience and utility methods for all classes."""

    def _set_fonts(self) -> None:
        self.TITLE_FONT = CTkFont(size=31, weight="bold", slant="roman")
        self.SUBHEADING_FONT = CTkFont(size=24, weight="normal", slant="roman")
        self.TEXT_FONT = CTkFont(size=15, weight="normal", slant="roman")
        self.BOLD_TEXT_FONT = CTkFont(size=15, weight="bold", slant="roman")
        self.CATEGORY_FONT = CTkFont(size=23, weight="bold", slant="roman")
        self.CWORD_BLOCK_FONT = CTkFont(
            size=18, weight="normal", slant="roman"
        )

    def _confirm_route(
        self,
        *,
        action: bool = None,
        condition: bool = None,
        confirmation: Dict[str, bool] = {"close": True},
    ) -> bool:
        """Allow the user to confirm if they wish to route through a messagebox."""

        if condition: # A condition is required for this confirmation to happen
            if AppHelper.confirm_with_messagebox(**confirmation):
                if action:
                    action()
                return True  # User agreed to the route
            else:
                return False  # User didn't agree to the route

        return True  # No condition, so just return True

    def _route(
        self,
        page: Union[HomePage, BrowserPage],  # Reference to page instance
        base: Base,  # Reference to base instance
        title: str,  # Title of the new page
        **kwargs,
    ) -> bool:
        """Method for all page-related classes to simplify navigation.

        All class instances that use ``_route`` must have their content packed
        and contain 4 content generation methods, as seen below.
        """
        if kwargs:  # The caller of this route has added arguments for confirmation
            if not self._confirm_route(**kwargs):
                return False  # User didn't want to route

        for widget in Base.base_container.winfo_children():  # Remove content
            widget.pack_forget()

        base.title(title)  # Update to a new title
        
        # Update page in ``config.ini``
        _update_config(Base.cfg, "m", "page", page.__class__.__name__)

        # Place the new page and call its content generation methods
        page.pack(expand=True, fill="both")
        page._make_containers()
        page._place_containers()
        page._make_content()
        page._place_content()

        return True  # Route was successful


class Base(CTk, Addons):
    """The main app instance."""

    base_container: CTkFrame = None
    lang_info: List[Dict[str, str], List[str]] = []
    locale: Locale = None
    cfg: ConfigParser = None

    def __init__(self, **kwargs) -> None:
        super().__init__()

        base_container = CTkFrame(self)
        base_container.pack(fill="both", expand=True)
        Base.base_container = base_container

        for kwarg in kwargs:
            setattr(Base, kwarg, kwargs[kwarg])

        self.protocol("WM_DELETE_WINDOW", self._exit_handler)  # Detect exit
        self.geometry("840x600")
        self.minsize(530, 370)
        if system() == "Windows":
            self.iconbitmap(LOGO_PATH)
        set_appearance_mode(Base.cfg.get("m", "appearance"))
        set_default_color_theme(Base.cfg.get("m", "theme"))
        set_widget_scaling(float(Base.cfg.get("m", "scale")))

        self._increment_launches()

        # Bring the user to the default Home Page
        page = Base.cfg.get("m", "page")
        self._route(globals()[page](self), self, _(PAGE_MAP[page]))

    def _increment_launches(self) -> None:
        """Increment ``launches`` in the program config by 1."""
        return _update_config(
            Base.cfg,
            "misc",
            "launches",
            str(int(Base.cfg.get("misc", "launches")) + 1),
        )

    def _exit_handler(
        self, restart: bool = False, webapp_on: bool = False
    ) -> None:
        """Called when the event "WM_DELETE_WINDOW" occurs or when the the
        program must be restarted, in which case the ``restart`` default
        parameter is overridden.
        """
        # If user wants to exit/restart
        if AppHelper.confirm_with_messagebox(exit_=True, restart=restart):
            _terminate_app()
            self.quit()

        if restart:  # Additionally perform a restart
            start()


class HomePage(CTkFrame, Addons):
    """Class that serves as a homescreen for the program, providing global
    setting configuration, exit functionality and the ability to view the
    currently available crossword puzzles.
    """

    def __init__(self, master) -> None:
        super().__init__(
            Base.base_container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.master = master

        self._set_fonts()

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
                light_image=Image.open(CWORD_IMG_LIGHT_PATH),
                dark_image=Image.open(CWORD_IMG_DARK_PATH),
                size=(453, 154),
            ),
        )

        self.b_open_cword_browser = CTkButton(
            self.cword_opts_container,
            text=_("View crosswords"),
            command=lambda: self._route(
                BrowserPage(self.master), self.master, _("Crossword Browser")
            ),
            width=175,
            height=50,
            font=self.TEXT_FONT,
        )

        self.b_close_app = CTkButton(
            self.cword_opts_container,
            text=_("Exit the app"),
            command=self.master._exit_handler,
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
            wraplength=self.settings_container.winfo_reqwidth() * 0.9,
        )

        self.l_language_opts = CTkLabel(
            self.settings_container,
            text=_("Languages"),
            font=self.BOLD_TEXT_FONT,
        )
        self.opts_language = CTkOptionMenu(
            self.settings_container,
            values=Base.lang_info[1],
            command=self.change_lang,
            font=self.TEXT_FONT,
        )
        self.opts_language.set(Base.locale.language_name)

        self.l_scale_opts = CTkLabel(
            self.settings_container, text=_("Size"), font=self.BOLD_TEXT_FONT
        )
        self.opts_scale = CTkOptionMenu(
            self.settings_container,
            font=self.TEXT_FONT,
            command=self.change_scale,
            values=[
                numbers.format_decimal(
                    str(round(num * 0.1, 1)), locale=Base.locale
                )
                for num in range(7, 16)
            ],
        )
        self.opts_scale.set(
            numbers.format_decimal(
                Base.cfg.get("m", "scale"), locale=Base.locale
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
        self.opts_appearance.set(_(Base.cfg.get("m", "appearance")))

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
            wraplength=self.settings_container.winfo_reqwidth(),
        )
        self.opts_cword_quality = CTkOptionMenu(
            self.settings_container,
            values=self.cword_qualities,
            command=self.change_crossword_quality,
            font=self.TEXT_FONT,
        )
        self.opts_cword_quality.set(_(Base.cfg.get("m", "cword_quality")))

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

    def change_appearance(self, appearance: str) -> None:
        """Ensures the user is not selecting the same appearance, then sets
        the appearance. Some list indexing is required to make the program
        compatible with non-english languages.
        """
        # Must be done because you cannot do ``set_appearance_mode("نظام")``,
        # for example
        eng_appearance_name: str = BASE_ENG_APPEARANCES[
            self.appearances.index(appearance)
        ]
        if eng_appearance_name == Base.cfg.get("m", "appearance"):
            return AppHelper.show_messagebox(same_appearance=True)

        set_appearance_mode(eng_appearance_name)
        _update_config(Base.cfg, "m", "appearance", eng_appearance_name)

    def change_scale(self, scale: str) -> None:
        """Ensures the user is not selecting the same scale, then sets the scale."""
        scale = float(numbers.parse_decimal(scale, locale=Base.locale))
        if scale == float(Base.cfg.get("m", "scale")):
            return AppHelper.show_messagebox(same_scale=True)

        set_widget_scaling(scale)
        _update_config(Base.cfg, "m", "scale", str(scale))

    def change_lang(self, lang: str) -> None:
        """Ensures the user is not selecting the same language, then creates a
        new ``locale`` variable based on the English name of the language
        (retrieved from ``self.localised_lang_db``). The method then installs a
        new set of translations with gettext and regenerates the content of the
        GUI.
        """
        lang = Base.lang_info[0][lang]
        if lang == Base.cfg.get("m", "language"):
            return AppHelper.show_messagebox(same_lang=True)

        Base.locale = Locale.parse(lang)
        AppHelper._install_translations(Base.locale)
        _update_config(Base.cfg, "m", "language", lang)

        self._route(HomePage(self.master), self.master, _("Crossword Puzzle"))

    def change_crossword_quality(self, quality: str) -> None:
        """Ensures the user is not selecting the same crossword quality, then
        updates the crossword quality in ``config.ini``.
        """
        eng_quality_name: str = BASE_ENG_CWORD_QUALITIES[
            self.cword_qualities.index(quality)
        ]
        if eng_quality_name == Base.cfg.get("m", "cword_quality"):
            return AppHelper.show_messagebox(same_quality=True)

        _update_config(Base.cfg, "m", "cword_quality", eng_quality_name)


class BrowserPage(CTkFrame, Addons):
    """Provides an interface to view available crosswords, set a preference for
    the word count, generate a crossword based on the selected parameters, and
    launch the crossword webapp to complete the generated crossword.
    """

    def __init__(self, master: Base) -> None:
        super().__init__(
            Base.base_container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.master = master
        self._set_fonts()

        if not CrosswordWrapper.helper:  # Set the CrosswordWrapper helper method
            CrosswordWrapper.helper = AppHelper

        self.launch_options_on: bool = False
        self.webapp_on: bool = False
        self.wc_pref: IntVar = IntVar()  # Word count preference
        self.wc_pref.set(-1)

        # Notify user the first time they open this page
        if Base.cfg.get("misc", "cword_browser_opened") == "0":
            AppHelper.show_messagebox(first_time_opening_cword_browser=True)
            _update_config(Base.cfg, "misc", "cword_browser_opened", "1")

    def _make_containers(self) -> None:
        self.center_container = CTkFrame(self)

        self.block_container = CTkScrollableFrame(
            self.center_container,
            orientation="horizontal",
            corner_radius=0,
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            scrollbar_button_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.block_container.bind_all("<MouseWheel>", self._handle_scroll)

        self.button_container = CTkFrame(
            self, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )

        self.pref_container = CTkFrame(
            self, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.pref_container.grid_columnconfigure((0, 1), weight=0)

    def _place_containers(self) -> None:
        self.center_container.pack(anchor="c", expand=True, fill="x")
        self.block_container.pack(expand=True, fill="both")
        self.button_container.place(relx=0.725, rely=0.8425, anchor="c")
        self.pref_container.place(relx=0.3, rely=0.84, anchor="c")

    def _make_content(self) -> None:
        self.l_title = CTkLabel(
            self, text=_("Crossword Browser"), font=self.TITLE_FONT
        )

        self.b_go_back = CTkButton(
            self,
            text=_("Go back"),
            command=lambda: self._route(
                HomePage(self.master),
                self.master,
                _("Crossword Puzzle"),
                action=self._terminate,
                condition=self.webapp_on,
            ),
            width=175,
            height=50,
            fg_color=Colour.Global.EXIT_BUTTON,
            hover_color=Colour.Global.EXIT_BUTTON_HOVER,
            font=self.TEXT_FONT,
        )

        self.b_load_cword = CTkButton(
            self.button_container,
            text=_("Load"),
            height=50,
            command=self.load,
            state="disabled",
            font=self.TEXT_FONT,
        )

        self.b_open_webapp = CTkButton(
            self.button_container,
            text=_("Open"),
            height=50,
            command=self.open_webapp,
            font=self.TEXT_FONT,
            fg_color=Colour.Global.GREEN_BUTTON,
            hover_color=Colour.Global.GREEN_BUTTON_HOVER,
        )

        self.b_terminate_webapp = CTkButton(
            self.button_container,
            text=_("Terminate"),
            height=50,
            command=self._terminate,
            fg_color=Colour.Global.EXIT_BUTTON,
            hover_color=Colour.Global.EXIT_BUTTON_HOVER,
            state="disabled",
            font=self.TEXT_FONT,
        )

        self.l_wc_prefs = CTkLabel(
            self.pref_container,
            text=_("Word count preferences"),
            state="disabled",
            font=self.BOLD_TEXT_FONT,
            text_color_disabled=(
                Colour.Light.TEXT_DISABLED,
                Colour.Dark.TEXT_DISABLED,
            ),
        )

        self.opts_custom_wc = CTkOptionMenu(
            self.pref_container,
            state="disabled",
            font=self.TEXT_FONT,
            command=lambda val: self.cwrapper.set_word_count(int(val)),
        )
        self.opts_custom_wc.set(_("Select word count"))

        self.rb_max_wc = CTkRadioButton(
            self.pref_container,
            text=f"{_('Maximum')}: ",
            variable=self.wc_pref,
            value=0,
            state="disabled",
            corner_radius=1,
            command=lambda: self._on_wc_sel("max"),
            font=self.TEXT_FONT,
        )

        self.rb_custom_wc = CTkRadioButton(
            self.pref_container,
            text=_("Custom"),
            variable=self.wc_pref,
            value=1,
            state="disabled",
            corner_radius=1,
            command=lambda: self._on_wc_sel("custom"),
            font=self.TEXT_FONT,
        )

        CategoryBlock._populate(self)

    def _place_content(self) -> None:
        self.l_title.place(relx=0.5, rely=0.1, anchor="c")
        self.b_go_back.place(relx=0.5, rely=0.2, anchor="c")
        self.b_load_cword.grid(row=0, column=0, sticky="nsew", padx=7, pady=7)
        self.b_terminate_webapp.grid(row=0, column=1, sticky="nsew", padx=7, pady=7)
        self.l_wc_prefs.grid(row=0, column=0, columnspan=2, pady=(5, 10))
        self.rb_max_wc.grid(row=1, column=0, padx=7, pady=7)
        self.rb_custom_wc.grid(row=2, column=0, padx=7, pady=7)
        self.opts_custom_wc.grid(row=3, column=0, padx=7, pady=7)

    def _handle_scroll(self, event: Event) -> None:
        """Scroll the center scroll frame only if the viewable width is greater
        than the scroll region. This prevents weird scroll behaviour in cases
        where the above condition is inverted.
        """
        scroll_region = self.block_container._parent_canvas.cget(
            "scrollregion"
        )
        viewable_width = self.block_container._parent_canvas.winfo_width()
        if scroll_region and int(scroll_region.split(" ")[2]) > viewable_width:
            # -1 * event.delta emulates a "natural" scrolling motion
            self.block_container._parent_canvas.xview(
                "scroll", -1 * event.delta, "units"
            )

    def _on_wc_sel(self, button_name: str) -> None:
        """Configure custom word count optionmenu based on radiobutton selection."""
        if button_name == "max":
            self.cwrapper.set_word_count(self.cwrapper.total_definitions)

            self.opts_custom_wc.set(_("Select word count"))
            self.opts_custom_wc.configure(state="disabled")

        else:
            self.cwrapper.set_word_count(3)

            self.opts_custom_wc.set(
                f"{str(numbers.format_decimal(3, locale=Base.locale))}"
            )
            self.opts_custom_wc.configure(state="normal")

        self.b_load_cword.configure(state="normal")

    def open_webapp(self) -> None:
        """Open the crossword web app at a port read from ``Base.cfg``."""
        Base.cfg.read(CONFIG_PATH)
        open_new_tab(
            f"http://127.0.0.1:{Base.cfg.get('misc', 'webapp_port')}/"
        )

    def _terminate(self) -> None:
        """Reconfigure the states of the GUIs buttons and terminate the app."""
        self.b_open_webapp.grid_forget()
        self._rollback_states()
        self.launch_options_on: bool = False
        _terminate_app()
        self.webapp_on: bool = False

    def _rollback_states(self) -> None:
        """Set all the widgets back to their default states (seen when opening
        the crossword browser).
        """
        if hasattr(self, "cwrapper"):  # User selected a crossword, meaning they
                                       # had a category open, so this must be done
            self.cwrapper.category_object.b_close.configure(state="normal")
            CrosswordBlock._config_selectors(state="normal")

        self.b_terminate_webapp.configure(state="disabled")
        self.b_open_webapp.grid_forget()
        self.b_load_cword.grid(row=0, column=0, sticky="nsew", padx=7, pady=7)
        self.b_load_cword.configure(state="disabled")
        self._configure_word_count_prefs("disabled")
        self.rb_max_wc.configure(text=f"{_('Maximum')}:")
        self.opts_custom_wc.set(_("Select word count"))
        self.wc_pref.set(-1)

    def _configure_word_count_prefs(self, state: str) -> None:
        """Configure all the word_count preference widgets to an either an
        interactive or disabled state (interactive when selecting a crossword,
        disabled when a crossword has been loaded).
        """
        self.l_wc_prefs.configure(state=state)
        self.rb_max_wc.configure(state=state)
        self.rb_custom_wc.configure(state=state)
        self.opts_custom_wc.configure(state=state)

    def load(self) -> None:
        """Initialise the crossword and web app."""
        self.cwrapper.make()
        if self.cwrapper.err_flag:  # Error in crossword generation, exit func
            return

        # It is safe to update widget states as crossword generation was OK
        self.b_load_cword.grid_forget()
        self.cwrapper.category_object.b_close.configure(state="disabled")
        CrosswordBlock._config_selectors(state="disabled")
        self._configure_word_count_prefs("disabled")
        self.cwrapper.category_object.selected_cword.set(-1)

        self._load()
        self.webapp_on: bool = True

        self.b_open_webapp.grid(row=0, column=0, sticky="nsew", padx=7, pady=7)
        self.b_terminate_webapp.configure(state="normal")

    def _load(self) -> None:
        """Gather data and use ``_create_app`` to initialise the Flask app on a
        new thread.
        """
        (
            starting_word_positions,
            starting_word_matrix,
            definitions_a,
            definitions_d,
        ) = _interpret_cword_data(self.cwrapper.crossword)
        colour_palette: Dict[str, str] = _get_colour_palette_for_webapp(
            get_appearance_mode()
        )
        _create_app(
            locale=Base.locale,
            scaling=self.master._get_widget_scaling(),
            colour_palette=colour_palette,
            json_colour_palette=dumps(colour_palette),
            port=Base.cfg.get("misc", "webapp_port"),
            name=self.cwrapper.translated_name,
            category=self.cwrapper.category,
            difficulty=self.cwrapper.difficulty,
            empty=EMPTY,
            directions=[ACROSS, DOWN],
            # Tuples in intersections must be removed. Changing this in
            # ``cworg_gen.py`` was annoying, so it is done here instead.
            intersections=[
                list(item) if isinstance(item, tuple) else item
                for sublist in self.cwrapper.crossword.intersections
                for item in sublist
            ],
            word_count=self.cwrapper.word_count,
            failed_insertions=self.cwrapper.crossword.fails,
            dimensions=self.cwrapper.crossword.dimensions,
            starting_word_positions=starting_word_positions,
            starting_word_matrix=starting_word_matrix,
            grid=self.cwrapper.crossword.grid,
            definitions_a=definitions_a,
            definitions_d=definitions_d,
            js_err_msgs=[
                _("To perform this operation, you must first select a cell.")
            ],
            uuid=str(uuid4()),
        )

    def _on_cword_selection(self, wrapper: CrosswordWrapper) -> None:
        """Called by an instance of ``CrosswordBlock``, which passes the
        data for its given crossword into this method. The method then saves
        this data, deselects any previous word count radiobutton selections,
        reconfigures the values of the custom word count optionmenu to be
        compatible with the newly selected crossword, and reconfigures the
        max word count label to show the correct maximum word count.
        """
        if not self.launch_options_on:
            self._configure_word_count_prefs("normal")
            self.launch_options_on: bool = True

        self.b_load_cword.configure(state="disabled")
        self.opts_custom_wc.configure(state="disabled")
        self.wc_pref.set(-1)
        self.opts_custom_wc.set(_("Select word count"))

        self.cwrapper = wrapper

        self.opts_custom_wc.configure(
            values=[
                str(numbers.format_decimal(num, locale=Base.locale))
                for num in range(3, self.cwrapper.total_definitions + 1)
            ]
        )
        self.rb_max_wc.configure(
            text=f"{_('Maximum')}: "
            f"{numbers.format_decimal(self.cwrapper.total_definitions, locale=Base.locale)}"
        )
        self.rb_max_wc.invoke()


class CategoryBlock(CTkFrame, Addons, BlockUtils):
    """A frame containing the name of a crossword category and a buttons to
    open/close all the crosswords contained within that category. Opening a
    category block will remove all other category blocks and display only the
    crosswords within that category.
    """

    blocks: List[object] = []  # Stores the current category blocks

    def __init__(
        self,
        container: CTkFrame,
        master: BrowserPage,
        name: str,
        fp: PathLike,
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
        self.name = name
        self.fp = fp
        self.value = value

        self.selected_cword = IntVar()
        self.selected_cword.set(-1)

        self._set_fonts()
        self._check_info()
        self._make_content()
        self._place_content()

    @classmethod
    def _populate(cls, master: BrowserPage) -> None:
        """Instantiate a variable amount of category blocks and put them in the 
        block container.
        """
        for i, category in enumerate(_get_crossword_categories()):
            block: CategoryBlock = cls(
                master.block_container,
                master,
                category.name,
                category.path,
                i,
            )
            cls._put_block(block)

    def _make_content(self) -> None:
        self.tb_name = CTkTextbox(
            self,
            font=self.CATEGORY_FONT,
            wrap="char",
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            scrollbar_button_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.tb_name.tag_config("center", justify="center")
        self.tb_name.insert("end", _(self.name.title()), "center")
        self.tb_name.configure(state="disabled")

        self.b_view = CTkButton(
            self,
            font=self.TEXT_FONT,
            text=_("View"),
            command=self._open,
            width=65,
        )
        self.b_close = CTkButton(
            self,
            font=self.TEXT_FONT,
            text=_("Close"),
            command=self._close,
            fg_color=Colour.Global.EXIT_BUTTON,
            hover_color=Colour.Global.EXIT_BUTTON_HOVER,
            width=65,
        )
        self.bottom_colour_tag = CTkLabel(
            self,
            text="",
            fg_color=load(open(path.join(self.fp, "info.json"))).get(
                "bottom_tag_colour"
            )
            or "#FF0000",
            corner_radius=10,
        )

    def _place_content(self) -> None:
        self.tb_name.place(
            relx=0.5, rely=0.2, anchor="c", relwidth=0.9, relheight=0.231
        )
        self.b_view.place(relx=0.5, rely=0.5, anchor="c")
        self.bottom_colour_tag.place(
            relx=0.5, rely=0.895, anchor="c", relwidth=0.75, relheight=0.06
        )

    def _check_info(self) -> None:
        if (
            "info.json" not in listdir(self.fp)
            or path.getsize(path.join(self.fp, "info.json")) <= 0
        ):
            _make_category_info_json(path.join(self.fp, "info.json"))

    def _open(self) -> None:
        """View all crossword info blocks for a specific category."""
        self.master.block_container._parent_canvas.xview("moveto", 0.0)
        self.b_view.configure(state="disabled")

        self._set_all(self._remove_block)
        self._put_block(self)
        CrosswordBlock._populate(self.master, self)

        self.b_close.place(relx=0.5, rely=0.7, anchor="c")

    def _close(self) -> None:
        """Remove all crossword info blocks, and regenerate the category blocks."""
        self.b_view.configure(state="normal")
        self.b_close.place_forget()

        CrosswordBlock._set_all(CrosswordBlock._remove_block)
        self._remove_block(self)
        self._populate(self.master)

        self.master.b_load_cword.configure(state="disabled")
        self.master._terminate()


class CrosswordBlock(CTkFrame, Addons, BlockUtils):
    """A frame containing a crosswords name, as well data read from its
    corresponding ``info.json`` file, including total definitions/word count,
    difficulty, and a symbol to prefix the crosswords name. A variable amount
    of these is created based on how many crosswords each category contains.
    """

    blocks: List[object] = []  # Stores the current crossword info blocks

    def __init__(
        self,
        master: BrowserPage,
        container: CTkFrame,
        category: str,
        category_object: CategoryBlock,
        name: str,
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

        self.cwrapper: CrosswordWrapper = CrosswordWrapper(
            category,
            name,
            language=Base.locale.language,
            category_object=category_object,
            value=value,
        )
        self.localised_difficulty: str = _(self.cwrapper.difficulty)

        self._set_fonts()
        self._make_content()
        self._place_content()

    @classmethod
    def _populate(cls, master: BrowserPage, category: str) -> None:
        """Instantiate a variable amount of crossword blocks and put them in 
        the block container.
        """
        for i, crossword in enumerate(
            _sort_crosswords_by_suffix(_get_base_crosswords(category.name))
        ):
            block: CrosswordBlock = cls(
                master,
                master.block_container,
                category.name,
                category,
                crossword.name,
                i,
            )
            cls._put_block(block)

    def _make_content(self) -> None:
        self.tb_name = CTkTextbox(
            self,
            font=self.CWORD_BLOCK_FONT,
            wrap="char",
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            scrollbar_button_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.tb_name.tag_config("center", justify="center")
        self.tb_name.insert(
            "end",
            f"{chr(int(self.cwrapper.info['symbol'], 16))} {self.cwrapper.translated_name}",
            "center",
        )
        self.tb_name.configure(state="disabled")

        self.l_total_words = CTkLabel(
            self,
            font=self.TEXT_FONT,
            text=f"{_('Total words')}: "
            f"{numbers.format_decimal(self.cwrapper.info['total_definitions'], locale=self.cwrapper.language)}",
        )

        self.l_difficulty = CTkLabel(
            self,
            font=self.TEXT_FONT,
            text=f"{_('Difficulty')}: {self.localised_difficulty}",
        )

        self.bottom_colour_tag = CTkLabel(
            self,
            text="",
            fg_color=Colour.Global.DIFFICULTIES[
                self.cwrapper.info["difficulty"]
            ],
            corner_radius=10,
        )

        self.rb_selector = CTkRadioButton(
            self,
            text=_("Select"),
            corner_radius=1,
            font=self.TEXT_FONT,
            variable=self.cwrapper.category_object.selected_cword,
            value=self.cwrapper.value,
            command=lambda: self.master._on_cword_selection(self.cwrapper),
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
    def _install_translations(locale: Locale) -> None:
        """Install translations from ``locale.language`` with gettext."""
        translation(
            "messages",
            localedir=LOCALES_PATH,
            languages=[locale.language],
        ).install()

    @staticmethod
    def confirm_with_messagebox(
        exit_: bool = False, restart: bool = False, close: bool = False
    ) -> bool:
        """Provide confirmations to the user with tkinter messageboxes."""
        if exit_ and restart:
            return messagebox.askyesno(
                _("Restart"), _("Are you sure you want to restart the app?")
            )

        if exit_ and not restart:
            return messagebox.askyesno(
                _("Exit"),
                _(
                    "Are you sure you want to exit the app? If the web app is "
                    "running, it will be terminated."
                ),
            )

        if close:
            return messagebox.askyesno(
                _("Back to home"),
                _(
                    "Are you sure you want to go back to the home screen? The web "
                    "app will be terminated."
                ),
            )

    @staticmethod
    def show_messagebox(*args, **kwargs) -> None:
        """Show an error/info messagebox."""
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

        if "first_time_opening_cword_browser" in kwargs:
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
                    "An unexpected error occured. Please reinstall the "
                    "application with"
                )
                + " pip install --force-reinstall crossword-puzzle",
            )


def start() -> None:
    cfg: ConfigParser = ConfigParser()
    cfg.read(CONFIG_PATH)
    locale: Locale = Locale.parse(cfg.get("m", "language"))
    AppHelper._install_translations(locale)
    app: Base = Base(locale=locale, lang_info=_get_language_options(), cfg=cfg)
    app.mainloop()


if __name__ == "__main__":
    start()
