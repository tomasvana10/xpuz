'''Methods to help with the translation of different parts of crossword_puzzle.'''

import os
import shutil
import json
import numpy as np
from pprint import pprint
from typing import List, Tuple, Dict, Union, Callable

import polib
from google.cloud import translate_v2

from constants import Paths, LanguageReplacementsForPybabel
from custom_types import CrosswordData


class LocaleTranslatorUtils:
    @staticmethod
    def update_msgstrs() -> None:
        '''Find all the untranslated entries in each `messages.po` file, then translate and update them
        using Google Cloud's translate_v2 module.
        '''
        dest_codes, localedir_names = LocaleTranslatorUtils._get_dest_codes_and_localedir_names()

        for i, dir_name in enumerate(localedir_names):
            messages: polib.POFile = polib.pofile(os.path.join(Paths.LOCALES_PATH, dir_name, "LC_MESSAGES", "messages.po"))
            untranslated_entries = messages.untranslated_entries()

            if not untranslated_entries: continue

            updates: int = 0
            for entry in untranslated_entries:
                text = entry.msgid
                if isinstance(text, bytes):
                    text = text.decode("utf-8")
                if dest_codes[i] == "en": continue # Cannot translate english
                entry.msgstr = client.translate(text, target_language=dest_codes[i], source_language="en", 
                                                format_="text")["translatedText"]
                updates += 1
            
            print(f"Updated {updates} msgstrs for {dir_name}")
            messages.save(newline=None)
            
    @staticmethod
    def _get_dest_codes_and_localedir_names() -> List[List[str]]:
        '''Get all the locale directory names, as well as the google translate language codes, which are 
        mostly the same. 
        '''
        locales: List[str] = os.listdir(Paths.LOCALES_PATH) # The names of all the files in the `locales` directory
        locales.remove("base.pot")
        dest_codes: List[str] = list() # Same as `locales`, but compatible with translation (some replacements)

        for locale_dir in locales:
            if locale_dir not in LanguageReplacementsForPybabel.REPLACEMENTS.values():
                dest_code = locale_dir
            else: # The locale dir name must be replaced with its google translate counterpart.
                dest_code = LanguageReplacementsForPybabel.REVERSE_REPLACEMENTS[locale_dir]  
            dest_codes.append(dest_code)  
    
        if ".DS_Store" in locales: locales.remove(".DS_Store")
        return [sorted(dest_codes), sorted(locales)]
    

class CrosswordTranslatorUtils:
    @staticmethod
    def update_cword_translations() -> None:   
        '''Travel down the locales directory, ensuring each locale has a cwords directory, exists in
        `base_cwords`, and all the necessary crosswords have been added and translated, and makes 
        those translations if required. 
        '''
        base_cword_dir_names = CrosswordTranslatorUtils._get_base_cword_dir_names()
        dest_codes, localedir_names = LocaleTranslatorUtils._get_dest_codes_and_localedir_names()
        
        # Loop through each locale directory -> update necessary directories and files
        for i, dir_name in enumerate(localedir_names):
            translation_code = dir_name
            # Locale dir name is different to the google translate language code
            if translation_code in LanguageReplacementsForPybabel.REVERSE_REPLACEMENTS.keys():
                translation_code = LanguageReplacementsForPybabel.REVERSE_REPLACEMENTS[dir_name]
                
            dir_path = os.path.join(Paths.LOCALES_PATH, dir_name)
            locale_dir_items = os.listdir(dir_path)
        
            if "cwords" not in locale_dir_items: # Make `cwords` dir in locale file if it isn't there
                os.mkdir(os.path.join(dir_path, "cwords"))
            
            current_cwords = os.listdir(os.path.join(dir_path, "cwords"))
            if ".DS_Store" in current_cwords: current_cwords.remove(".DS_Store")

            # Check if all the base crosswords are in this locale directory, and translate them if needed.
            for cword_dir_name in current_cwords:
                current_cword_dir = os.path.join(dir_path, "cwords", cword_dir_name)
                if os.listdir(current_cword_dir): continue # Already made translations for this cword
                if cword_dir_name not in base_cword_dir_names: # No longer exists in base cwords
                    shutil.rmtree(current_cword_dir)
                    continue

                # The current crossword directory hasn't been made yet; make it and do the translations
                try: 
                    os.mkdir(current_cword_dir)
                except: ... # It may have just been empty
                
                definitions, info = CrosswordTranslatorUtils._get_cword_data(cword_dir_name)
                if dir_name == "en": # Just write the non-translated definitions and info
                    info["translated_name"] = info["name"]
                    CrosswordTranslatorUtils._write_translated_cword_data(current_cword_dir, definitions, info)
                    return
                
                translated_definitions, translated_info = CrosswordTranslatorUtils._format_and_translate_cword_data(translation_code, definitions, info)
                # Write the translated data!
                CrosswordTranslatorUtils._write_translated_cword_data(current_cword_dir, translated_definitions, translated_info)

    @staticmethod
    def _format_and_translate_cword_data(language: str,
                                         definitions: Dict[str, str], 
                                         info: Dict[str, Union[str, int, None]]
                                         ) -> CrosswordData:
        '''Facilitates the efficient translation of a dictionary of definitions through bulk translation,
        ensuring that each translation made does not exceed the translation request limit by splitting 
        the definitions into parts. Returns a data with an identical structure to what was passed (except
        it is translated).
        '''
        arrayified_definitions = np.array([pair for item in definitions.items() for pair in item])
        # Split into manageable parts for translation requests
        split_definitions = np.array_split(arrayified_definitions, 
                                           CrosswordTranslatorUtils._get_definitions_parts(arrayified_definitions))
        translated_definitions = CrosswordTranslatorUtils._translate_parts(split_definitions, language)
        # Recreate the definitions dictionary by assigning every two items to a key and value
        formatted_definitions = {part[i]["translatedText"]: part[i + 1]["translatedText"] \
                                 for part in translated_definitions for i in range(0, len(part), 2)}

        # Update just the `translated_name` key of `info`
        info["translated_name"] = client.translate(info["name"], target_language=language, 
                                                   source_language="en", format_="text")["translatedText"]
        
        return formatted_definitions, info
    
    @staticmethod
    def _translate_parts(definitions: List[np.array], 
                         language: str
                         ) -> List[Dict]:
        '''Translate the parts of a split definitions array and return a new array of those translated parts.'''
        translated_parts = list()
        for part in definitions:
            translated_parts.append(client.translate(list(part), target_language=language, source_language="en", format_="text"))

        return translated_parts
    
    @staticmethod
    def _get_definitions_parts(definitions: np.array) -> int:
        '''Find the parts required to split a definitions array into using a recursive function.'''
        length: int = len(definitions)
        parts: int = 1
        if length <= 128: return parts

        def _reduce(length: int, 
                    parts: int
                    ) -> Union[Callable, int]:
            length = int(length / 2)
            parts += 1
            if length > 128:
                return _reduce(length, parts)
            else:
                return parts

        return _reduce(length, parts)
    
    @staticmethod
    def _get_cword_data(cword_dir_name: str) -> CrosswordData:
        '''Load the `definitions.json` and `info.json` files from a given base crossword.'''
        cword_path = os.path.join(Paths.BASE_CWORDS_PATH, cword_dir_name)
        with open(os.path.join(cword_path, "definitions.json"), "r") as file:
            definitions = json.load(file)
        with open(os.path.join(cword_path, "info.json"), "r") as file:
            info = json.load(file)
            
        return definitions, info
    
    @staticmethod
    def _write_translated_cword_data(cword_dir_name: str, 
                                     definitions: Dict[str, str], 
                                     info: Dict[str, Union[str, int]]
                                     ) -> None:
        with open(os.path.join(cword_dir_name, "definitions.json"), "w") as file:
            json.dump(definitions, file, indent=4)
        with open(os.path.join(cword_dir_name, "info.json"), "w") as file:
            json.dump(info, file, indent=4)
    
    @staticmethod
    def _get_base_cword_dir_names() -> List[str]:
        '''Get all the directory names of the crosswords in `Paths.BASE_CWORDS_PATH`.'''
        dir_names: List[str] = list()
        for dir_name in os.listdir(Paths.BASE_CWORDS_PATH):
            if dir_name: # Must not be NoneType
                dir_names.append(dir_name)
        
        if ".DS_Store" in dir_names: dir_names.remove(".DS_Store")
        
        return dir_names
            
        
if __name__ == "__main__":
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "src/googlekey.json"
    
    client = translate_v2.Client()
    CrosswordTranslatorUtils.update_cword_translations()

    # LocaleTranslatorUtils.update_msgstrs()