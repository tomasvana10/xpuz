"""GUI page for searching, viewing and loading available crosswords."""

from json import dumps, load
from os import DirEntry, PathLike, listdir, path
from tkinter import Event, IntVar, StringVar
from typing import Dict, List, Optional, Tuple, Union
from uuid import uuid4
from webbrowser import open_new_tab

from babel import numbers
from customtkinter import (
    CTkButton,
    CTkEntry,
    CTkFrame,
    CTkLabel,
    CTkOptionMenu,
    CTkRadioButton,
    CTkScrollableFrame,
    CTkSegmentedButton,
    CTkTextbox,
    get_appearance_mode,
)

from crossword_puzzle.base import Addons, Base
from crossword_puzzle.constants import (
    ACROSS,
    BASE_ENG_VIEWS,
    DOWN,
    EMPTY,
    PAGE_MAP,
    Colour,
)
from crossword_puzzle.cword_webapp.app import _create_app, _terminate_app
from crossword_puzzle.utils import (
    BlockUtils,
    GUIHelper,
    _get_base_categories,
    _get_base_crosswords,
    _get_colour_palette,
    _interpret_cword_data,
    _make_category_info_json,
    _read_cfg,
    _sort_crosswords_by_suffix,
    _update_cfg,
)
from crossword_puzzle.wrappers import CrosswordWrapper


class BrowserPage(CTkFrame, Addons):
    """Provides an interface to view available crosswords, set a preference for
    the word count, generate a crossword based on the selected parameters, and
    launch the crossword webapp to complete the generated crossword.
    """

    def __init__(self, master: "Base") -> None:
        super().__init__(
            Base.base_container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.master = master
        self.master._set_dim()
        self._set_fonts()
        self._width, self._height = (
            self.master.winfo_width(), self.master.winfo_height()
        )
        
        self.grid_rowconfigure(0, minsize=self._height * 0.15, weight=1)
        self.grid_rowconfigure(1, minsize=self._height * 0.85, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if (
            not CrosswordWrapper.helper
        ):  # Set the CrosswordWrapper helper method
            CrosswordWrapper.helper = GUIHelper

        self.launch_options_on: bool = False
        self.webapp_on: bool = False
        self.wc_pref: IntVar = IntVar()  # Word count preference
        self.wc_pref.set(-1)
        self.view_pref: StringVar = StringVar()  # Browser view preference
        self.view_pref.set(Base.cfg.get("m", "view"))

        # Notify user the first time they open this page
        if Base.cfg.get("misc", "browser_opened") == "0":
            GUIHelper.show_messagebox(first_time_browser=True)
            _update_cfg(Base.cfg, "misc", "browser_opened", "1")

    def _make_containers(self) -> None:
        self.header_container = CTkFrame(
            self, fg_color=(Colour.Light.SUB, Colour.Dark.SUB), corner_radius=0
        )
        self.browser_container = CTkFrame(
            self, corner_radius=0, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN))
        
        self.view_container = CTkFrame(
            self.browser_container, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        
        self.center_container = CTkFrame(self.browser_container)

        self.block_container = CTkScrollableFrame(
            self.center_container,
            orientation="horizontal",
            corner_radius=0,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            scrollbar_button_color=(Colour.Light.SUB, Colour.Dark.SUB),
        )
        self.block_container.bind_all("<MouseWheel>", self._handle_scroll)

        self.bottom_container = CTkFrame(
            self.browser_container, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.button_container = CTkFrame(
            self.bottom_container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )

        self.pref_container = CTkFrame(
            self.bottom_container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.pref_container.grid_columnconfigure((0, 1), weight=0)

    def _place_containers(self) -> None:
        self.header_container.grid(row=0, column=0, sticky="nsew")
        self.browser_container.grid(row=1, column=0, sticky="nsew")
        self.view_container.place(relx=0.5, rely=0.13, anchor="c")
        self.center_container.place(relx=0.5, rely=0.45, anchor="c", relwidth=1.0)
        self.block_container.pack(expand=True, fill="both")
        self.bottom_container.place(relx=0.5, rely=0.82, anchor="c")
        self.pref_container.grid(row=0, column=0, padx=(10, 50), pady=10)
        self.button_container.grid(row=0, column=1, padx=(50, 10), pady=10)

    def _make_content(self) -> None:
        self.l_title = CTkLabel(
            self.header_container, text=_("Crossword Browser"), font=self.TITLE_FONT
        )

        self.b_go_back = CTkButton(
            self.header_container,
            text=_("Back"),
            command=lambda: self._route(
                "HomePage",
                self.master,
                _(PAGE_MAP["HomePage"]),
                action=self._terminate,
                condition=self.webapp_on,
            ),
            height=50,
            width=100,
            fg_color=Colour.Global.EXIT_BUTTON,
            hover_color=Colour.Global.EXIT_BUTTON_HOVER,
            font=self.TEXT_FONT,
        )

        self.views = [_("Categorised"), _("Flattened")]
        self.sb_view = CTkSegmentedButton(
            self.view_container,
            values=self.views,
            font=self.TEXT_FONT,
            command=self.change_view,
            variable=self.view_pref,
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            height=50,
            unselected_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.master.update()
        for button in self.sb_view._buttons_dict.values():
            button.configure(width=150)

        self.e_search = CTkEntry(
            self.view_container,
            placeholder_text=f"{_('Search')} [↵]",
            font=self.TEXT_FONT,
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            bg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            justify="center",
            width=300,
        )
        self.e_search.bind(
            "<Return>", lambda e: self._search_crossword(self.e_search.get())
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

        self.change_view()

    def _place_content(self) -> None:
        self.l_title.place(relx=0.5, rely=0.5, anchor="c")
        self.b_go_back.place(x=20, y=20)
        self.sb_view.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.e_search.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.b_load_cword.grid(row=0, column=0, sticky="nsew", padx=7, pady=7)
        self.b_terminate_webapp.grid(
            row=0, column=1, sticky="nsew", padx=7, pady=7
        )
        self.l_wc_prefs.grid(row=0, column=0, columnspan=2, pady=(5, 10))
        self.rb_max_wc.grid(row=1, column=0, padx=7, pady=7)
        self.rb_custom_wc.grid(row=2, column=0, padx=7, pady=7)
        self.opts_custom_wc.grid(row=3, column=0, padx=7, pady=7)

    def _search_crossword(self, query: str) -> None:
        """Regenerate all the crossword blocks based on a crossword name query."""
        if self.view_pref.get() != "Flattened":  # Only works in Flattened view
            return

        self._rollback_states()
        CategoryBlock._set_all(CategoryBlock._remove_block)
        CrosswordBlock._set_all(CrosswordBlock._remove_block)
        self._reset_scroll_frame()
        CrosswordBlock._populate_all(self, query)

    def _reset_search(self) -> None:
        """Remove all text from the search box and regenerate the placeholder
        text.
        """
        self.master.focus_force()
        self.e_search.delete(0, "end")
        self.e_search.configure(placeholder_text=f"{_('Search')} [↵]")

    def _reset_scroll_frame(self) -> None:
        """Set the x position of the center scroll frame to the start."""
        self.block_container._parent_canvas.xview("moveto", 0.0)

    def _update_segbutton_text_colours(self, view: str) -> None:
        """Configure all segmented button colours in ``self.sb_view`` to have
        a black text colour if unselected, otherwise, set the text colour to
        white.
        """

        if get_appearance_mode().casefold() != "light":
            return

        for button in self.sb_view._buttons_dict.values():
            if button.cget("text") != view:
                button.configure(text_color="black")
            else:
                button.configure(text_color="white")

    def change_view(self, callback: Optional[bool] = None) -> None:
        """Change the browser view to Flattened or Categorical."""

        self._rollback_states()
        # Remove existing blocks
        CategoryBlock._set_all(CategoryBlock._remove_block)
        CrosswordBlock._set_all(CrosswordBlock._remove_block)
        self._reset_scroll_frame()
        # Find true english name of selected view
        view = BASE_ENG_VIEWS[self.views.index(self.view_pref.get())]

        self._update_segbutton_text_colours(view)
        if view == "Categorised":
            self._reset_search()
            self.e_search.configure(state="disabled")
            CategoryBlock._populate(self)
        elif view == "Flattened":
            self._reset_search()
            self.e_search.configure(state="normal")
            CrosswordBlock._populate_all(self)

        _update_cfg(Base.cfg, "m", "view", view)

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
        _read_cfg(Base.cfg)
        open_new_tab(
            f"http://127.0.0.1:{Base.cfg.get('misc', 'webapp_port')}/"
        )

    def _terminate(self) -> None:
        """Reconfigure the states of the GUIs buttons and terminate the app."""
        self.b_open_webapp.grid_forget()
        self._rollback_states()
        if Base.cfg.get("m", "view") == "Flattened":
            self.e_search.configure(state="normal")
        self.sb_view.configure(state="normal")
        _terminate_app()
        self.webapp_on: bool = False

    def _rollback_states(self) -> None:
        """Set all the widgets back to their default states (seen when opening
        the crossword browser).
        """
        if hasattr(
            self, "cwrapper"
        ):  # User selected a crossword, meaning they
            # had a category open, so this must be done
            if self.cwrapper.category_object:
                self.cwrapper.category_object.b_close.configure(state="normal")
            CrosswordBlock._config_selectors(state="normal")

        self.sb_view.configure(state="normal")
        self.b_terminate_webapp.configure(state="disabled")
        self.b_open_webapp.grid_forget()
        self.b_load_cword.grid(row=0, column=0, sticky="nsew", padx=7, pady=7)
        self.b_load_cword.configure(state="disabled")
        self._configure_word_count_prefs("disabled")
        self.rb_max_wc.configure(text=f"{_('Maximum')}:")
        self.opts_custom_wc.set(_("Select word count"))
        self.wc_pref.set(-1)
        self.launch_options_on: bool = False

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
        if self.cwrapper.category_object:
            self.cwrapper.category_object.b_close.configure(state="disabled")
            self.cwrapper.category_object.selected_cword.set(-1)
        else:
            CrosswordBlock.global_selected_cword.set(-1)
        CrosswordBlock._config_selectors(state="disabled")
        self._configure_word_count_prefs("disabled")
        self.sb_view.configure(state="disabled")
        self.e_search.configure(state="disabled")

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
        colour_palette: Dict[str, str] = _get_colour_palette(
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
            # ``crossword.py`` was annoying, so it is done here instead.
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
        """Instantiate all the base category blocks and put them in the central
        scroll container.
        """
        for i, category in enumerate(_get_base_categories()):
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
            _make_category_info_json(self.fp)

    def _open(self) -> None:
        """View all crossword info blocks for a specific category."""
        self.master._reset_scroll_frame()
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

    # If the user is viewing the browser in flattened mode, then a categorised
    # IntVar (belonging in the crossword's category object) cannot be used.
    # Instead, this global attribute is set to an IntVar at runtime when
    # required and is used instead of a category's IntVar.
    global_selected_cword: Union[None, IntVar] = None

    def __init__(
        self,
        master: BrowserPage,
        container: CTkFrame,
        category: str,
        name: str,
        value: int,
        category_object: Optional[CategoryBlock] = None,
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
    def _populate(cls, master: BrowserPage, category: CategoryBlock) -> None:
        """Instantiate all the base crossword blocks for a given category and
        put them in the central scroll container.
        """
        for i, crossword in enumerate(
            _get_base_crosswords(category.fp)
        ):
            block: CrosswordBlock = cls(
                master,
                master.block_container,
                category.name,
                crossword.name,
                i,
                category,
            )
            cls._put_block(block)

    @classmethod
    def _populate_all(
        cls, master: BrowserPage, query: Optional[str] = None
    ) -> None:
        """Instantiate all the base crossword blocks and sort them holistically
        by difficulty suffix, putting them in the central scroll container only
        if they match the provided ``query`` parameter (if it is not None).
        """
        crosswords: List[Tuple[DirEntry, DirEntry]] = [
            (category, crossword)
            for category in _get_base_categories()
            for crossword in _get_base_crosswords(category.path, sort=False)
        ]
        cls.global_selected_cword = IntVar()
        cls.global_selected_cword.set(-1)
        for i, (category, crossword) in enumerate(
            _sort_crosswords_by_suffix(crosswords)
        ):
            block: CrosswordBlock = cls(
                master,
                master.block_container,
                category.name,
                crossword.name,
                i,
            )
            # If a query has been provided, only put the block if the query
            # returns true
            if query and not BlockUtils._match_block_query(
                query, block.cwrapper.translated_name
            ):
                continue
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
        translated_name = self.cwrapper.translated_name
        self.tb_name.insert(
            "end",
            f"{chr(int(self.cwrapper.info['symbol'], 16))} {translated_name}",
            "center",
        )
        self.tb_name.configure(state="disabled")

        total_words = numbers.format_decimal(
            self.cwrapper.info["total_definitions"],
            locale=self.cwrapper.language,
        )
        self.l_total_words = CTkLabel(
            self,
            font=self.TEXT_FONT,
            text=f"{_('Total words')}: {total_words}",
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
            variable=getattr(
                self.cwrapper.category_object,
                "selected_cword",  # Categorised IntVar
                CrosswordBlock.global_selected_cword,  # Global IntVar (fallback)
            ),
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
