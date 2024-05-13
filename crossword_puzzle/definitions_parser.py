from random import sample
from typing import Dict

from regex import sub  # Similar to ``re`` module but with more functionality

from crossword_puzzle.constants import CrosswordRestrictions
from crossword_puzzle.errors import (
    EmptyDefinitions,
    EscapeCharacterInWord,
    InsufficientDefinitionsAndOrWordCount,
    ShorterDefinitionsThanWordCount,
)


class DefinitionsParser:
    """Provides methods to ensure a crossword's definitions are valid."""

    @staticmethod
    def _parse_definitions(
        definitions: Dict[str, str], word_count: int
    ) -> Dict[str, str]:
        """Process a dictionary of definitions through statements to raise
        errors for particular edge cases in a definitions dictionary. This
        method also uses ``_format_definitions`` to randomly sample a specified
        amount of definitions from the definitions dictionary, then format
        those definitions appropriately.
        """
        # Required error checking
        if not definitions:
            raise EmptyDefinitions
        if len(definitions) < 3 or word_count < 3:
            raise InsufficientDefinitionsAndOrWordCount
        if len(definitions) < word_count:
            raise ShorterDefinitionsThanWordCount
        if any(
            "\\" in word for word in definitions.keys()
        ):  # Escape character breaks regex
            raise EscapeCharacterInWord

        """Removed for now; some localised crosswords have 1 letter words 
        (like zh) and keeping this error checking would be too inconvenient.
        
        if not (all(len(k) >= 3 for k in definitions.keys())):
                raise InsufficientWordLength
        """

        return DefinitionsParser._format_definitions(definitions, word_count)

    @staticmethod
    def _format_definitions(
        definitions: Dict[str, str], word_count: int
    ) -> Dict[str, str]:
        """Randomly pick definitions from a larger sample, then prune
        everything except the language characters from the words (the keys of
        the definitions).
        """
        # Randomly sample ``word_count`` amount of definitions
        randomly_sampled_definitions = dict(
            sample(list(definitions.items()), word_count)
        )

        # Remove all non language chars from the keys of
        # ``randomly_sampled_definitions``` (the words) and capitalise its values
        # (the clues/definitions)
        formatted_definitions = {
            sub(CrosswordRestrictions.KEEP_LANGUAGES_PATTERN, "", k).upper(): v
            for k, v in randomly_sampled_definitions.items()
        }

        return formatted_definitions
