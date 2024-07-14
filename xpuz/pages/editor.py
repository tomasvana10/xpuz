"""GUI page for editing and making crosswords and their words. Only allows for
the creation and editing of new crosswords, not pre-installed ones.
"""

from json import dump
from os import PathLike, mkdir, path, rename
from shutil import rmtree
from tkinter import Event, IntVar
from typing import Callable, Dict, List, Optional, Union

from CTkToolTip import CTkToolTip
from customtkinter import (
    CTkButton,
    CTkEntry,
    CTkFrame,
    CTkImage,
    CTkLabel,
    CTkOptionMenu,
    CTkRadioButton,
    CTkScrollableFrame,
    CTkTextbox,
)
from pathvalidate import ValidationError, validate_filename
from PIL import Image
from regex import search

from xpuz.base import Addons, Base
from xpuz.constants import (
    BASE_CWORDS_PATH,
    DIFFICULTIES,
    DOC_CAT_PATH,
    EDITOR_DIM,
    EXPORT_IMG_PATH,
    FOLDER_DIS_IMG_PATH,
    FOLDER_IMG_PATH,
    IMPORT_IMG_PATH,
    NONLANGUAGE_PATTERN,
    PAGE_MAP,
    Colour,
)
from xpuz.import_export import Export, Import
from xpuz.td import CrosswordInfo
from xpuz.utils import (
    BlockUtils,
    GUIHelper,
    _doc_data_routine,
    _get_base_crosswords,
    _get_english_string,
    _make_category_info_json,
    _open_file,
)
from xpuz.wrappers import CrosswordWrapper


class Form(Addons):
    """Encapsulation of a CTkEntry, CTkLabel and CTkButton to construct a field
    to input data pertaining to a crossword's info or its words.

    Contains features such as default value detection, text colour modification
    based on incorrect value, and tooltips to provide constraints for input.
    """

    crossword_forms: List["Form"] = []
    word_forms: List["Form"] = []

    def __init__(
        self,
        master: CTkFrame,
        name: str,
        validation_func: Callable,
        pane_name: str,
        b_confirm: CTkButton,
        tooltip: str,
        pane_instance: Optional[bool] = None,
    ) -> None:
        self._set_fonts()

        # Have to encapsulate the frame within the instance here. If ``Form``
        # inherits ``CTkFrame``, this causes issues when defining ``__str__``
        # on older python versions.
        self._frame = CTkFrame(
            master, fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN)
        )

        self._label = CTkLabel(
            self._frame,
            text=_(name.title()),
            font=self.BOLD_TEXT_FONT,
            text_color_disabled=(
                Colour.Light.TEXT_DISABLED,
                Colour.Dark.TEXT_DISABLED,
            ),
        )
        self._form = CTkEntry(
            self._frame,
            font=self.TEXT_FONT,
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            bg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self._form._name = name
        self._tooltip = CTkToolTip(
            self._form, message=tooltip, delay=0.2, y_offset=12
        )
        self.b_reset_to_default = CTkButton(
            self._frame,
            text="↺",
            command=lambda: self.put(self.default, is_default=True),
            height=28,
            width=28,
            font=self.TEXT_FONT,
            state="disabled",
        )
        self._label.grid(row=0, column=0, sticky="w", padx=(5, 0), pady=(0, 5))
        self._form.grid(row=1, column=0, pady=(0, 25))
        self.b_reset_to_default.grid(row=1, column=1, sticky="nw", padx=(5, 0))

        self.master = master
        self.name = name
        self.pane_name = pane_name
        self.is_valid: bool = True
        self.default: str = ""
        self.has_default_value: bool = True
        self.b_confirm = b_confirm
        self.pane_instance = pane_instance
        self._form.bind("<KeyRelease>", lambda e: validation_func(self))

    @staticmethod
    def _any_nondefault_values(forms: List["Form"]) -> bool:
        """Return true if any form in ``forms`` contains a nondefault value."""
        return any(not form.has_default_value for form in forms)

    @staticmethod
    def _all_valid_values(forms: List["Form"]) -> bool:
        """Return true if any form in ``forms`` contains an invalid value."""
        return all(form.is_valid for form in forms)

    @classmethod
    def __new__(cls, *args, **kwargs) -> "Form":
        instance = super().__new__(cls)
        if kwargs["pane_name"] == "crossword":
            cls.crossword_forms.append(instance)
        else:
            cls.word_forms.append(instance)
        return instance

    def __str__(self) -> str:
        return str(self._form.get())

    def __len__(self) -> int:
        return len(str(self))

    def unbind_(self) -> None:
        self._form.unbind("<KeyRelease>")

    def grid(self, *args, **kwargs) -> None:
        """Wrapper method for gridding ``self._frame``."""
        self._frame.grid(*args, **kwargs)

    def _update_confirm_button(
        self, pane: CTkFrame, b_confirm: CTkButton
    ) -> None:
        """Enable or disable the confirm button based on the form content."""
        forms = (
            Form.crossword_forms if pane == "crossword" else Form.word_forms
        )
        has_selected_block = hasattr(
            getattr(self.pane_instance, "crossword_block", ""), "cwrapper"
        )
        if (
            Form._any_nondefault_values(forms)
            # An instance of the crossword pane has been provided, allowing this
            # method to check if the default difficulty is chosen or not.
            or self.pane_instance
            and has_selected_block
            and self.pane_instance.crossword_block.cwrapper.difficulty
            != self.pane_instance.difficulty
        ) and Form._all_valid_values(forms):
            # There is at least one form that is valid, and all of the forms are
            # valid, so the confirm button can be toggled on
            b_confirm.configure(state="normal")
        else:
            b_confirm.configure(state="disabled")

    def unfocus(self) -> None:
        """Remove focus from the entry by bringing focus to a pane."""
        self.master.focus_force()

    def focus(self) -> None:
        """Focus ``self._form``. Must be done after a small delay, or else the
        button press that triggered this method will be handled after it actually
        sets focus to the form.
        """
        self.master.master.after(5, self._form.focus_set)

    def wipe(self) -> None:
        """Remove all characters from ``self._form``."""
        self._form.delete(0, "end")

    def put(self, text: str, is_default: bool = False) -> None:
        """Wipe ``self._form`` and insert ``text``."""
        self.wipe()
        self._form.insert(0, text)
        if is_default:
            self.b_reset_to_default.configure(state="disabled")
            self.set_valid()  # Most likely already valid.
            self._check_default()

    def set_state(self, state: str) -> None:
        """Set the state of ``self._form`` and ``self._label``."""
        self._label.configure(state=state)
        self._form.configure(state=state)
        if state == "disabled":  # Also hide or show the tooltip
            self._tooltip.hide()
        else:
            self._tooltip.show()

    def set_valid(self) -> None:
        """Set the text colour of ``self._form`` to black or white, depending
        on the appearance mode, signifying it has a valid value.
        """
        self._form.configure(text_color=("black", "white"))
        self.is_valid = True

    def set_invalid(self) -> None:
        """Set the text colour of ``self._form`` to red, signifying it contains
        an incorrect value.
        """
        self._form.configure(text_color="red")
        self.is_valid = False

    def _check_default(self) -> None:
        """Update the reset field button, and check if the confirm button should
        be updated as well.
        """
        if self.default != str(
            self
        ):  # Nondefault value, allow the user to reset
            # it by enabling the reset button
            self.b_reset_to_default.configure(state="normal")
            self.has_default_value = False
        else:
            if self.default == "":  # An empty value is automatically invalid
                self.set_invalid()
            self.b_reset_to_default.configure(state="disabled")
            self.has_default_value = True
        # Since this method was called a result of the user modifying a field,
        # also update the confirm button
        self._update_confirm_button(self.pane_name, self.b_confirm)

    def set_default(self, text: Union[str, int]) -> None:
        """Update ``self.default`` to ``text``, and put it into the entry."""
        self.default = str(text)
        self.put(self.default, is_default=True)
        # The value in ``self`` must now be the default value, so prevent the
        # user from resetting to default or pressing the confirm button
        self.b_reset_to_default.configure(state="disabled")
        self.b_confirm.configure(state="disabled")


class FormParser:
    @staticmethod
    def _parse_name(form: Form) -> None:
        """Parse the crossword name form contents."""
        try:
            # Detect filename validation errors to prevent OS errors when editing
            if len(form) <= 32 and validate_filename(str(form)) is None:
                form.set_valid()
            else:
                form.set_invalid()
        except ValidationError:
            form.set_invalid()
        form._check_default()

    @staticmethod
    def _parse_symbol(form: Form) -> None:
        """Parse the crossword symbol form contents."""
        if len(form) == 1:
            form.set_valid()
        else:
            form.set_invalid()
        form._check_default()

    @staticmethod
    def _parse_word(form: Form) -> None:
        """Parse a crossword's word form contents."""
        if (
            len(form) < 1
            or len(form) > 32
            or "\\" in str(form)
            or bool(
                search(NONLANGUAGE_PATTERN, str(form))
            )  # Non-lang char present
        ):
            form.set_invalid()
        else:
            form.set_valid()
        form._check_default()

    @staticmethod
    def _parse_clue(form: Form) -> None:
        """Parse a crossword clue form contents."""
        if len(form) < 1 or "\\" in str(form):
            form.set_invalid()
        else:
            form.set_valid()
        form._check_default()


class EditorPage(CTkFrame, Addons):
    """Base page for ``editor.py``. Consists of some utility methods required
    only by CrosswordPane and WordPane, as well as the title bar and contains
    for the aforementioned two classes.
    """

    def __init__(self, master: Base) -> None:
        super().__init__(
            Base.base_container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )
        self.master = master
        self.master._set_dim(dim=EDITOR_DIM)
        self._set_fonts()
        self.master.update()
        self._width, self._height = (
            self.master.winfo_width(),
            self.master.winfo_height(),
        )
        self.fp: PathLike = self._get_user_category_path()
        self.scaling: float = float(Base.cfg.get("m", "scale"))

        # Reset the form arrays to prevent duplicates when opening ``EditorPage``
        # more than once in a single instance
        Form.crossword_forms = []
        Form.word_forms = []

        self.grid_rowconfigure(0, minsize=self._height * 0.15, weight=1)
        self.grid_rowconfigure(1, minsize=self._height * 0.85, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.master.bind("<Return>", lambda e: self._handle_enter())

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

        # Instantiating both the left and right columns/panes for editing
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
                "HomePage",
                self.master,
                _(PAGE_MAP["HomePage"]),
                condition=Form._any_nondefault_values(Form.crossword_forms)
                or Form._any_nondefault_values(Form.word_forms),
                confirmation={"exiting_with_nondefault_fields": True},
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

    def unbind_(self) -> None:
        """Remove bindings which can be detected on different pages."""
        self.crossword_pane.preview.unbind_all("<MouseWheel>")
        for form in [*Form.crossword_forms, *Form.word_forms]:
            form.unbind_()
        self.master.unbind("<Return>")

    def _get_user_category_path(self) -> PathLike:
        """Find where to access categories from, whether that is in the package
        or in the system documents.
        """
        fp: PathLike = path.join(BASE_CWORDS_PATH, "user")  # Assume the system
        # documents don't exist
        if _doc_data_routine(
            doc_callback=lambda: mkdir(DOC_CAT_PATH),
            local_callback=lambda: mkdir(fp),
            sublevel=DOC_CAT_PATH,
        ):  # Func returned true, meaning the system documents are accessible,
            # so reassign fp to the document category path
            fp = DOC_CAT_PATH
        _make_category_info_json(fp, "#FFFFFF")
        return fp

    def _handle_scroll(self, event: Event) -> None:
        """Scroll one of the two scrollable frames depending on the user's
        cursor position.
        """
        container: CTkFrame = (
            self.crossword_pane.preview
            # User's cursor is on the left half of the screen
            if event.x_root
            - self.master.winfo_rootx()  # Account for window offset
            <= EDITOR_DIM[0] * self.scaling / 2
            # Right half
            else self.word_pane.preview
        )
        scroll_region = container._parent_canvas.cget("scrollregion")
        viewable_height = container._parent_canvas.winfo_height()
        if (
            scroll_region
            and int(scroll_region.split(" ")[3]) > viewable_height
        ):
            container._parent_canvas.yview("scroll", -1 * event.delta, "units")

    def _handle_enter(self) -> None:
        focused_form_name = self.master.focus_get().master._name
        crossword_pane_button = self.crossword_pane.b_confirm
        word_pane_button = self.word_pane.b_confirm

        if (
            focused_form_name in ["name", "symbol"]
            and crossword_pane_button.cget("state") == "normal"
        ):
            crossword_pane_button.invoke()
        elif (
            focused_form_name in ["word", "clue"]
            and word_pane_button.cget("state") == "normal"
        ):
            word_pane_button.invoke()

    def _toggle_forms(self, state: str, forms: List[Form]) -> None:
        """Enable or disable all the forms in ``forms``."""
        for form in forms:
            form.set_state(state)
            form.set_valid()
            form.unfocus()

    def _reset_forms(
        self, forms: List[Form], set_invalid: bool = False
    ) -> None:
        """Remove all the content from the forms in ``forms``."""
        for form in forms:
            form.wipe()
            if set_invalid:  # Set to true when adding a new crossword
                form.set_invalid()

    def _set_form_defaults(self, *args, forms: List[Form]):
        """Set the default of each form in ``forms`` to the respective value
        in ``args``. Requires len(args) to be equal to len(forms).
        """
        for i, form in enumerate(forms):
            form.set_default(args[i])

    def _write_data(self, toplevel: PathLike, data: Dict, type_: str):
        """Write ``data`` to a crossword's info.json or definitions.json."""
        file = "info.json" if type_ == "info" else "definitions.json"
        with open(path.join(toplevel, file), "w") as f:
            dump(data, f, indent=4)


class CrosswordPane(CTkFrame, Addons):
    """The left half of ``EditorPage``. Contains a preview of all the user's
    crosswords, providing the ability to edit them or add new ones.
    """

    def __init__(self, container: CTkFrame, master: EditorPage) -> None:
        super().__init__(
            container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            width=master._height * 0.5,
            height=master._width * 0.85,
            corner_radius=0,
        )
        self.pane_name: str = "crossword"
        self.mode: str = ""  # "edit" or "add"
        self.master = master
        # Updated by ``UserCrosswordBlock``
        self.crossword_block: Union[None, UserCrosswordBlock] = None
        self.difficulty = ""
        self.grid(row=0, column=0, sticky="nsew", padx=(0, 1))
        # This is done not to remove any blocks, but remove the empty info label
        # from the UserCrosswordBlock.blocks array if it was there when the user
        # exited ``EditorPage`` (in the same instance)
        UserCrosswordBlock._set_all(UserCrosswordBlock._remove_block)

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
            self.container,
            text=_("Your Crosswords"),
            font=self.SUBHEADING_FONT,
        )

        self.preview = CTkScrollableFrame(
            self.container,
            orientation="vertical",
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            scrollbar_button_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            width=250,
        )
        self.preview.bind_all(
            "<MouseWheel>",
            lambda e: self.master._handle_scroll(e),
        )

        self.explorer_img_states = (
            CTkImage(Image.open(FOLDER_IMG_PATH), size=(14, 14)),
            CTkImage(Image.open(FOLDER_DIS_IMG_PATH), size=(14, 14)),
        )
        self.b_explorer = CTkButton(
            self.b_edit_container,
            text="",
            width=40,
            height=30,
            font=self.TEXT_FONT,
            command=lambda: _open_file(self.crossword_block.cwrapper.toplevel),
            state="disabled",
            image=self.explorer_img_states[1],
        )

        self.b_export = CTkButton(
            self.b_edit_container,
            text="",
            width=40,
            height=30,
            image=CTkImage(Image.open(EXPORT_IMG_PATH), size=(14, 14)),
            font=self.TEXT_FONT,
            command=self._export,
        )
        self.b_import = CTkButton(
            self.b_edit_container,
            text="",
            width=40,
            height=30,
            image=CTkImage(Image.open(IMPORT_IMG_PATH), size=(14, 14)),
            font=self.TEXT_FONT,
            command=self._import,
        )
        self.b_remove = CTkButton(
            self.b_edit_container,
            text="-",
            width=40,
            height=30,
            font=self.TEXT_FONT,
            command=self._remove,
            state="disabled",
        )
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
            text=_("Save") + " [↵]",
            font=self.TEXT_FONT,
            height=50,
            command=self._write,
            state="disabled",
        )
        self.name_form = Form(
            self.form_container,
            "name",
            FormParser._parse_name,
            pane_name=self.pane_name,
            b_confirm=self.b_confirm,
            tooltip=_("length >= 1 and valid OS file name"),
            pane_instance=self,
        )
        self.symbol_form = Form(
            self.form_container,
            "symbol",
            FormParser._parse_symbol,
            pane_name=self.pane_name,
            b_confirm=self.b_confirm,
            tooltip=_("length == 1"),
            pane_instance=self,
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
            command=self._update_difficulty,
        )
        self.opts_difficulty.set("")

        UserCrosswordBlock._populate(self)

    def _place_content(self) -> None:
        self.container.place(relx=0.5, rely=0.5, anchor="c")
        self.l_title.grid(row=0, column=0, columnspan=2, pady=(0, 25))
        self.preview.grid(row=1, column=0, padx=(0, 40), sticky="nsew")
        self.b_explorer.pack(side="left", padx=(0, 7.5))
        self.b_export.pack(side="left", padx=(0, 7.5))
        self.b_import.pack(side="left", padx=(0, 48.4))
        self.b_add.pack(side="left", padx=(0, 7.5))
        self.b_remove.pack(side="left", padx=(0, 7.5))
        self.b_edit_container.grid(row=2, column=0, pady=(7.5, 0), sticky="w")
        self.name_form.grid(row=0, column=0)
        self.symbol_form.grid(row=1, column=0)
        self.l_difficulty.grid(
            row=2, column=0, sticky="w", padx=(5, 0), pady=(0, 5)
        )
        self.opts_difficulty.grid(row=3, column=0, pady=(0, 45), sticky="w")
        self.b_confirm.grid(row=4, column=0, sticky="w", pady=(30, 0))
        self.form_container.grid(row=1, column=1, sticky="n")

    def _export(self) -> None:
        """Export all of the user's crosswords into a json file."""
        if isinstance(UserCrosswordBlock.blocks[0], CTkLabel):
            return GUIHelper.show_messagebox(no_crosswords_to_export_err=True)

        Export(UserCrosswordBlock.blocks).start()

    def _import(self) -> None:
        """Allow the user to add new crosswords from a JSON file that was
        exported through xpuz.
        """
        if Form._any_nondefault_values(Form.crossword_forms):
            if not GUIHelper.confirm_with_messagebox(
                importing_with_nondefault_fields=True
            ):
                return None
        imp = Import(self, self.master.fp)
        imp.start()

        self._reset()
        self.b_add.configure(state="normal")
        UserCrosswordBlock._populate(self, imp.imported_crossword_fullnames)
        self.master.word_pane._reset()
        for block in UserCrosswordBlock.blocks:
            if hasattr(block, "_flash"):
                block._flash()

    def _update_difficulty(self, difficulty: str) -> None:
        """Find the english version of ``difficulty`` and update
        ``self.difficulty``.
        """
        self.difficulty = _get_english_string(
            DIFFICULTIES, self.difficulties, difficulty
        )
        Form.crossword_forms[0]._update_confirm_button(
            self.pane_name, self.b_confirm
        )

    def _toggle_forms(self, state: str, forms: List[Form]) -> None:
        """An extension to the method in ``EditorPage`` of the same name to
        configure the state of the difficulty optionmenu.
        """
        self.master._toggle_forms(state, forms)
        self.l_difficulty.configure(state=state)
        self.opts_difficulty.configure(state=state)

    def _remove(self) -> None:
        """Remove a crossword from the OS file system."""
        if not GUIHelper.confirm_with_messagebox(  # Provide confirmation
            self.pane_name, delete_cword_or_word=True
        ):
            return

        fp = self.crossword_block.cwrapper.toplevel
        rmtree(fp)

        self._reset()
        self.b_add.configure(state="normal")
        UserCrosswordBlock._populate(self)  # Regenerate new crossword preview
        self.master.word_pane._reset()

    def _add(self) -> None:
        """Default all forms to empty, and allow the user to define the data for
        a new crossword.
        """
        if Form._any_nondefault_values(Form.crossword_forms):
            if not GUIHelper.confirm_with_messagebox(
                self.pane_name, confirm_cword_or_word_add=True
            ):
                return

        intvar = UserCrosswordBlock.selected_block
        if intvar:
            intvar.set(-1)  # Remove existing crossword selection

        self.mode = "add"
        self.crossword_block = None
        self.master.word_pane._reset()
        self.l_title.configure(
            text=_("Your Crosswords") + " ({})".format(_("Adding"))
        )
        self.b_remove.configure(state="disabled")
        self.b_confirm.configure(
            text=_("Add") + " [↵]",
        )
        Form.crossword_forms[0].focus()
        self._toggle_forms("normal", Form.crossword_forms)
        self.master._reset_forms(Form.crossword_forms, set_invalid=True)
        # Default the difficulty to Easy
        self.opts_difficulty.set(self.difficulties[0])
        self.difficulty = DIFFICULTIES[0]
        self.master._set_form_defaults("", "", forms=Form.crossword_forms)
        self.focus_force()

    def _get_cword_dirname(self, name: str) -> str:
        """Return the final name of the updated/new crossword's directory,
        appending a hyphen (if the user specified name doesn't end in one) and
        the casefolded difficulty.
        """
        dir_name = name
        if not any(
            dir_name.endswith(diff.casefold()) for diff in DIFFICULTIES
        ):
            hyphen_char = "" if dir_name.endswith("-") else "-"
            dir_name += hyphen_char
            dir_name += self.difficulty.casefold()

        return dir_name

    def _write(self) -> None:
        """Update/write a crossword based on form data."""
        if not Form._all_valid_values(Form.crossword_forms):
            return
        difficulty = DIFFICULTIES.index(self.difficulty)
        symbol = hex(ord(str(self.symbol_form)))
        name = str(self.name_form)
        translated_name = str(self.name_form)

        dir_name = self._get_cword_dirname(name)

        if self.mode == "add":
            # Must make a new info, and not read it from the crossword wrapper
            info = CrosswordInfo(
                total_definitions=0,
                difficulty=difficulty,
                symbol=symbol,
                name=name,
                translated_name=translated_name,
                category="user",
            )

            toplevel = path.join(self.master.fp, dir_name)
            try:
                mkdir(toplevel)
            except FileExistsError:
                return GUIHelper.show_messagebox(crossword_exists_err=True)
            # Must also create info and definitions as this is a fresh crossword
            # that doesn't contain them
            self.master._write_data(toplevel, info, "info")
            self.master._write_data(toplevel, {}, "definitions")

        elif self.mode == "edit":
            # Modify existing crossword wrapper info
            cwrapper = self.crossword_block.cwrapper
            info = cwrapper.info
            info["difficulty"] = difficulty
            info["symbol"] = symbol
            info["name"] = name
            info["translated_name"] = translated_name

            toplevel = cwrapper.toplevel
            prior_level = path.dirname(toplevel)

            # Info was updated, to write it
            self.master._write_data(toplevel, info, "info")
            # Join toplevel of crossword with new name to rename it
            try:
                rename(toplevel, path.join(prior_level, dir_name))
            except FileExistsError:
                return GUIHelper.show_messagebox(crossword_exists_err=True)

        self.master.word_pane._reset()
        self._reset()
        self.b_add.configure(state="normal")
        UserCrosswordBlock._populate(self)

    def _reset(self) -> None:
        """Revert all the states of the widgets in ``CrosswordPane`` to their
        default values.
        """
        UserCrosswordBlock._set_all(UserCrosswordBlock._remove_block)
        self.l_title.configure(text=_("Your Crosswords"))
        self.b_explorer.configure(state="disabled")
        self.b_explorer.configure(image=self.explorer_img_states[1])
        self.master._reset_forms(Form.crossword_forms, set_invalid=True)
        self._toggle_forms("disabled", Form.crossword_forms)
        self.b_confirm.configure(text=_("Save") + " [↵]")
        self.b_remove.configure(state="disabled")
        self.b_add.configure(state="disabled")
        self.b_confirm.configure(state="disabled")
        self.opts_difficulty.set("")
        self.master._set_form_defaults("", "", forms=Form.crossword_forms)
        self.focus_force()


class UserCrosswordBlock(CTkFrame, Addons, BlockUtils):
    """A small frame that displays a crossword's name and provides a radiobutton
    to select it.

    See browser.py for implementations similar to this.
    """

    blocks: List["UserCrosswordBlock"] = []
    selected_block: Union[None, IntVar] = None

    def __init__(
        self,
        master: CrosswordPane,
        container: CTkScrollableFrame,
        name: str,
        value: int,
        flash: bool = False,
    ):
        super().__init__(
            container,
            corner_radius=10,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            border_color=(Colour.Light.SUB, Colour.Dark.SUB),
            border_width=3,
        )
        self.master = master
        self.flash = flash

        # The most useful thing I have decided to code in this project
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

    def _flash(self) -> None:
        if not self.flash:
            return
        self.master.master.update_idletasks()
        self.master.master.master.after(150, self.configure(fg_color="green"))
        self.master.master.master.after(
            150, self.configure(fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN))
        )

    @classmethod
    def _populate(
        cls, master: CrosswordPane, flash_these: Optional[List[str]] = None
    ) -> None:
        """Put all of the user crosswords into ``master.preview``
        (CTkScrollableFrame) as user crossword blocks.
        """
        # Ensure the class' IntVar is ready, and remove any existing selection
        cls.selected_block: IntVar = IntVar()
        cls.selected_block.set(-1)

        for i, crossword in enumerate(
            _get_base_crosswords(
                path.join(BASE_CWORDS_PATH, "user"), allow_empty_defs=True
            )
        ):
            block: UserCrosswordBlock = cls(
                master,
                master.preview,
                crossword.name,
                i,
                flash=flash_these and crossword.name in flash_these,
            )
            cls._put_block(block, side="top")

        if len(UserCrosswordBlock.blocks) == 0:
            # Add a label that indicates there are no user crosswords
            l_empty_info = CTkLabel(
                master.preview,
                text=_("Press")
                + ' "+" '
                + _("to add a")
                + "\n"
                + _("new crossword."),
                font=master.ITALIC_TEXT_FONT,
            )
            cls._put_block(l_empty_info, side="top")

    def _make_content(self) -> None:
        self.tb_name = CTkTextbox(
            self,
            font=self.BOLD_TEXT_FONT,
            wrap="none",
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            height=10,
            width=165,
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
        self.rb_selector.pack(side="left", padx=10, pady=10)

    def _on_selection(self) -> None:
        """Apply the information of this block to the crossword forms, and
        configure the widget states appropriately.
        """
        # Currently, there are nondefault values. Ensure the user wants to
        # override these values with a confirmation
        if Form._any_nondefault_values(Form.crossword_forms):
            if not GUIHelper.confirm_with_messagebox(
                self.master.pane_name, confirm_cword_or_word_add=True
            ):
                return

        self.master.mode = "edit"
        self.master.l_title.configure(
            text=_("Your Crosswords") + " ({})".format(_("Editing"))
        )
        self.master.crossword_block = self
        self.master.b_explorer.configure(state="normal")
        self.master.b_explorer.configure(
            image=self.master.explorer_img_states[0]
        )
        self.master.difficulty = self.cwrapper.difficulty
        self.master._toggle_forms("normal", Form.crossword_forms)
        self.master.b_confirm.configure(text=_("Save") + " [↵]")
        self.master.master._reset_forms(Form.crossword_forms)
        self.master.master._set_form_defaults(
            self.cwrapper.name,
            chr(int(self.cwrapper.info["symbol"], 16)),
            forms=Form.crossword_forms,
        )
        Form.crossword_forms[0].focus()
        self.master.opts_difficulty.set(self.localised_difficulty)
        self.master.b_remove.configure(state="normal")
        self.master.master.word_pane._reset()
        self.master.master.word_pane.b_add.configure(state="normal")
        UserWordBlock._set_all(UserWordBlock._remove_block)
        UserWordBlock._populate(
            self.master.master.word_pane, self.cwrapper.definitions
        )


class WordPane(CTkFrame, Addons):
    """The right half of ``EditorPage``. Contains a preview of all the words
    present in the currently selected crossword.
    """

    def __init__(self, container: CTkFrame, master: EditorPage) -> None:
        super().__init__(
            container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            width=master._height * 0.5,
            height=master._width * 0.85,
            corner_radius=0,
        )
        self.pane_name = "word"
        self.master = master
        self.word = (
            ""  # The currently selected word, unchanged by editing until
        )
        # the word is saved and reselected
        self.grid(row=0, column=1, sticky="nsew")

        self._set_fonts()
        self._make_content()
        self._place_content()
        self.master._toggle_forms("disabled", Form.word_forms)

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
        self.form_container.grid_rowconfigure((0, 1, 2), weight=1)

        self.l_title = CTkLabel(
            self.container, text=_("Your Words"), font=self.SUBHEADING_FONT
        )

        self.preview = CTkScrollableFrame(
            self.container,
            orientation="vertical",
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            scrollbar_button_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
            width=250,
        )

        self.b_remove = CTkButton(
            self.b_edit_container,
            text="-",
            width=40,
            height=30,
            font=self.TEXT_FONT,
            state="disabled",
            command=self._remove,
        )
        self.b_add = CTkButton(
            self.b_edit_container,
            text="+",
            width=40,
            height=30,
            font=self.TEXT_FONT,
            state="disabled",
            command=self._add,
        )

        self.b_confirm = CTkButton(
            self.form_container,
            text=_("Save") + " [↵]",
            font=self.TEXT_FONT,
            height=50,
            state="disabled",
            command=lambda: self.master.master.after(15, self._write),
        )
        self.word_form = Form(
            self.form_container,
            "word",
            FormParser._parse_word,
            pane_name=self.pane_name,
            b_confirm=self.b_confirm,
            tooltip=_(
                "length >= 1 and length <= 32 and is a language character"
            ),
        )

        self.clue_form = Form(
            self.form_container,
            "clue",
            FormParser._parse_clue,
            pane_name=self.pane_name,
            b_confirm=self.b_confirm,
            tooltip=_("length >= 1"),
        )

    def _place_content(self) -> None:
        self.container.place(relx=0.5, rely=0.5, anchor="c")
        self.l_title.grid(row=0, column=0, columnspan=2, pady=(0, 25))
        self.preview.grid(row=1, column=0, padx=(0, 40), sticky="nsew")
        self.b_remove.pack(side="right", anchor="e")
        self.b_add.pack(side="right", anchor="e", padx=(81.5, 10))
        self.b_edit_container.grid(
            row=2, column=0, pady=(7.5, 0), padx=(60, 0)
        )
        self.word_form.grid(row=0, column=0)
        self.clue_form.grid(row=1, column=0)
        self.b_confirm.grid(row=2, column=0, sticky="w", pady=(135, 0))
        self.form_container.grid(row=1, column=1, sticky="n")

    def _add(self) -> None:
        """Default all forms to empty, and allow the user to define the data for
        a new/existing word.
        """
        if Form._any_nondefault_values(Form.word_forms):
            if not GUIHelper.confirm_with_messagebox(
                self.pane_name, confirm_cword_or_word_add=True
            ):
                return

        intvar = UserWordBlock.selected_block
        if intvar:
            intvar.set(-1)

        self.mode = "add"
        self.l_title.configure(
            text=_("Your Words") + " ({})".format(_("Adding"))
        )
        Form.word_forms[0].focus()
        self.b_remove.configure(state="disabled")
        self.b_confirm.configure(text=_("Add") + " [↵]")
        self.master._toggle_forms("normal", Form.word_forms)
        self.master._reset_forms(Form.word_forms, set_invalid=True)
        self.master._set_form_defaults("", "", forms=Form.word_forms)
        self.focus_force()

    def _remove(self) -> None:
        """Remove a word/clue pair from the crossword's definitions"""
        if not GUIHelper.confirm_with_messagebox(
            self.pane_name, delete_cword_or_word=True
        ):
            return

        cwrapper = self.master.crossword_pane.crossword_block.cwrapper
        definitions = cwrapper.definitions
        del definitions[self.word]
        self.master._write_data(cwrapper.toplevel, definitions, "definitions")

        self._reset()
        self.b_add.configure(state="normal")
        UserWordBlock._populate(self, definitions)

    def _write(self) -> None:
        """Update a word or write a new one to a crossword's definitions."""
        cwrapper = self.master.crossword_pane.crossword_block.cwrapper
        definitions = cwrapper.definitions

        if self.mode == "add":
            if str(self.word_form) in definitions.keys():
                return GUIHelper.show_messagebox(word_exists_err=True)

            definitions[str(self.word_form)] = str(self.clue_form)

        elif self.mode == "edit":
            # For simplicity, the original word is just deleted, and a new pair
            # is created
            del definitions[self.word]
            definitions[str(self.word_form)] = str(self.clue_form)

        self.master._write_data(cwrapper.toplevel, definitions, "definitions")
        self._reset()
        UserWordBlock._populate(self, definitions)
        self.b_add.configure(state="normal")

    def _reset(self) -> None:
        """Revert all the states of the widgets in ``WordPane`` to their
        default values.
        """
        self.l_title.configure(text=_("Your Words"))
        UserWordBlock._set_all(UserWordBlock._remove_block)
        self.master._reset_forms(Form.word_forms, set_invalid=True)
        self.master._toggle_forms("disabled", Form.word_forms)
        self.master._set_form_defaults("", "", forms=Form.word_forms)
        self.b_confirm.configure(text=_("Save") + " [↵]")
        self.b_confirm.configure(state="disabled")
        self.b_add.configure(state="disabled")
        self.b_remove.configure(state="disabled")


class UserWordBlock(CTkFrame, Addons, BlockUtils):
    """A small frame that displays a crossword's word and provides a radiobutton
    to select it.

    See browser.py for implementations similar to this.
    """

    blocks: List[object] = []
    selected_block: Union[None, IntVar] = None

    def __init__(
        self,
        master: WordPane,
        container: CTkScrollableFrame,
        word: str,
        clue: str,
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
        self.word = word
        self.clue = clue
        self.value = value

        self._set_fonts()
        self._make_content()
        self._place_content()

    @classmethod
    def _populate(cls, master: WordPane, definitions: Dict[str, str]) -> None:
        """Put all of the words of a user crossword into ``master.preview``
        (CTkScrollableFrame) as user word blocks.
        """
        cls.selected_block = IntVar()
        cls.selected_block.set(-1)

        for i, (word, clue) in enumerate(
            sorted(definitions.items(), key=lambda item: item[0])
        ):
            block: UserWordBlock = cls(
                master,
                master.preview,
                word,
                clue,
                i,
            )
            cls._put_block(block, side="top")

        if len(UserWordBlock.blocks) == 0:
            l_empty_info = CTkLabel(
                master.preview,
                text=_("Press")
                + ' "+" '
                + _("to add a")
                + "\n"
                + _("new word."),
                font=master.ITALIC_TEXT_FONT,
            )
            cls._put_block(l_empty_info, side="top")

    def _make_content(self) -> None:
        self.tb_name = CTkTextbox(
            self,
            font=self.BOLD_TEXT_FONT,
            wrap="none",
            fg_color=(Colour.Light.SUB, Colour.Dark.SUB),
            height=10,
            width=165,
        )
        self.tb_name.insert(1.0, self.word)
        self.tb_name.configure(state="disabled")
        self.rb_selector = CTkRadioButton(
            self,
            text="",
            value=self.value,
            variable=UserWordBlock.selected_block,
            corner_radius=0,
            height=50,
            command=self._on_selection,
        )

    def _place_content(self) -> None:
        self.tb_name.pack(side="left", padx=10, pady=10)
        self.rb_selector.pack(side="left", padx=10, pady=10)

    def _on_selection(self) -> None:
        """Apply the information of this block to the word forms, and
        configure the widget states appropriately.
        """
        if Form._any_nondefault_values(Form.word_forms):
            if not GUIHelper.confirm_with_messagebox(
                self.master.pane_name, confirm_cword_or_word_add=True
            ):
                return

        self.master.mode = "edit"
        self.master.word = self.word
        self.master.l_title.configure(
            text=_("Your Words") + " ({})".format(_("Editing"))
        )
        Form.word_forms[0].focus()
        self.master.master._toggle_forms("normal", Form.word_forms)
        self.master.b_confirm.configure(text=_("Save") + " [↵]")
        self.master.master._reset_forms(Form.word_forms)
        self.master.master._set_form_defaults(
            self.word,
            self.clue,
            forms=Form.word_forms,
        )
        self.master.b_remove.configure(state="normal")
