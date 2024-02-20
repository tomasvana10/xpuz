import random
from typing import Dict

import regex # Similar to "re" module but with more functionality

from errors import (
    EmptyDefinitions, InsufficientDefinitionsAndOrWordCount, ShorterDefinitionsThanWordCount, 
    InsufficientWordLength, EscapeCharacterInWord
)
from constants import CrosswordRestrictions


class DefinitionsParser:
    @staticmethod
    def _parse_definitions(definitions: Dict[str, str], 
                           word_count: int
                           ) -> Dict[str, str]:
        '''Conditional statements to raise errors for particular edge cases in a definitions dictionary.
        This function also uses `_format_definitions` to randomly sample a specified amount of definitions
        from the definitions dictionary, then format those definitions appropriately.
        '''
        definitions = definitions

        # Required error checking
        if not definitions:
            raise EmptyDefinitions
        if len(definitions) < 3 or word_count < 3: 
            raise InsufficientDefinitionsAndOrWordCount
        if len(definitions) < word_count: 
            raise ShorterDefinitionsThanWordCount
        if any("\\" in word for word in definitions.keys()): # Escape character break regex filtering.
            raise EscapeCharacterInWord

        definitions = DefinitionsParser._format_definitions(definitions, word_count)
        
        '''Removed for now; some translated crosswords have 1 letter words, and keeping this error checking
        would be too inconvenient.
        if not (all(len(k) >= 3 for k in definitions.keys())):
                raise InsufficientWordLength
        '''

        return definitions
    
    @staticmethod
    def _format_definitions(definitions: Dict[str, str],
                            word_count: int
                            ) -> Dict[str, str]:
        '''Randomly pick definitions from a larger sample, then remove all but language characters.'''
        randomly_sampled_definitions = dict(random.sample(list(definitions.items()), word_count))
        
        # Remove all non language chars from the keys of `randomly_sampled_definitions` (the words)
        # and capitalise its values (the clues/definitions).
        formatted_definitions = {regex.sub(CrosswordRestrictions.KEEP_LANGUAGES_PATTERN, 
                                          "", k).upper(): v.capitalize() \
                                for k, v in randomly_sampled_definitions.items()}
        
        return formatted_definitions