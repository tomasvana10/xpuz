from __future__ import annotations

from configparser import ConfigParser
from platform import system
from typing import Dict, List, Tuple

from babel import Locale
from customtkinter import (
    CTk,
    CTkFont,
    CTkFrame,
    set_appearance_mode,
    set_default_color_theme,
    set_widget_scaling,
)

from crossword_puzzle.constants import DIM, LOGO_PATH, PAGE_MAP
from crossword_puzzle.cword_webapp.app import _terminate_app
from crossword_puzzle.utils import GUIHelper, _update_cfg


class Addons:
    """Convenience and utility methods for all page classes."""

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

        if (
            condition
        ):  # A condition is required for this confirmation to happen
            if GUIHelper.confirm_with_messagebox(**confirmation):
                if action:
                    action()
                return True  # User agreed to the route
            else:
                return False  # User didn't agree to the route

        return True  # No condition, so just return True

    def _route(
        self,
        page_ref: str,  # Reference to page instance
        base: Base,  # Reference to base instance
        title: str,  # Title of the new page
        **kwargs,
    ) -> bool:
        """Method for all page-related classes to simplify navigation.

        All class instances that use ``_route`` must have their content packed
        and contain 4 content generation methods, as seen below.
        """
        try:
            page_inst = locals()[page_ref](base)
        except KeyError:
            from crossword_puzzle.pages import (
                BrowserPage,
                EditorPage,
                HomePage,
            )

            page_inst = locals()[page_ref](base)

        if (
            kwargs
        ):  # The caller of this route has added arguments for confirmation
            if not self._confirm_route(**kwargs):
                return False  # User didn't want to route

        for widget in Base.base_container.winfo_children():  # Remove content
            widget.pack_forget()

        base.title(title)  # Update to a new title

        # Update page in ``config.ini``
        _update_cfg(Base.cfg, "m", "page", page_inst.__class__.__name__)

        # Place the new page and call its content generation methods
        page_inst.pack(expand=True, fill="both")
        page_inst._make_containers()
        page_inst._place_containers()
        page_inst._make_content()
        page_inst._place_content()

        return True  # Route was successful


class Base(CTk, Addons):
    """The main app instance."""

    base_container: CTkFrame = None
    lang_info: Tuple[Dict[str, str], List[str]] = []
    locale: Locale = None
    cfg: ConfigParser = None
    fullscreen: bool = False

    def __init__(self, **kwargs) -> None:
        super().__init__()

        base_container = CTkFrame(self)
        base_container.pack(fill="both", expand=True)
        Base.base_container = base_container

        for kwarg in kwargs:
            setattr(Base, kwarg, kwargs[kwarg])

        self.protocol("WM_DELETE_WINDOW", self._exit_handler)  # Detect exit
        if system() == "Windows":
            self.iconbitmap(LOGO_PATH)
        set_appearance_mode(Base.cfg.get("m", "appearance"))
        set_default_color_theme(Base.cfg.get("m", "theme"))
        set_widget_scaling(float(Base.cfg.get("m", "scale")))
        self._set_dim()

        self._increment_launches()

        # Bring the user to the default Home Page
        page = Base.cfg.get("m", "page")
        self._route(page, self, _(PAGE_MAP[page]))

    def _set_dim(self) -> None:
        scale = float(Base.cfg.get("m", "scale"))
        new_width = DIM[0] * scale
        new_height = DIM[1] * scale

        self.minsize(new_width, new_height)
        self.maxsize(new_width, new_height)
        self.geometry(f"{new_width}x{new_height}")

    def _toggle_fullscreen(self) -> None:
        Base.fullscreen = not Base.fullscreen
        if self.fullscreen:
            self.maxsize(self.winfo_screenwidth(), self.winfo_screenheight())
        else:
            self._set_dim()
        self.attributes("-fullscreen", Base.fullscreen)

    def _increment_launches(self) -> None:
        """Increment ``launches`` in the program config by 1."""
        return _update_cfg(
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
        if GUIHelper.confirm_with_messagebox(exit_=True, restart=restart):
            _terminate_app()
            self.quit()

        if restart:  # Additionally perform a restart
            from .main import main

            main()
