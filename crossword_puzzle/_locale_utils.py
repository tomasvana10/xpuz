"""Module to remove any inconsistencies with the locale naming conventions of 
Babel's ``Locales`` class. 

NOTE: `_write_locales` only works on macOS currently.
NOTE: Requires the googletrans module, which is not listed in `requirements.txt`.
"""

import subprocess

import googletrans

from crossword_puzzle.constants import LanguageReplacementsForPybabel


class LocaleUtils:
    @staticmethod
    def _parse_locales(langcodes: dict[str, str]) -> dict[str, str]:
        """Replace all googletrans langcodes as specified by
        ``LanguageReplacementsForPyBabel`` if the value of the langcode isn't
        falsy. If it is a None value, it is removed entirely.
        """
        parsed_langcodes = langcodes
        for replacement in LanguageReplacementsForPybabel.REPLACEMENTS:
            parsed_langcodes.remove(replacement)
            sub = LanguageReplacementsForPybabel.REPLACEMENTS[replacement]
            if sub:
                parsed_langcodes.append(sub)

        parsed_langcodes.append("en")

        return parsed_langcodes

    @staticmethod
    def _write_locales(langcodes: dict[str, str]) -> None:
        """Runs the ``pybabel init`` command to create ~100 locale files within
        ``crossword_puzzle/locales`` based on the parsed langcodes.
        """
        for code in langcodes:
            try:
                print(f"Inserting: {code}")
                cmd = f"pybabel init -l {code} -i locales/base.pot -d locales"
                subprocess.run(["zsh", "-c", cmd], text=True)
            except Exception:
                print(f"Failed to insert: {code}")


if __name__ == "__main__":
    langcodes = list(googletrans.LANGCODES.values())
    parsed_langcodes = LocaleUtils._parse_locales(langcodes)
    LocaleUtils._write_locales(langcodes)
