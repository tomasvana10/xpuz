"""Custom types for type annotation in the source code of ``xpuz``."""

from typing import Dict, List, Tuple, Union, Any

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

from xpuz.constants import PROJECT_URL, ACROSS, DOWN


class Placement(TypedDict):
    """A dictionary specifying the placement information of `word` at `pos`
    in the grid.
    
    Args:
        word (str): The word.
        direction (Union[ACROSS, DOWN]): The direction of the word.
        pos (Tuple[int, int]): The position of the word in (row, column) form.
        intersections (Union[List[None], List[Tuple[int, int]]]): 
            The intersecting points that `word` has with a grid array in 
            (row, column) form.      
    """

    word: str
    direction: Union[ACROSS, DOWN]
    pos: Tuple[int, int]
    intersections: Union[List[None], List[Tuple[int, int]]]


class CrosswordData(TypedDict):
    """The JSON serialised definitions and info of a base crossword.
    
    Args:
        definitions (Dict[str, str]): The crossword's definitions.
        info (Dict[str, Union[str, int, None]]): The crossword's info.
    """

    definitions: Dict[str, str]
    info: Dict[str, Union[str, int, None]]


class CrosswordInfo(TypedDict):
    """A crossword's information.
    
    Example:
        ```json
            {
                "total_definitions": 23,
                "difficulty": 3,
                "symbol": "0x1f331",
                "name": "Biology",
                "translated_name": "Biologie",
                "category": "science"
            }
        ```
    
    Args:
        total_definitions (int): The total amount of definitions available for
                                 the crossword. 
        difficulty (int): An integer ranging from 0-3 (Easy, Medium, Hard, Extreme)
        symbol (str): A hexadecimal stored in a string, representing the crossword's 
                      symbol. This value is converted to an integer at runtime.
        name (str): The crossword's english name.
        translated_name (str): The crossword's translated name.
        category (str): The crossword's category (Geography, Computer Science, 
                        Mathematics, Science, or User))
    """

    total_definitions: int
    difficulty: int
    symbol: str  # Hexadecimal
    name: str
    translated_name: Union[None, str]
    category: str

class IPuzV2(TypedDict):
    """The `ipuz` v2 structure (JSON).
    
    Args:
        version (str): The version of the ipuz format, stored as a url. Defaults
                       to [ipuz.org/v2](http://ipuz.org/v2)
        kind (List[str]): The puzzle format. Defaults to 
                          [crossword#1](http://ipuz.org/crossword#1)
        origin (str): A link to the puzzle's origin. Default to the
                      [xpuz repository](https://github.com/tomasvana10/xpuz)
        author (str): The puzzle's author.
        date (str): The puzzle's date of creation.
        title (str): The puzzle's title.
        difficulty (str): The puzzle's difficulty. Not the same as the inbuilt
                          `xpuz` difficulties.
        dimensions (Dict[str, int]): The dimensions of the puzzle.
        puzzle (List[List[Union[int, None]]]): The puzzle itself.
        solution (List[List[Union[str, None]]]): The solution to the puzzle.
        clues (Dict[str, List[List[Union[int, str]]]]): The puzzle's clues.
    """
    
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
        **kwargs: Dict[str, Any],
    ) -> "IPuzV2":
        """Return an instance of `IPuzV2` with the standard parameters already
        defined through the method's default arguments.
        
        Args:
            version: The puzzle's version.
            kind: The puzzle's kind.
            origin: The puzzle's source of creation.
            author: The puzzle's author.
            **kwargs: Remaining arguments that are covered in 
                      [IPuzV2](td.md#xpuz.td.IPuzV2)
        """
        return cls(
            version=version, kind=kind, origin=origin, author=author, **kwargs
        )
