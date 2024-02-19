'''Methods to help with the translation of different parts of xword_puzzle.'''

import os
from typing import List

import polib
from google.cloud import translate_v2

from constants import Paths, LanguageReplacementsForPybabel

class LocaleTranslatorUtils:
    @staticmethod
    def update_msgstrs() -> None:
        '''Find all the untranslated entries in each `messages.po` file, then translate and update them
        using Google Cloud's translate_v2 module.
        '''
        client = translate_v2.Client()
        
        dest_codes, localedir_names = LocaleTranslatorUtils.get_dest_codes_and_localedir_names()

        for i, localedir_name in enumerate(localedir_names):
            messages = polib.pofile(os.path.join(Paths.LOCALES_PATH, localedir_name, "LC_MESSAGES", "messages.po"))
            untranslated_entries = messages.untranslated_entries()

            if not untranslated_entries:
                continue

            updates: int = 0
            for entry in untranslated_entries:
                text = entry.msgid
                if isinstance(text, bytes):
                    text = text.decode("utf-8")
                if dest_codes[i] == "en": continue # Cannot translate english
                entry.msgstr = client.translate(entry.msgid, target_language=dest_codes[i], 
                                                source_language="en", format_="text")["translatedText"]
                updates += 1
            
            print(f"Updated {updates} msgstrs for {localedir_name}")
            messages.save(newline=None)
            

    @staticmethod
    def get_dest_codes_and_localedir_names() -> List[List[str]]:
        '''Get all the locale directory names, as well as the google translate language codes, which are 
        mostly the same. 
        '''
        locales: List[str] = os.listdir(Paths.LOCALES_PATH)
        locales.remove("base.pot")
        dest_codes: List[str] = list()

        for locale_dir in locales:
            if locale_dir not in LanguageReplacementsForPybabel.REPLACEMENTS.values():
                dest_code = locale_dir
            else: # The locale dir name must be replaced with its google translate counterpart.
                dest_code = LanguageReplacementsForPybabel.REVERSE_REPLACEMENTS[locale_dir]  
            dest_codes.append(dest_code)  
    
        return [sorted(dest_codes), sorted(locales)]
    

class CrosswordTranslatorUtils:
    @staticmethod
    def update_localised_cwords():
        ...
    
    @staticmethod
    def get_base_cwords():
        ...


if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "src/googlekey.json"
    LocaleTranslatorUtils.update_msgstrs()