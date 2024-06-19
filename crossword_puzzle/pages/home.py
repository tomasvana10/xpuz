"""Default GUI page for crossword_puzzle. Provides config options and routing
buttons to other available pages.
"""

from typing import List

from babel import Locale, numbers
from customtkinter import (
    CTkButton,
    CTkFrame,
    CTkImage,
    CTkLabel,
    CTkOptionMenu,
    set_appearance_mode,
    set_widget_scaling,
)
from PIL import Image

from crossword_puzzle.base import Addons, Base
from crossword_puzzle.constants import (
    BASE_ENG_APPEARANCES,
    BASE_ENG_CWORD_QUALITIES,
    CWORD_IMG_DARK_PATH,
    CWORD_IMG_LIGHT_PATH,
    FS_IMG_DARK_PATH,
    FS_IMG_LIGHT_PATH,
    Colour,
)
from crossword_puzzle.utils import GUIHelper, _update_cfg


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

        self.main_container = CTkFrame(
            self.container,
            corner_radius=0,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )

        self.button_container = CTkFrame(
            self.main_container,
            fg_color=(Colour.Light.MAIN, Colour.Dark.MAIN),
        )

    def _place_containers(self) -> None:
        self.container.pack(fill="both", expand=True)
        self.button_container.place(relx=0.5, rely=0.7, anchor="c")
        self.settings_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid(row=0, column=0, sticky="nsew")

    def _make_content(self) -> None:
        self.l_title = CTkLabel(
            self.main_container,
            text=_("Crossword Puzzle"),
            font=self.TITLE_FONT,
        )

        self.b_fullscreen = CTkLabel(
            self.main_container,
            text="",
            image=CTkImage(
                light_image=Image.open(FS_IMG_LIGHT_PATH),
                dark_image=Image.open(FS_IMG_DARK_PATH),
            ),
        )
        self.b_fullscreen.bind(
            "<Button-1>", lambda e: self.master._toggle_fullscreen()
        )

        self.cword_img = CTkLabel(
            self.main_container,
            text="",
            image=CTkImage(
                light_image=Image.open(CWORD_IMG_LIGHT_PATH),
                dark_image=Image.open(CWORD_IMG_DARK_PATH),
                size=(453, 154),
            ),
        )

        self.b_open_browser = CTkButton(
            self.button_container,
            text=_("Browser"),
            command=lambda: self._route(
                "BrowserPage", self.master, _("Crossword Browser")
            ),
            width=150,
            height=50,
            font=self.TEXT_FONT,
        )

        self.b_open_editor = CTkButton(
            self.button_container,
            text=_("Editor"),
            command=lambda: self._route(
                "EditorPage", self.master, _("Crossword Editor")
            ),
            width=150,
            height=50,
            font=self.TEXT_FONT,
        )

        self.b_close_app = CTkButton(
            self.button_container,
            text=_("Exit"),
            command=self.master._exit_handler,
            width=150,
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
            text=_("Language"),
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
        self.b_fullscreen.place(x=20, y=20, anchor="c")
        self.b_open_browser.grid(
            row=0, column=0, sticky="nsew", padx=10, pady=10
        )
        self.b_open_editor.grid(
            row=0, column=1, sticky="nsew", padx=10, pady=10
        )
        self.b_close_app.grid(
            row=1, column=0, columnspan=2, sticky="ns", padx=10, pady=10
        )
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
            return GUIHelper.show_messagebox(same_appearance=True)

        set_appearance_mode(eng_appearance_name)
        _update_cfg(Base.cfg, "m", "appearance", eng_appearance_name)

    def change_scale(self, scale: str) -> None:
        """Ensures the user is not selecting the same scale, then sets the scale."""
        scale = float(numbers.parse_decimal(scale, locale=Base.locale))
        if scale == float(Base.cfg.get("m", "scale")):
            return GUIHelper.show_messagebox(same_scale=True)

        set_widget_scaling(scale)
        _update_cfg(Base.cfg, "m", "scale", str(scale))
        self.master._set_dim()

    def change_lang(self, lang: str) -> None:
        """Ensures the user is not selecting the same language, then creates a
        new ``locale`` variable based on the English name of the language
        (retrieved from ``self.localised_lang_db``). The method then installs a
        new set of translations with gettext and regenerates the content of the
        GUI.
        """
        lang = Base.lang_info[0][lang]
        if lang == Base.cfg.get("m", "language"):
            return GUIHelper.show_messagebox(same_lang=True)

        Base.locale = Locale.parse(lang)
        GUIHelper._install_translations(Base.locale)
        _update_cfg(Base.cfg, "m", "language", lang)

        self._route("HomePage", self.master, _("Crossword Puzzle"))

    def change_crossword_quality(self, quality: str) -> None:
        """Ensures the user is not selecting the same crossword quality, then
        updates the crossword quality in ``config.ini``.
        """
        eng_quality_name: str = BASE_ENG_CWORD_QUALITIES[
            self.cword_qualities.index(quality)
        ]
        if eng_quality_name == Base.cfg.get("m", "cword_quality"):
            return GUIHelper.show_messagebox(same_quality=True)

        _update_cfg(Base.cfg, "m", "cword_quality", eng_quality_name)
