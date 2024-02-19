'''Custom types for type annotation in the source code of crossword_puzzle.'''


from typing import List, Tuple, Union, TypedDict

class Placement(TypedDict):
    '''A dictionary specifying the placement information of `word` at `pos` in the grid'''
    word: str
    direction: str
    pos: Tuple[int]
    intersections: Union[List[...], List[Tuple[int]]]