'''Custom error classes used in `definitions_parser.py` and `cword_gen.py`.'''

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
class AlreadyGeneratedCrossword(Exception):
    def __init__(self):
        super().__init__("This crossword object already contains a generated crossword, view it by printing the crossword object")
class PrintingCrosswordObjectBeforeGeneration(Exception):
    def __init__(self):
        super().__init__("Call generate() on this object before printing it")