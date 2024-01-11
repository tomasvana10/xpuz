import random
import string
import json
import math

import regex # Similar to "re" module but with more functionality

class Directions:
    ACROSS = "a"
    DOWN = "d"


class Style:
    EMPTY = "▮"


class Restrictions:
    KEEP_LANGUAGES_PATTERN = r"\PL"
    

# Errors
class EmptyDefinitions(Exception):
    def __init__(self):
        super().__init__("Definitions must not be empty")
class InsufficientDefinitionsAndOrWordCount(Exception):
    def __init__(self):
        super().__init__("Length of definitions and/or word count must be greater than or equal to 3")
class ShorterDefinitionsThanWordCount(Exception):
    def __init__(self):
        super().__init__("Length of definitions must be greater than or equal to the crossword word count")
class InsufficientWordLength(Exception):
    def __init__(self):
        super().__init__("All words must be greater than or equal to 3 characters in length")
class EscapeCharacterInWord(Exception):
    def __init__(self):
        super().__init__("All keys in words must not contain an escape character")
        
        
class Crossword(object):
    def __init__(self, name, definitions, word_count):
        if not definitions:
            raise EmptyDefinitions
        if len(definitions) < 3 or word_count < 3:
            raise InsufficientDefinitionsAndOrWordCount
        if len(definitions) < word_count:
            raise ShorterDefinitionsThanWordCount
        if any("\\" in word for word in definitions.keys()):
            raise EscapeCharacterInWord

        self.name = name
        self.word_count = word_count
        self.definitions = self._format_definitions(definitions)
        self.dimensions = self._find_dimensions()
        
        if not (all(len(k) >= 3 for k in definitions.keys())):
            raise InsufficientWordLength

    def _format_definitions(self, definitions):
        if self.retry: 
            return dict(random.sample(list(definitions.items()), len(definitions))) 
        else:
            randomly_sampled_definitions = dict(random.sample(list(definitions.items()), self.word_count))
            formatted_definitions = {regex.sub(Restrictions.KEEP_LANGUAGES_PATTERN, "", k) .upper(): v \
                                    for k, v in randomly_sampled_definitions.items()}
            return formatted_definitions
    
    def _find_dimensions(self):
        '''Determine the square dimensions of the crossword based on total word count or maximum
        word length'''
        total_char_count = sum(len(word) for word in self.definitions.keys())
        dimensions = math.ceil(math.sqrt(total_char_count * 1.85))
        if dimensions < (max_word_len := (len(max(self.definitions.keys(), key=len)))):
            dimensions = max_word_len

        return dimensions