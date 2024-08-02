"""Entry point of ``xpuz``."""

from configparser import ConfigParser
try:
    from ctypes import windll
    from locale import windows_locale
except ImportError:
    pass
from os import environ
from os import name as os_name

from babel import Locale

from xpuz.base import Base
from xpuz.utils import GUIHelper, _get_language_options, _read_cfg, _update_cfg


def _get_os_language() -> str:
    """Infer language code from operating system data.
    
    Returns:
        The locale.
    """
    if os_name == "posix":
        return environ["LANG"].split("-")[0]
    else:
        return windows_locale[
            windll.kernel32.GetUserDefaultUILanguage()
        ].split("-")[0]


def main() -> None:
    """Main function to initialise the `xpuz` GUI."""
    cfg: ConfigParser = ConfigParser()
    _read_cfg(cfg)

    locale: Locale = Locale.parse(cfg.get("m", "language"))
    # First-time initialisation, try detecting the OS locale
    if int(cfg.get("misc", "launches")) == 0:
        try:
            locale: Locale = Locale.parse(_get_os_language())
            _update_cfg(cfg, "m", "language", locale.language)
        except Exception:
            pass

    GUIHelper._install_translations(locale)
    app: Base = Base(locale=locale, lang_info=_get_language_options(), cfg=cfg)
    app.mainloop()


if __name__ == "__main__":
    main()
