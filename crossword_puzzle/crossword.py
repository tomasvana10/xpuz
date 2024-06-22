from collections import namedtuple
from math import ceil, sqrt
from random import choice
from typing import Dict, List, Tuple, Union

from crossword_puzzle.constants import (
    ACROSS,
    DIMENSIONS_CONSTANT,
    DOWN,
    EMPTY,
    WHITESPACE_SCALAR,
)
from crossword_puzzle.td import Placement
from crossword_puzzle.utils import (
    _format_definitions,
    _randomise_definitions,
    _verify_definitions,
)


class Crossword:
    """The Crossword class creates and populates a grid with a given amount of
    randomly sampled words from a larger set of crossword definitions in a
    crossword-like pattern.
    """

    def __init__(
        self,
        name: str,
        definitions: Dict[str, str],
        word_count: int,
        via_find_best_crossword: bool = False,
        dimensions: Union[None, int] = None,
    ) -> None:
        if via_find_best_crossword:  # Prevent recalculation of dimensions and
                                     # only shuffle existing definitions
            self.definitions: Dict[str, str] = _randomise_definitions(
                definitions
            )
            self.dimensions = dimensions
        else:  # First time instantiation (likely by ``_find_best_crossword``)
            _verify_definitions(definitions, word_count)
            self.definitions = _format_definitions(definitions, word_count)
            self.dimensions: int = self._get_dimensions()

        self.name = name  # Generally derived from the crossword directory name
                          # (without the difficulty suffix and title-cased)
        self.word_count = word_count  # Amount of words to be inserted
        self.generated: bool = False  # Flag to prevent duplicate generation
        self.intersections = []  # Store word intersection coordinates
        self.data = {}  # Store placement data
        self.inserts: int = 0  # Successfully inserted words
        self.fails: int = 0  # Words that no placements were found for
        self.total_intersections: int = 0  # Total intersecting points

    @property
    def cells(self) -> str:
        return "\n".join(" ".join(cell for cell in row) for row in self.grid)

    def __repr__(self) -> str:
        """Display a dev-friendly representation of ``Crossword``."""
        return repr(
            namedtuple(
                "Crossword",
                ["name", "word_count", "fails", "total_intersections", "data"],
            )(
                self.name,
                self.word_count,
                self.fails,
                self.total_intersections,
                self.data,
            )
        )

    def generate(self) -> Union[bool, None]:
        """Create a two-dimensional array (filled with ``EMPTY`` characters)."""
        if not self.generated:
            self.grid: List[List[str]] = self._init_grid()
            self._populate_grid(
                list(self.definitions.keys())  # Keys of definitions are words
            )
            self.generated: bool = True
        else:
            return False

    def _get_dimensions(self) -> int:
        """Determine the square dimensions of the crossword based on total word
        count or maximum word length.
        """
        self.total_char_count: int = sum(
            len(word) for word in self.definitions.keys()
        )
        dimensions: int = (
            ceil(sqrt(self.total_char_count * WHITESPACE_SCALAR))
            + DIMENSIONS_CONSTANT
        )
        max_word_len = max(map(len, self.definitions.keys()))

        # Return the larger of ``max_word_len`` and ``dimensions`` to ensure all
        # words can be placed in the grid.
        return max(dimensions, max_word_len)

    def _init_grid(self) -> List[List[str]]:
        """Return a two-dimensional array of ``EMPTY`` characters."""
        return [
            [EMPTY for col in range(self.dimensions)]
            for row in range(self.dimensions)
        ]

    @staticmethod
    def _unpack_placement_info(
        placement: Placement,
    ) -> Tuple[str, Union[ACROSS, DOWN], int, int]:
        return (
            placement["word"],
            placement["direction"],
            placement["pos"][0],
            placement["pos"][1],
        )

    @staticmethod
    def _sort_placements(placements: List[Placement]) -> List[Placement]:
        return sorted(
            placements, key=lambda p: p["intersections"], reverse=True
        )

    def _place_word(
        self,
        word: str,
        direction: Union[ACROSS, DOWN],
        row: int,
        col: int,
    ) -> None:
        """Place a word in the grid at the given row, column and direction."""
        if direction == ACROSS:
            for i, letter in enumerate(word):
                self.grid[row][col + i] = letter

        elif direction == DOWN:
            for i, letter in enumerate(word):
                self.grid[row + i][col] = letter

    def _get_middle_placement(self, word: str) -> Placement:
        """Return the placement for the first word in a random orientation in
        the middle of the grid. This naturally makes the generator build off of
        the center, making the crossword look nicer.
        """
        direction: str = choice([ACROSS, DOWN])
        middle: int = self.dimensions // 2

        if direction == ACROSS:
            row = middle
            col: int = middle - len(word) // 2
        elif direction == DOWN:
            row = middle - len(word) // 2
            col = middle

        return {
            "word": word,
            "direction": direction,
            "pos": (row, col),
            "intersections": [],
        }

    def _find_intersections(
        self,
        word: str,
        direction: Union[ACROSS, DOWN],
        row: int,
        col: int,
    ) -> Union[Tuple[None], Tuple[int]]:
        """Find the row and column of all points of intersection that ``word``
        has with ``self.grid``.
        """
        intersections: List[Tuple[int, int]] = []  # (row, column) form

        if direction == ACROSS:
            for i, letter in enumerate(word):
                if self.grid[row][col + i] == word[i]:  # Intersection found
                    intersections.append(tuple([row, col + i]))

        elif direction == DOWN:
            for i, letter in enumerate(word):
                if self.grid[row + i][col] == word[i]:
                    intersections.append(tuple([row + i, col]))

        return intersections

    def _validate_placement(
        self,
        word: str,
        direction: Union[ACROSS, DOWN],
        row: int,
        col: int,
    ) -> bool:
        """Determine if a word is suitable to be inserted into the grid. Causes
        for this function returning False are as follows:
            1. The word exceeds the limits of the grid if placed at ``row``
               and ``col``.
            2. The word intersects with another word of the same orientation at
               its first or last letter, e.x. ATHENSOFIA (Athens + Sofia)
            3. Other characters are in the way of the word - not
               overlapping/intersecting.
            4. Directly adjacent intersections are present.
        """
        if direction == ACROSS:
            # Case 1
            if col + len(word) > self.dimensions:
                return False

            # Case 2
            if (
                word[0] == self.grid[row][col]
                or word[-1] == self.grid[row][col + len(word) - 1]
            ):
                return False

            for i, letter in enumerate(word):
                # Case 3
                if self.grid[row][col + i] not in [
                    EMPTY,
                    letter,
                ]:
                    return False

                # Case 4
                if self.grid[row][col + i] == word[i] and (
                    (
                        col + i - 1 >= 0
                        and self.grid[row][col + i - 1] == word[i - 1]
                    )
                    or (
                        col + i + 1 < self.dimensions
                        and self.grid[row][col + i + 1] == word[i + 1]
                    )
                ):
                    return False

        if direction == DOWN:
            if row + len(word) > self.dimensions:
                return False

            if (
                word[0] == self.grid[row][col]
                or word[-1] == self.grid[row + len(word) - 1][col]
            ):
                return False

            for i, letter in enumerate(word):
                if self.grid[row + i][col] not in [
                    EMPTY,
                    letter,
                ]:
                    return False

                if self.grid[row + i][col] == word[i] and (
                    (
                        row + i - 1 >= 0
                        and self.grid[row + i - 1][col] == word[i - 1]
                    )
                    or (
                        row + i + 1 < self.dimensions
                        and self.grid[row + i + 1][col] == word[i + 1]
                    )
                ):
                    return False

        # All checks passed, this placement is valid
        return True

    def _prune_unreadable_placements(
        self, placements: List[Placement]
    ) -> List[Placement]:
        """Remove all placements that will result in the word being directly
        adjacent to another word,
        e.x.          or:
            ATHENS       ATHENSSOFIA
            SOFIA
        """

        pruned_placements: List[Placement] = []

        for placement in placements:
            word_length: int = len(placement["word"])
            row, col = placement["pos"]
            readability_flag = False

            if placement["direction"] == ACROSS:
                check_above: bool = row != 0
                check_below: bool = row != self.dimensions - 1
                check_left: bool = col != 0
                check_right: bool = col + word_length != self.dimensions
                for i in range(word_length):
                    # This letter is at an intersecting point, no need to check it
                    if (row, col + i) in placement["intersections"]:
                        continue
                    if check_above:
                        if self.grid[row - 1][col + i] != EMPTY:
                            readability_flag = True
                            break
                    if check_below:
                        if self.grid[row + 1][col + i] != EMPTY:
                            readability_flag = True
                            break
                    if check_left and i == 0:
                        if self.grid[row][col - 1] != EMPTY:
                            readability_flag = True
                            break
                    if check_right and i == word_length - 1:
                        if self.grid[row][col + i + 1] != EMPTY:
                            readability_flag = True
                            break

            elif placement["direction"] == DOWN:
                check_above: bool = row != 0
                check_below: bool = row + word_length < self.dimensions
                check_left: bool = col != 0
                check_right: bool = col + 1 < self.dimensions
                for i in range(word_length):
                    if (row + i, col) in placement["intersections"]:
                        continue
                    if check_above and i == 0:
                        if self.grid[row - 1][col] != EMPTY:
                            readability_flag = True
                            break
                    if check_below and i == word_length - 1:
                        if self.grid[row + i + 1][col] != EMPTY:
                            readability_flag = True
                            break
                    if check_left:
                        if self.grid[row + i][col - 1] != EMPTY:
                            readability_flag = True
                            break
                    if check_right:
                        if self.grid[row + i][col + 1] != EMPTY:
                            readability_flag = True
                            break

            if not readability_flag:  # No flags; placement is OK
                pruned_placements.append(placement)

        return pruned_placements

    def _get_placements(self, word: str) -> List[Placement]:
        """Find all placements for a given word (across and down), if valid."""
        placements: List[Placement] = []

        for direction in [
            ACROSS,
            DOWN,
        ]:
            for row in range(self.dimensions):
                for col in range(self.dimensions):
                    # The word can be inserted, so determine its intersections
                    # and add it to the potential placements
                    if self._validate_placement(word, direction, row, col):
                        intersections = self._find_intersections(
                            word, direction, row, col
                        )
                        placements.append(
                            {
                                "word": word,
                                "direction": direction,
                                "pos": (row, col),
                                "intersections": intersections,
                            }
                        )

        return placements

    def _add_data(self, placement: Placement) -> None:
        """Add placement information to ``self.data``."""
        self.data[(placement["pos"][0], placement["pos"][1])] = {
            "word": placement["word"],
            "direction": placement["direction"],
            "intersections": placement["intersections"],
            "definition": self.definitions[placement["word"]],
        }

    def _populate_grid(
        self, words: List[str], insert_backlog: bool = False
    ) -> None:
        """Attempt to all the words in the grid, recursing once to retry the
        placement of words with no intersections.
        """
        if not insert_backlog: # First time execution, attempt to insert all words
            self.backlog: List[str] = []

        if self.inserts == 0:  # First insertion is always in the middle
            middle_placement: Placement = self._get_middle_placement(words[0])
            self._place_word(*Crossword._unpack_placement_info(middle_placement))
            self._add_data(middle_placement)
            self.intersections.append(middle_placement["intersections"])
            self.inserts += 1
            del words[0]

        for word in words:  # Insert remaining words
            placements: List[Placement] = self._get_placements(word)
            placements = self._prune_unreadable_placements(placements)
            if not placements: # Could not find any placements, go to next word
                self.fails += 1
                continue

            # Sort placements from highest to lowest intersections
            sorted_placements = Crossword._sort_placements(placements)
            if not sorted_placements[0]["intersections"]:  # No intersections
                if not insert_backlog: # First time execution; append words here
                                       # for eventual reinsertion
                    self.backlog.append(word)
                    continue
                else:  # Reinsertion didn't help much, just pick a random placement
                    placement: Placement = choice(sorted_placements)
            else:
                placement: Placement = sorted_placements[0]

            self._place_word(*Crossword._unpack_placement_info(placement))
            self._add_data(placement)
            self.intersections.append(placement["intersections"])
            self.total_intersections += len(placement["intersections"])
            self.inserts += 1

        if self.backlog and not insert_backlog:  # Backlog contains uninserted
                                                 # words; attempt to insert them
            self._populate_grid(self.backlog, insert_backlog=True)


if __name__ == "__main__":  # Example usage outside context of the GUI
    from .wrappers import CrosswordWrapper

    cwrapper = CrosswordWrapper("geography", "capitals-easy", 3)
    cwrapper.make()
    print(cwrapper)
