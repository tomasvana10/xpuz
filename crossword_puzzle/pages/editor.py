"""GUI page for editing and making crosswords and their words. Only allows for
the creation and editing of new crosswords, not pre-installed ones.
"""

from os import mkdir, path
from tkinter.ttk import Separator

from customtkinter import CTkButton, CTkFrame, CTkLabel, CTkOptionMenu

from crossword_puzzle.base import Addons, Base
from crossword_puzzle.constants import (
    BASE_CWORDS_PATH, DOC_CAT_PATH, EDITOR_DIM, PAGE_MAP, Colour,
)
from crossword_puzzle.utils import (
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
            self.master.winfo_width(), self.master.winfo_height()
        )
        
        self.grid_rowconfigure(0, minsize=self._height * 0.15, weight=1)
        self.grid_rowconfigure(1, minsize=self._height * 0.85, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._check_user_category()

    def _make_containers(self) -> None:
        self.header_container = CTkFrame(
            self, fg_color=(Colour.Light.SUB, Colour.Dark.SUB), corner_radius=0
        )
        self.editor_container = CTkFrame(
            self, corner_radius=0, fg_color=(Colour.Light.SUB, Colour.Dark.SUB))
        self.editor_container.grid_columnconfigure((0, 1), weight=1)
        
        self.crossword_pane = CrosswordPane(self.editor_container, self)
        self.word_pane = WordPane(self.editor_container, self)

    def _place_containers(self) -> None:
        self.header_container.grid(row=0, column=0, sticky="ew")
        self.editor_container.grid(row=1, column=0, sticky="ew")

    def _make_content(self) -> None:
        self.l_title = CTkLabel(
            self.header_container, text=_("Crossword Editor"), font=self.TITLE_FONT
        )

        self.b_go_back = CTkButton(
            self.header_container,
            text=_("Back"),
            command=lambda: self._route(
                "HomePage",
                self.master,
                _(PAGE_MAP["HomePage"])
            ),
            height=50,
            fg_color=Colour.Global.EXIT_BUTTON,
            hover_color=Colour.Global.EXIT_BUTTON_HOVER,
            font=self.TEXT_FONT,
        )

        """
        values=[
            crossword.name
            for crossword in _get_base_crosswords(
                path.join(BASE_CWORDS_PATH, "user")
            )
        ],
        """

    def _place_content(self) -> None:
        self.b_go_back.place(x=20, y=20)
        self.l_title.place(relx=0.5, rely=0.5, anchor="c")

    def _check_user_category(self) -> None:
        fp = path.join(BASE_CWORDS_PATH, "user")
        if _doc_data_routine(
            doc_callback=lambda: mkdir(DOC_CAT_PATH), 
            local_callback=lambda: mkdir(fp), 
            sublevel=DOC_CAT_PATH
        ):
            fp = DOC_CAT_PATH  # Success, there is now a user category in 
                               # sys documents, so update ``fp``
            
        _make_category_info_json(fp, "#FFFFFF")


class CrosswordPane(CTkFrame):
    def __init__(self, container: CTkFrame, master: EditorPage) -> None:
        super().__init__(
            container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            width=master._height * 0.5,
            height=master._width * 0.85,
            corner_radius=0,
        )
        self.master = master
        self.grid(row=0, column=0, sticky="ew", padx=(0, 1))


class WordPane(CTkFrame):
    def __init__(self, container: CTkFrame, master: EditorPage) -> None:
        super().__init__(
            container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            width=master._height * 0.5,
            height=master._width * 0.85,
            corner_radius=0,
        )
        self.master = master
        self.grid(row=0, column=1, sticky="ew", padx=(1, 0))
