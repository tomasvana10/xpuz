"""Custom types for type annotation in the source code of ``xpuz``."""

from typing import Dict, List, Tuple, Union

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

from xpuz.constants import PROJECT_URL


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

class IPuzV2(TypedDict):
    """ipuz v2 structure (JSON)."""
    
    version: str
    kind: List[str]
    origin: str
    author: str
    date: str
    title: str
    difficulty: str
    dimensions: Dict[str, int]
    puzzle: List[List[Union[int, None]]]
    solution: List[List[Union[str, None]]]
    clues: Dict[str, List[List[Union[int, str]]]]
    
    @classmethod
    def create(
        cls, 
        version: str = "http://ipuz.org/v2", 
        kind: List[str] = ["http://ipuz.org/crossword#1"],
        origin: str = PROJECT_URL,
        author: str = "xpuz Crossword Generator",
        **kwargs,
    ) -> "IPuzV2":
        return cls(version=version, kind=kind, **kwargs)
