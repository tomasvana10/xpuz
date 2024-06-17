"""Developer utilities. Translation-related"""

import json
import os
import shutil
import subprocess
import sys
from typing import Dict, List, Union

import googletrans
import numpy as np
import polib
from constants import (
    BASE_CWORDS_PATH,
    BASE_POT_PATH,
    LANG_REPLACEMENTS,
    LOCALES_PATH,
    REVERSE_LANG_REPLACEMENTS,
)
from google.cloud import translate_v2
from td import CrosswordData


class Locales:
    @staticmethod
    def _run_locales_routine():
        langcodes = Locales._parse(list(googletrans.LANGCODES.values()))
        Locales._write_locales(langcodes)

    @staticmethod
    def _parse(langcodes: Dict[str, str]) -> Dict[str, str]:
        parsed_langcodes = langcodes
        for replacement in LANG_REPLACEMENTS:
            parsed_langcodes.remove(replacement)
            sub = LANG_REPLACEMENTS[replacement]
            if sub:
                parsed_langcodes.append(sub)

        parsed_langcodes.append("en")

        return parsed_langcodes

    @staticmethod
    def _write_locales(langcodes: Dict[str, str]) -> None:
        """Runs the ``pybabel init`` command to create ~100 locale files within
        ``crossword_puzzle/locales`` based on the parsed langcodes.
        """
        existing_langcodes = os.listdir(LOCALES_PATH)
        for code in langcodes:
            try:
                if code in existing_langcodes:
                    continue
                print(f"Inserting: {code}")
                cmd = f"pybabel init -l {code} -i {BASE_POT_PATH} -d {LOCALES_PATH}"
                if sys.platform == "darwin":
                    subprocess.run(["zsh", "-c", cmd], text=True)
                elif sys.platform == "win32":
                    os.system(cmd)
            except Exception:
                print(f"Failed to insert: {code}")


class Translation:
    @staticmethod
    def update_msgstrs() -> None:
        """Find all the untranslated entries in each ``messages.po`` file,
        then translate and update them using Google Cloud's ``translate_v2``
        module.
        """
        locales, lang_codes = Translation._get_locales_and_lang_codes()
        local_client = client

        for i, locale in enumerate(locales):
            messages: polib.POFile = polib.pofile(
                os.path.join(
                    LOCALES_PATH, locale, "LC_MESSAGES", "messages.po"
                )
            )
            untranslated_entries = messages.untranslated_entries()

            if not untranslated_entries:
                continue

            updates: int = 0
            for entry in untranslated_entries:
                text = entry.msgid
                if isinstance(text, bytes):
                    text = text.decode("utf-8")
                if lang_codes[i] == "en":
                    continue  # Cannot translate english
                entry.msgstr = local_client.translate(
                    text,
                    dest=lang_codes[i],
                    src="en",
                ).text
                updates += 1

            print(f"(Locale: {locale}) - Updated {updates} msgstr(s)")
            messages.save(newline=None)

    @staticmethod
    def _get_locales_and_lang_codes() -> List[List[str]]:
        """Get all the locale directory names, as well as the google translate
        language codes, which are mostly the same.
        """
        locales: List[str] = sorted(
            [f.name for f in os.scandir(LOCALES_PATH) if f.is_dir()]
        )

        lang_codes: List[str] = [
            (
                REVERSE_LANG_REPLACEMENTS[locale]
                if locale in LANG_REPLACEMENTS.values()
                else locale
            )
            for locale in locales
        ]

        return locales, lang_codes

    @staticmethod
    def update_cword_translations() -> None:
        """Travel down the locales directory, ensuring each locale has a cwords
        directory, exists in ``base_cwords``, and all the necessary crosswords
        have been added and translated, and makes those translations if required.
        """
        locales, lang_codes = Translation._get_locales_and_lang_codes()
        base_category_tree = Translation._get_base_cword_category_tree()

        for i, locale in enumerate(locales):
            locale_path = os.path.join(LOCALES_PATH, locale)
            cwords_path = os.path.join(locale_path, "cwords")
            if not os.path.exists(cwords_path):
                os.mkdir(cwords_path)

            # Remove categories of the locale's crosswords if they are no longer
            # present in the base categories
            for existing_category in [
                f.name for f in os.scandir(cwords_path) if f.is_dir()
            ]:
                if existing_category not in base_category_tree.keys():
                    shutil.rmtree(os.path.join(cwords_path, existing_category))

            for category, cwords in base_category_tree.items():
                category_path = os.path.join(cwords_path, category)
                if not os.path.exists(category_path):
                    os.mkdir(category_path)

                for existing_cword in [
                    f.name for f in os.scandir(category_path) if f.is_dir()
                ]:
                    if existing_cword not in base_category_tree[category]:
                        shutil.rmtree(
                            os.path.join(category_path, existing_cword)
                        )

                for cword in cwords:  # Make and translate (if required) all
                    # crosswords in the current category
                    cword_path = os.path.join(category_path, cword)
                    if not os.path.exists(cword_path):
                        os.mkdir(cword_path)

                    if os.listdir(cword_path):
                        continue  # Probably made translations already

                    definitions, info = Translation._get_cword_data(
                        category, cword
                    )
                    if locale == "en":  # Just write the non-translated
                        # definitions and info
                        info["translated_name"] = info["name"]
                        Translation._write_translated_cword_data(
                            cword_path, definitions, info
                        )
                        continue

                    # Make the translations
                    translated_definitions, translated_info = (
                        Translation._format_and_translate_cword_data(
                            lang_codes[i], definitions, info
                        )
                    )
                    # Write the translated data!
                    Translation._write_translated_cword_data(
                        cword_path, translated_definitions, translated_info
                    )
                    print(
                        f"(Locale: {locale}) - Wrote translations of "
                        f"{category}/{cword}"
                    )

    @staticmethod
    def _format_and_translate_cword_data(
        language: str,
        definitions: Dict[str, str],
        info: Dict[str, Union[str, int, None]],
    ) -> CrosswordData:
        """Facilitates the efficient translation of a dictionary of definitions
        through bulk translation, ensuring that each translation made does not
        exceed the translation request limit by splitting the definitions into
        parts. Returns a data with an identical structure to what was passed
        (except it is translated).
        """
        local_client = client

        arrayified_definitions = np.array(
            [pair for item in definitions.items() for pair in item]
        )
        # Split into manageable parts for translation requests
        split_definitions = np.array_split(
            arrayified_definitions,
            Translation._get_definitions_parts(arrayified_definitions),
        )

        translated_definitions = Translation._translate_parts(
            split_definitions, language
        )

        # Recreate the definitions dictionary by assigning every two items to a
        # key and value
        formatted_definitions = {
            part[i]["translatedText"]: part[i + 1]["translatedText"]
            for part in translated_definitions
            for i in range(0, len(part), 2)
        }

        # Update just the `translated_name` key of `info`
        info["translated_name"] = local_client.translate(
            info["name"],
            target_language=language,
            source_language="en",
            format_="text",
        )["translatedText"]

        return formatted_definitions, info

    @staticmethod
    def _translate_parts(
        definitions: List[np.array], language: str
    ) -> List[dict]:
        """Translate the parts of a split definitions array and return a new
        array of those translated parts.
        """
        local_client = client

        translated_parts = list()
        for part in definitions:
            translated_parts.append(
                local_client.translate(
                    list(part),
                    target_language=language,
                    source_language="en",
                    format_="text",
                )
            )

        return translated_parts

    @staticmethod
    def _get_definitions_parts(definitions: np.array) -> int:
        """Find the parts required to split a definitions array into using a
        recursive function.
        """
        length: int = len(definitions)
        parts: int = 1
        if length <= 128:
            return parts

        def _reduce(length: int, parts: int) -> int:
            length = int(length / 2)
            parts += 1
            if length > 128:
                return _reduce(length, parts)
            else:
                return parts

        return _reduce(length, parts)

    @staticmethod
    def _get_base_cword_category_tree() -> Dict[str, List[str]]:
        category_tree: Dict[str, List[str]] = dict()
        for category in [
            f for f in os.scandir(BASE_CWORDS_PATH) if f.is_dir()
        ]:
            cwords: List[str] = list()
            for cword in [
                f.name for f in os.scandir(category.path) if f.is_dir()
            ]:
                cwords.append(cword)
            category_tree[category.name] = cwords

        return category_tree

    @staticmethod
    def _get_cword_data(category: str, name: str) -> CrosswordData:
        base_cword_path = os.path.join(BASE_CWORDS_PATH, category, name)
        """Load the `definitions.json` and `info.json` files from a given base 
        crossword.
        """
        with open(
            os.path.join(base_cword_path, "definitions.json"), "r"
        ) as def_file, open(
            os.path.join(base_cword_path, "info.json"), "r"
        ) as info_file:
            definitions, info = json.load(def_file), json.load(info_file)

        return definitions, info

    @staticmethod
    def _write_translated_cword_data(
        path: str,
        definitions: Dict[str, str],
        info: Dict[str, Union[str, int]],
    ) -> None:
        with open(
            os.path.join(path, "definitions.json"), "w"
        ) as def_file, open(os.path.join(path, "info.json"), "w") as info_file:
            json.dump(definitions, def_file, indent=4)
            json.dump(info, info_file, indent=4)


if __name__ == "__main__":
    LOCALE_INIT = False
    DO_GETTEXT_TRANSLATIONS = False
    DO_CROSSWORD_TRANSLATIONS = False

    if LOCALE_INIT:
        Locales._run_locales_routine()
    if DO_GETTEXT_TRANSLATIONS:
        client = googletrans.Translator()
        Translation.update_msgstrs()
    if DO_CROSSWORD_TRANSLATIONS:
        # NOTE: translating crosswords without google-cloud will take forever
        # os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "src/googlekey.json"
        # client = translate_v2.Client()
        Translation.update_cword_translations()
