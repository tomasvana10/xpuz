"""GUI page for editing and making crosswords and their words. Only allows for
the creation and editing of new crosswords, not pre-installed ones.
"""

from os import mkdir, path
from tkinter import IntVar, Event
from typing import List, Union

from customtkinter import (
    CTkButton,
    CTkFrame,
    CTkLabel,
    CTkOptionMenu,
    CTkScrollableFrame,
    CTkEntry,
    CTkRadioButton,
    CTkTextbox,
)

from crossword_puzzle.base import Addons, Base
from crossword_puzzle.constants import (
    BASE_CWORDS_PATH,
    DOC_CAT_PATH,
    EDITOR_DIM,
    PAGE_MAP,
    PREV_SCALE_MAP,
    Colour,
)
from crossword_puzzle.utils import (
    BlockUtils,
    _doc_data_routine,
    _get_base_crosswords,
    _make_category_info_json,
)


class Editor:
    pass  # form validation, stuff like that


class EditorPage(CTkFrame, Addons):
    def __init__(self, master) -> None:
        super().__init__(
            Base.base_container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.master = master
        self.master._set_dim(dim=EDITOR_DIM)
        self._set_fonts()
        self._width, self._height = (
            self.master.winfo_width(),
            self.master.winfo_height(),
        )
        self.fp = self._get_user_category_path()

        self.grid_rowconfigure(0, minsize=self._height * 0.15, weight=1)
        self.grid_rowconfigure(1, minsize=self._height * 0.85, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def _make_containers(self) -> None:
        self.header_container = CTkFrame(
            self, fg_color=(Colour.Light.SUB, Colour.Dark.SUB), corner_radius=0
        )
        self.editor_container = CTkFrame(
            self, corner_radius=0, fg_color=(Colour.Light.SUB, Colour.Dark.SUB)
        )
        self.editor_container.grid_columnconfigure((0, 1), weight=1)
        self.editor_container.grid_rowconfigure(
            0, weight=1, minsize=self._height * 0.85
        )

        self.crossword_pane = CrosswordPane(self.editor_container, self)
        self.word_pane = WordPane(self.editor_container, self)

    def _place_containers(self) -> None:
        self.header_container.grid(row=0, column=0, sticky="nsew")
        self.editor_container.grid(row=1, column=0, sticky="nsew")

    def _make_content(self) -> None:
        self.l_title = CTkLabel(
            self.header_container,
            text=_("Crossword Editor"),
            font=self.TITLE_FONT,
        )

        self.b_go_back = CTkButton(
            self.header_container,
            text=_("Back"),
            command=lambda: self._route(
                "HomePage", self.master, _(PAGE_MAP["HomePage"])
            ),
            height=50,
            width=100,
            fg_color=Colour.Global.EXIT_BUTTON,
            hover_color=Colour.Global.EXIT_BUTTON_HOVER,
            font=self.TEXT_FONT,
        )

    def _place_content(self) -> None:
        self.b_go_back.place(x=20, y=20)
        self.l_title.place(relx=0.5, rely=0.5, anchor="c")

    def _get_user_category_path(self) -> None:
        fp = path.join(BASE_CWORDS_PATH, "user")
        if _doc_data_routine(
            doc_callback=lambda: mkdir(DOC_CAT_PATH),
            local_callback=lambda: mkdir(fp),
            sublevel=DOC_CAT_PATH,
        ):
            fp = DOC_CAT_PATH  # Success, there is now a user category in
            # sys documents, so update ``fp``

        _make_category_info_json(fp, "#FFFFFF")
        return fp

    def _handle_scroll(self, event: Event, container: CTkScrollableFrame):
        scroll_region = container._parent_canvas.cget("scrollregion")
        viewable_height = container._parent_canvas.winfo_height()
        if (
            scroll_region
            and int(scroll_region.split(" ")[3]) > viewable_height
        ):
            # -1 * event.delta emulates a "natural" scrolling motion
            container._parent_canvas.yview("scroll", -1 * event.delta, "units")


class CrosswordPane(CTkFrame, Addons):
    def __init__(self, container: CTkFrame, master: EditorPage) -> None:
        super().__init__(
            container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            width=master._height * 0.5,
            height=master._width * 0.85,
            corner_radius=0,
        )
        self.master = master
        self.grid(row=0, column=0, sticky="nsew", padx=(0, 1))

        self._set_fonts()
        self._make_content()
        self._place_content()

    def _make_content(self):
        self.container = CTkFrame(
            self, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.container.grid_rowconfigure(1, minsize=self.master._height * 0.5)
        self.b_edit_container = CTkFrame(
            self.container, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.field_container = CTkFrame(
            self.container, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.field_container.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6), weight=1)

        self.l_title = CTkLabel(
            self.container, text=_("Your Crosswords"), font=self.TITLE_FONT
        )

        self.preview = CTkScrollableFrame(
            self.container,
            orientation="vertical",
            height=self.master._height
            * PREV_SCALE_MAP[Base.cfg.get("m", "scale")],
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            scrollbar_button_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.preview.bind_all(
            "<MouseWheel>",
            lambda e: self.master._handle_scroll(e, self.preview),
        )

        self.b_remove = CTkButton(
            self.b_edit_container,
            text="-",
            width=40,
            height=30,
            font=self.TEXT_FONT,
        )
        self.b_add = CTkButton(
            self.b_edit_container,
            text="+",
            width=40,
            height=30,
            font=self.TEXT_FONT,
        )

        self.l_name = CTkLabel(
            self.field_container, text=_("Name"), font=self.BOLD_TEXT_FONT
        )
        self.e_name = CTkEntry(
            self.field_container,
            font=self.TEXT_FONT,
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            bg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )

        self.l_difficulty = CTkLabel(
            self.field_container,
            text=_("Difficulty"),
            font=self.BOLD_TEXT_FONT,
        )
        self.opts_difficulty = CTkOptionMenu(
            self.field_container, font=self.TEXT_FONT
        )

        self.l_symbol = CTkLabel(
            self.field_container, text=_("Symbol"), font=self.BOLD_TEXT_FONT
        )
        self.e_symbol = CTkEntry(
            self.field_container,
            font=self.TEXT_FONT,
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            bg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )

        self.b_confirm = CTkButton(
            self.field_container,
            text=_("Update"),
            font=self.TEXT_FONT,
            height=50,
        )

        MiniCrosswordBlock._populate(self)

    def _place_content(self):
        self.container.place(relx=0.5, rely=0.5, anchor="c")
        self.l_title.grid(row=0, column=0, columnspan=2, pady=(0, 35))
        self.preview.grid(row=1, column=0, padx=(0, 50))
        self.b_add.pack(side="right", anchor="e")
        self.b_remove.pack(side="right", anchor="e", padx=(81.5, 10))
        self.b_edit_container.grid(row=2, column=0, pady=(7.5, 0))
        self.l_name.grid(row=0, column=0, sticky="w", padx=(5, 0), pady=(0, 5))
        self.e_name.grid(row=1, column=0, pady=(0, 25))
        self.l_difficulty.grid(
            row=2, column=0, sticky="w", padx=(5, 0), pady=(0, 5)
        )
        self.opts_difficulty.grid(row=3, column=0, pady=(0, 25))
        self.l_symbol.grid(
            row=4, column=0, sticky="w", padx=(5, 0), pady=(0, 5)
        )
        self.e_symbol.grid(row=5, column=0, pady=(0, 45))
        self.b_confirm.grid(row=6, column=0)
        self.field_container.grid(row=1, column=1, sticky="n")


class MiniCrosswordBlock(CTkFrame, Addons, BlockUtils):
    blocks: List[object] = []
    selected_block: Union[None, IntVar]

    def __init__(self, master, container, name, value, fp):
        super().__init__(
            container,
            corner_radius=10,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            border_color=(Colour.Light.SUB, Colour.Dark.SUB),
            border_width=3,
        )

        self.master = master
        self.name = name
        self.value = value
        self.fp = fp

        self._set_fonts()
        self._make_content()
        self._place_content()

    @classmethod
    def _populate(cls, master):
        cls.selected_block = IntVar()
        cls.selected_block.set(-1)

        for i, crossword in enumerate(
            _get_base_crosswords(
                path.join(BASE_CWORDS_PATH, "user"), lenient=True
            )
        ):
            block: MiniCrosswordBlock = cls(
                master,
                master.preview,
                crossword.name,
                i,
                crossword.path,
            )
            cls._put_block(block, side="top")

    def _make_content(self):
        self.tb_name = CTkTextbox(
            self,
            font=self.BLOCK_FONT,
            wrap="none",
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            height=10,
            width=125,
        )
        self.tb_name.insert(1.0, self.name)
        self.tb_name.configure(state="disabled")
        self.rb_selector = CTkRadioButton(
            self,
            text="",
            value=self.value,
            variable=MiniCrosswordBlock.selected_block,
            corner_radius=0,
            height=50,
        )

    def _place_content(self):
        self.tb_name.pack(side="left", padx=10, pady=10)
        self.rb_selector.pack(side="right", padx=10, pady=10)


class WordPane(CTkFrame, Addons):
    def __init__(self, container: CTkFrame, master: EditorPage) -> None:
        super().__init__(
            container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            width=master._height * 0.5,
            height=master._width * 0.85,
            corner_radius=0,
        )
        self.master = master
        self.grid(row=0, column=1, sticky="nsew")

        self._set_fonts()
        self._make_content()
        self._place_content()

    def _make_content(self):
        self.container = CTkFrame(
            self, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.container.grid_rowconfigure(1, minsize=self.master._height * 0.5)
        self.b_edit_container = CTkFrame(
            self.container, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.field_container = CTkFrame(
            self.container, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.field_container.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        self.l_title = CTkLabel(
            self.container, text=_("Placeholder's Words"), font=self.TITLE_FONT
        )

        self.preview = CTkScrollableFrame(
            self.container,
            orientation="vertical",
            height=self.master._height
            * PREV_SCALE_MAP[Base.cfg.get("m", "scale")],
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            scrollbar_button_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )

        self.b_remove = CTkButton(
            self.b_edit_container,
            text="-",
            width=40,
            height=30,
            font=self.TEXT_FONT,
        )
        self.b_add = CTkButton(
            self.b_edit_container,
            text="+",
            width=40,
            height=30,
            font=self.TEXT_FONT,
        )

        self.l_word = CTkLabel(
            self.field_container, text=_("Word"), font=self.BOLD_TEXT_FONT
        )
        self.e_word = CTkEntry(
            self.field_container,
            font=self.TEXT_FONT,
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            bg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )

        self.l_clue = CTkLabel(
            self.field_container, text=_("Clue"), font=self.BOLD_TEXT_FONT
        )
        self.e_clue = CTkEntry(
            self.field_container,
            font=self.TEXT_FONT,
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            bg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )

        self.b_confirm = CTkButton(
            self.field_container,
            text=_("Update"),
            font=self.TEXT_FONT,
            height=50,
        )

    def _place_content(self):
        self.container.place(relx=0.5, rely=0.5, anchor="c")
        self.l_title.grid(row=0, column=0, columnspan=2, pady=(0, 35))
        self.preview.grid(row=1, column=0, padx=(0, 50))
        self.b_add.pack(side="right", anchor="e")
        self.b_remove.pack(side="right", anchor="e", padx=(81.5, 10))
        self.b_edit_container.grid(row=2, column=0, pady=(7.5, 0))
        self.l_word.grid(row=0, column=0, sticky="w", padx=(5, 0), pady=(0, 5))
        self.e_word.grid(row=1, column=0, pady=(0, 25))
        self.l_clue.grid(row=2, column=0, sticky="w", padx=(5, 0), pady=(0, 5))
        self.e_clue.grid(row=3, column=0, pady=(0, 45))
        self.b_confirm.grid(row=4, column=0)
        self.field_container.grid(row=1, column=1, sticky="n")
