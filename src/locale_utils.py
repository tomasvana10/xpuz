'''The `LocaleUtils` class uses `_parse_locales` to parse `googletrans` langcodes to remove any 
inconsistencies with the locale naming conventions of Babel's `Locales` class. 

The class uses `_write_locales` to initialise all of the locale folders based on the parsed locales.

NOTE: `_write_locales` only works on macOS currently.
'''

import subprocess
from typing import Dict

import googletrans

from constants import LanguageReplacementsForPybabel

class LocaleUtils:
    @staticmethod
    def _parse_locales(langcodes: Dict[str, str]) -> Dict[str, str]:
        '''Replace all googletrans langcodes as specified by `LanguageReplacementsForPyBabel` if the
        value of the langcode isn't falsy. If it is a None value, it is removed entirely.
        '''
        parsed_langcodes = langcodes
        for replacement in LanguageReplacementsForPybabel.REPLACEMENTS:
            parsed_langcodes.remove(replacement)
            if (sub := (LanguageReplacementsForPybabel.REPLACEMENTS[replacement])):
                parsed_langcodes.append(sub)
        
        parsed_langcodes.append("en")
        
        return parsed_langcodes

    @staticmethod
    def _write_locales(langcodes: Dict[str, str]) -> None:
        '''Runs the pybabel `init` command to create approximately 104 locale files within
        `crossword_puzzle/locales` based on the parsed langcodes.
        '''
        for code in langcodes:
            try: 
                print(f"Inserting: {code}")
                cmd = f"pybabel init -l {code} -i locales/base.pot -d locales"
                subprocess.run(['zsh', '-c', cmd], text=True)
            except:
                print(f"Failed to insert: {code}")


if __name__ == "__main__":
    langcodes = list(googletrans.LANGCODES.values())
    parsed_langcodes = LocaleUtils._parse_locales(langcodes)
    LocaleUtils._write_locales(langcodes)