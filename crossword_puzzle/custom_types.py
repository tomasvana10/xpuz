"""Custom types for type annotation in the source code of crossword_puzzle."""

from typing import TypedDict


class Placement(TypedDict):
    """A dictionary specifying the placement information of ``word`` at ``pos`` 
    in the grid.
    """
    word: str
    direction: str
    pos: tuple[int]
    intersections: list[None] | list[tuple[int]]

class CrosswordData(TypedDict):
    """The JSON serialised definitions and info of a base crossword."""
    definitions: dict[str, str]
    info: dict[str, str | int | None]