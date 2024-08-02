"""Custom errors module."""


class CrosswordGenerationError(Exception):
    """Generic error class for errors related to crossword generation."""
    pass


class DefinitionsParsingError(Exception):
    """Generic error class for errors related to the parsing of a crossword's 
    definitions.
    """
    pass
