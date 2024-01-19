import regex # Similar to "re" module but with more functionality
import random
from typing import Dict

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
        definitions = definitions

        if not definitions:
            raise EmptyDefinitions
        if len(definitions) < 3 or word_count < 3:
            raise InsufficientDefinitionsAndOrWordCount
        if len(definitions) < word_count:
            raise ShorterDefinitionsThanWordCount
        if any("\\" in word for word in definitions.keys()):
            raise EscapeCharacterInWord

        definitions = DefinitionsParser._format_definitions(definitions, word_count)
        
        if not (all(len(k) >= 3 for k in definitions.keys())):
                raise InsufficientWordLength

        return definitions
    
    @staticmethod
    def _format_definitions(definitions: Dict[str, str],
                            word_count: int
                            ) -> Dict[str, str]:
        '''Randomly pick definitions from a larger sample, then remove all but language characters.'''
        randomly_sampled_definitions = dict(random.sample(list(definitions.items()), word_count))
        formatted_definitions = {regex.sub(CrosswordRestrictions.KEEP_LANGUAGES_PATTERN, 
                                            "", k).upper(): v \
                                for k, v in randomly_sampled_definitions.items()}
        
        return formatted_definitions