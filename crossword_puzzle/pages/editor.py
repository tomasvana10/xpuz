"""GUI page for editing and making crosswords and their words. Only allows for
the creation and editing of new crosswords, not pre-installed ones.
"""

from os import mkdir, path, listdir

from customtkinter import CTkButton, CTkFrame, CTkLabel, CTkOptionMenu

from crossword_puzzle.base import Addons, Base
from crossword_puzzle.constants import (
    BASE_CWORDS_PATH, DOC_DATA_PATH, DOC_CAT_PATH, Colour,
)
from crossword_puzzle.utils import (
    _doc_data_routine,
    _get_base_crosswords,
    _make_category_info_json,
)


class EditorPage(CTkFrame, Addons):
    def __init__(self, master) -> None:
        super().__init__(
            Base.base_container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.master = master
        self._set_fonts()

        self._check_user_category()

    def _make_containers(self) -> None:
        self.container = CTkFrame(self)
        self.container.grid_rowconfigure((0, 1), weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.add_word_container = CTkFrame(
            self.container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            border_color=(Colour.Light.SUB, Colour.Dark.SUB),
            border_width=5,
            corner_radius=0,
        )
        self.add_cword_container = CTkFrame(
            self.container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            border_color=(Colour.Light.SUB, Colour.Dark.SUB),
            border_width=5,
            corner_radius=0,
        )

    def _place_containers(self) -> None:
        self.container.pack(fill="both", expand=True)
        self.add_word_container.grid(row=0, column=0, sticky="nsew")
        self.add_cword_container.grid(row=1, column=0, sticky="nsew")

    def _make_content(self) -> None:
        self.l_title = CTkLabel(
            self, text=_("Crossword Editor"), font=self.TITLE_FONT
        )

        self.b_go_back = CTkButton(
            self.add_word_container,
            text=_("Back"),
            command=lambda: self._route(
                "HomePage",
                self.master,
                _("Crossword Puzzle"),
            ),
            height=50,
            fg_color=Colour.Global.EXIT_BUTTON,
            hover_color=Colour.Global.EXIT_BUTTON_HOVER,
            font=self.TEXT_FONT,
        )

        self.l_cwords_opts = CTkLabel(
            self.add_word_container,
            text=_("Your crosswords"),
            font=self.BOLD_TEXT_FONT,
        )
        self.opts_cwords = CTkOptionMenu(
            self.add_word_container,
            values=[
                crossword.name
                for crossword in _get_base_crosswords(
                    path.join(BASE_CWORDS_PATH, "user")
                )
            ],
            font=self.TEXT_FONT,
        )
        self.opts_cwords.set("Choose")

    def _place_content(self) -> None:
        self.b_go_back.place(x=20, y=20)
        self.l_title.place(relx=0.5, rely=0.075, anchor="c")
        self.l_cwords_opts.place(relx=0.2, rely=0.3, anchor="c")
        self.opts_cwords.place(relx=0.2, rely=0.42, anchor="c")

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
