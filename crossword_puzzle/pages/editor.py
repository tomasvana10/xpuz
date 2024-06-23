"""GUI page for editing and making crosswords and their words. Only allows for
the creation and editing of new crosswords, not pre-installed ones.
"""

from os import mkdir, path, PathLike
from tkinter import IntVar, Event
from typing import List, Union, Callable
from shutil import rmtree

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
from pathvalidate import validate_filename, ValidationError

from crossword_puzzle.base import Addons, Base
from crossword_puzzle.constants import (
    BASE_CWORDS_PATH,
    DOC_CAT_PATH,
    EDITOR_DIM,
    PAGE_MAP,
    PREV_SCALE_MAP,
    DIFFICULTIES,
    Colour,
)
from crossword_puzzle.utils import (
    BlockUtils,
    GUIHelper,
    _doc_data_routine,
    _get_base_crosswords,
    _make_category_info_json,
)
from crossword_puzzle.wrappers import CrosswordWrapper
from crossword_puzzle.td import CrosswordInfo


class FormParser:
    @staticmethod
    def _parse_name_entry(form) -> None:
        try:
            if len(form) <= 32 and validate_filename(str(form)) is None:
                form.set_valid()
            else:
                form.set_invalid()
        except Exception:
            form.set_invalid()
        form._check_default()

    @staticmethod
    def _get_symbol_components(symbol):
        return [hex(ord(char)) for char in symbol]

    @staticmethod
    def _parse_symbol_entry(form) -> None:
        components = FormParser._get_symbol_components(str(form))
        if len(components) == 1:
            form.set_valid()
        else:
            form.set_invalid()
        form._check_default()


class Form(CTkFrame, Addons):
    crossword_forms: List[object] = []
    word_forms: List[object] = []

    def __init__(
        self,
        master: CTkFrame,
        name: str,
        validation_func: Callable,
        pane: str,
        b_confirm: CTkButton,
    ) -> None:
        self._set_fonts()
        super().__init__(
            master,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )

        self._label = CTkLabel(
            self,
            text=_(name.title()),
            font=self.BOLD_TEXT_FONT,
            text_color_disabled=(
                Colour.Light.TEXT_DISABLED,
                Colour.Dark.TEXT_DISABLED,
            ),
        )
        self._form = CTkEntry(
            self,
            font=self.TEXT_FONT,
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            bg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.b_reset_default = CTkButton(
            self,
            text="↺",
            command=lambda: self.put(self.default, is_default=True),
            height=28,
            width=28,
            font=self.TEXT_FONT,
        )
        self.b_reset_default.configure(state="disabled")

        self._label.grid(row=0, column=0, sticky="w", padx=(5, 0), pady=(0, 5))
        self._form.grid(row=1, column=0, pady=(0, 25))
        self.b_reset_default.grid(row=1, column=1, sticky="nw", padx=(5, 0))

        self.name = name
        self.pane = pane
        self.is_valid: bool = True
        self.default: str = ""
        self.has_default_value: bool = True
        self.b_confirm = b_confirm
        self._form.bind("<KeyRelease>", lambda e: validation_func(self))

    @staticmethod
    def _any_nondefault_values(forms):
        return any(not form.has_default_value for form in forms)

    @staticmethod
    def _update_confirm_button(
        pane, b_confirm, lenient=False
    ):
        forms = (
            Form.crossword_forms if pane == "crossword" else Form.word_forms
        )
        if (
            Form._any_nondefault_values(forms) or lenient
        ) and all(form.is_valid for form in forms):
            b_confirm.configure(state="normal")
        else:
            b_confirm.configure(state="disabled")

    @classmethod
    def __new__(cls, *args, **kwargs) -> object:
        instance = super().__new__(cls)
        if kwargs["pane"] == "crossword":
            cls.crossword_forms.append(instance)
        else:
            cls.word_forms.append(instance)
        return instance

    def __str__(self):
        return str(self._form.get())

    def __len__(self):
        return len(str(self))

    def unfocus(self) -> None:
        self.master.focus_force()

    def wipe(self) -> None:
        self._form.delete(0, "end")

    def put(self, text: str, is_default=False) -> None:
        self.wipe()
        self._form.insert(0, text)
        if is_default:
            self.b_reset_default.configure(state="disabled")
            self.set_valid()
            self.has_default_value = True
            self._check_default()
            Form._update_confirm_button(self.pane, self.b_confirm)

    def set_state(self, state: str) -> None:
        self._label.configure(state=state)
        self._form.configure(state=state)

    def set_valid(self) -> None:
        self._form.configure(text_color=("black", "white"))
        self.is_valid = True

    def set_invalid(self) -> None:
        self._form.configure(text_color="red")
        self.is_valid = False

    def _check_default(self) -> None:
        if self.default != str(self):
            self.b_reset_default.configure(state="normal")
            self.has_default_value = False
        else:
            if self.default == "":
                self.set_invalid()
            self.b_reset_default.configure(state="disabled")
            self.has_default_value = True
        Form._update_confirm_button(self.pane, self.b_confirm)

    def set_default(self, text: str) -> None:
        self.default = text
        self.put(self.default, is_default=True)
        self.b_reset_default.configure(state="disabled")
        self.b_confirm.configure(state="disabled")


class EditorPage(CTkFrame, Addons):
    def __init__(self, master: Base) -> None:
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
        
        Form.crossword_forms = []
        Form.word_forms = []

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

    def _get_user_category_path(self) -> PathLike:
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

    def _handle_scroll(
        self, event: Event, container: CTkScrollableFrame
    ) -> None:
        scroll_region = container._parent_canvas.cget("scrollregion")
        viewable_height = container._parent_canvas.winfo_height()
        if (
            scroll_region
            and int(scroll_region.split(" ")[3]) > viewable_height
        ):
            container._parent_canvas.yview("scroll", -1 * event.delta, "units")

    def _toggle_forms(self, state, forms) -> None:
        for form in forms:
            form.set_state(state)
            form.set_valid()
            form.unfocus()

    def _reset_forms(self, forms, set_invalid=False) -> None:
        for form in forms:
            form.wipe()
            if set_invalid:
                form.set_invalid()

    def _set_form_defaults(self, *args, forms):  # len(args) == len(forms)
        for i, form in enumerate(forms):
            form.set_default(args[i])
    

class CrosswordPane(CTkFrame, Addons):
    def __init__(self, container: CTkFrame, master: EditorPage) -> None:
        super().__init__(
            container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            width=master._height * 0.5,
            height=master._width * 0.85,
            corner_radius=0,
        )
        self.name = "crossword"
        self.master = master
        self.crossword_block: Union[None, UserCrosswordBlock] = None
        self.grid(row=0, column=0, sticky="nsew", padx=(0, 1))

        self._set_fonts()
        self._make_content()
        self._place_content()
        self._toggle_forms("disabled", Form.crossword_forms)

    def _make_content(self) -> None:
        self.container = CTkFrame(
            self, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.container.grid_rowconfigure(1, minsize=self.master._height * 0.5)
        self.b_edit_container = CTkFrame(
            self.container, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.form_container = CTkFrame(
            self.container, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.form_container.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

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
            command=self._remove,
        )
        self.b_remove.configure(state="disabled")
        self.b_add = CTkButton(
            self.b_edit_container,
            text="+",
            width=40,
            height=30,
            font=self.TEXT_FONT,
            command=self._add,
        )

        self.b_confirm = CTkButton(
            self.form_container,
            text=_("Save"),
            font=self.TEXT_FONT,
            height=50,
            command=self._write,
        )
        self.b_confirm.configure(state="disabled")
        self.name_form = Form(
            self.form_container,
            "name",
            FormParser._parse_name_entry,
            pane=self.name,
            b_confirm=self.b_confirm,
        )
        self.symbol_form = Form(
            self.form_container,
            "symbol",
            FormParser._parse_symbol_entry,
            pane=self.name,
            b_confirm=self.b_confirm,
        )

        self.l_difficulty = CTkLabel(
            self.form_container,
            text=_("Difficulty"),
            font=self.BOLD_TEXT_FONT,
            text_color_disabled=(
                Colour.Light.TEXT_DISABLED,
                Colour.Dark.TEXT_DISABLED,
            ),
        )
        self.difficulties = [_("Easy"), _("Medium"), _("Hard"), _("Extreme")]
        self.opts_difficulty = CTkOptionMenu(
            self.form_container,
            font=self.TEXT_FONT,
            values=self.difficulties,
            command=self._on_difficulty_click,
        )
        self.opts_difficulty.set("")

        UserCrosswordBlock._populate(self)

    def _place_content(self) -> None:
        self.container.place(relx=0.5, rely=0.5, anchor="c")
        self.l_title.grid(row=0, column=0, columnspan=2, pady=(0, 25))
        self.preview.grid(row=1, column=0, padx=(0, 50))
        self.b_add.pack(side="right", anchor="e")
        self.b_remove.pack(side="right", anchor="e", padx=(81.5, 10))
        self.b_edit_container.grid(row=2, column=0, pady=(7.5, 0))
        self.name_form.grid(row=0, column=0)
        self.symbol_form.grid(row=1, column=0)
        self.l_difficulty.grid(
            row=2, column=0, sticky="w", padx=(5, 0), pady=(0, 5)
        )
        self.opts_difficulty.grid(row=3, column=0, pady=(0, 45), sticky="w")
        self.b_confirm.grid(row=4, column=0, sticky="w")
        self.form_container.grid(row=1, column=1, sticky="n")

    def _on_difficulty_click(self, difficulty):
        self.difficulty = DIFFICULTIES[self.difficulties.index(difficulty)]
        Form._update_confirm_button(self.name, self.b_confirm, lenient=True)

    def _toggle_forms(self, state, forms):
        self.master._toggle_forms(state, forms)
        self.l_difficulty.configure(state=state)
        self.opts_difficulty.configure(state=state)

    def _remove(self):
        if not GUIHelper.confirm_with_messagebox(self.name, delete_cword_or_word=True):
            return 
        
        fp = self.crossword_block.cwrapper.toplevel
        rmtree(fp)
        
        UserCrosswordBlock._set_all(UserCrosswordBlock._remove_block)
        UserCrosswordBlock._populate(self)
        self.master._reset_forms(Form.crossword_forms, set_invalid=True)
        self._toggle_forms("disabled", Form.crossword_forms)
        self.b_remove.configure(state="disabled")
        self.b_confirm.configure(state="disabled")
        self.master._set_form_defaults("", "", forms=Form.crossword_forms)
        self.opts_difficulty.set("")

    def _add(self) -> None:
        if Form._any_nondefault_values(Form.crossword_forms):
            if not GUIHelper.confirm_with_messagebox(self.name, confirm_cword_or_word_add=True):
                return 

        if (intvar := UserCrosswordBlock.selected_block):
            intvar.set(-1)
        self.b_remove.configure(state="disabled")
        self.b_confirm.configure(text=_("Add"))
        self._toggle_forms("normal", Form.crossword_forms)
        self.master._reset_forms(Form.crossword_forms, set_invalid=True)
        self.opts_difficulty.set(self.difficulties[0])
        self.difficulty = DIFFICULTIES[0]
        self.master._set_form_defaults("", "", forms=Form.crossword_forms)
        self.focus_force()

    def _write(self) -> None:
        print(str(self.name_form))
        print(str(self.symbol_form))
        print(self.difficulty)
        print("writing...")


class UserCrosswordBlock(CTkFrame, Addons, BlockUtils):
    blocks: List[object] = []
    selected_block: Union[None, IntVar]

    def __init__(
        self,
        master: CrosswordPane,
        container: CTkScrollableFrame,
        name: str,
        value: int,
    ):
        super().__init__(
            container,
            corner_radius=10,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            border_color=(Colour.Light.SUB, Colour.Dark.SUB),
            border_width=3,
        )
        self.master = master

        self.cwrapper: CrosswordWrapper = CrosswordWrapper(
            "user",
            name,
            language=Base.locale.language,
            value=value,
        )
        self.localised_difficulty: str = _(self.cwrapper.difficulty)

        self._set_fonts()
        self._make_content()
        self._place_content()

    @classmethod
    def _populate(cls, master: CrosswordPane) -> None:
        """Put all base crosswords in the user category into the crossword pane's
        scrollable frame. They can have no definitions.json file.
        """
        cls.selected_block = IntVar()
        cls.selected_block.set(-1)

        for i, crossword in enumerate(
            _get_base_crosswords(
                path.join(BASE_CWORDS_PATH, "user"), lenient=True
            )
        ):
            block: UserCrosswordBlock = cls(
                master,
                master.preview,
                crossword.name,
                i,
            )
            cls._put_block(block, side="top")

    def _make_content(self) -> None:
        self.tb_name = CTkTextbox(
            self,
            font=self.BOLD_TEXT_FONT,
            wrap="none",
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            height=10,
            width=125,
        )
        self.tb_name.insert(1.0, self.cwrapper.name)
        self.tb_name.configure(state="disabled")
        self.rb_selector = CTkRadioButton(
            self,
            text="",
            value=self.cwrapper.value,
            variable=UserCrosswordBlock.selected_block,
            corner_radius=0,
            height=50,
            command=self._on_selection,
        )

    def _place_content(self) -> None:
        self.tb_name.pack(side="left", padx=10, pady=10)
        self.rb_selector.pack(side="right", padx=10, pady=10)

    def _on_selection(self) -> None:
        if Form._any_nondefault_values(Form.crossword_forms):
            if not GUIHelper.confirm_with_messagebox(self.master.name, confirm_cword_or_word_add=True):
                return
        self.master.crossword_block = self
        self.master.difficulty = self.cwrapper.difficulty
        self.master._toggle_forms("normal", Form.crossword_forms)
        self.master.b_confirm.configure(text=_("Save"))
        self.master.master._reset_forms(Form.crossword_forms)
        self.master.master._set_form_defaults(
            self.cwrapper.name,
            chr(int(self.cwrapper.info["symbol"], 16)),
            forms=Form.crossword_forms,
        )
        self.master.opts_difficulty.set(self.localised_difficulty)
        self.master.b_remove.configure(state="normal")


class WordPane(CTkFrame, Addons):
    def __init__(self, container: CTkFrame, master: EditorPage) -> None:
        super().__init__(
            container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            width=master._height * 0.5,
            height=master._width * 0.85,
            corner_radius=0,
        )
        self.name = "word"
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
        self.form_container = CTkFrame(
            self.container, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )
        self.form_container.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

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
            self.form_container, text=_("Word"), font=self.BOLD_TEXT_FONT
        )
        self.e_word = CTkEntry(
            self.form_container,
            font=self.TEXT_FONT,
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            bg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )

        self.l_clue = CTkLabel(
            self.form_container, text=_("Clue"), font=self.BOLD_TEXT_FONT
        )
        self.e_clue = CTkEntry(
            self.form_container,
            font=self.TEXT_FONT,
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            bg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )

        self.b_confirm = CTkButton(
            self.form_container,
            text=_("Save"),
            font=self.TEXT_FONT,
            height=50,
        )

    def _place_content(self) -> None:
        self.container.place(relx=0.5, rely=0.5, anchor="c")
        self.l_title.grid(row=0, column=0, columnspan=2, pady=(0, 25))
        self.preview.grid(row=1, column=0, padx=(0, 50))
        self.b_add.pack(side="right", anchor="e")
        self.b_remove.pack(side="right", anchor="e", padx=(81.5, 10))
        self.b_edit_container.grid(row=2, column=0, pady=(7.5, 0))
        self.l_word.grid(row=0, column=0, sticky="w", padx=(5, 0), pady=(0, 5))
        self.e_word.grid(row=1, column=0, pady=(0, 25))
        self.l_clue.grid(row=2, column=0, sticky="w", padx=(5, 0), pady=(0, 5))
        self.e_clue.grid(row=3, column=0, pady=(0, 45))
        self.b_confirm.grid(row=4, column=0)
        self.form_container.grid(row=1, column=1, sticky="n")
