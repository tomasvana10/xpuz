class Directions:
    ACROSS = "a"
    DOWN = "d"


class Style:
    EMPTY = "▮"


class Restrictions:
    KEEP_LANGUAGES_PATTERN = "" # Figure out a regex to remove all but language characters from a string


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
        
        
class Crossword(object):
    ...