"""Custom types for type annotation in the source code of crossword_puzzle."""

from typing import Dict, List, Tuple, TypedDict, Union


class Placement(TypedDict):
    """A dictionary specifying the placement information of ``word`` at ``pos``
    in the grid.
    """

    word: str
    direction: str
    pos: Tuple[int]
    intersections: List[None] | List[Tuple[int]]


class CrosswordData(TypedDict):
    """The JSON serialised definitions and info of a base crossword."""

    definitions: Dict[str, str]
    info: Dict[str, Union[str, int, None]]
