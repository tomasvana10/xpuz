"""Custom types for type annotation in the source code of ."""

from typing import Dict, List, Tuple, Union

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict


class Placement(TypedDict):
    """A dictionary specifying the placement information of ``word`` at ``pos``
    in the grid.
    """

    word: str
    direction: str
    pos: Tuple[int, int]
    intersections: Union[List[None], List[Tuple[int, int]]]


class CrosswordData(TypedDict):
    """The JSON serialised definitions and info of a base crossword."""

    definitions: Dict[str, str]
    info: Dict[str, Union[str, int, None]]


class CrosswordInfo(TypedDict):
    """A crossword's information"""

    total_definitions: int
    difficulty: int
    symbol: str  # Hexadecimal
    name: str
    translated_name: Union[None, str]
    category: str
