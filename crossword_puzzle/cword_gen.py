from math import ceil, sqrt
from random import choice, sample
from typing import Dict, List, Tuple, Union

from crossword_puzzle.constants import CrosswordDirection, CrosswordStyle, DimensionsCalculation
from crossword_puzzle.custom_types import Placement
from crossword_puzzle.definitions_parser import DefinitionsParser
from crossword_puzzle.errors import PrintingCrosswordObjectBeforeGeneration
from crossword_puzzle.utils import find_best_crossword, load_definitions


class Crossword:
    """The Crossword class creates and populates a grid with a given amount of
    randomly sampled words from a larger set of crossword definitions in a
    crossword-like pattern.

    Usage information:
    To begin, assign a definitions JSON to a variable by running
    >>> definitions = load_definitions("geography", "capitals-easy", "en")

    For simple use, instantiate the class with the required parameters and call
    the ``Crossword.generate`` function.
    >>> crossword = Crossword("Capitals", definitions=definitions, word_count=10)
    >>> crossword.generate()
    >>> print(crossword)

    For more advanced use, use ``utils.find_best_crossword``, which takes
    an ungenerated instance of the Crossword class. This will return a crossword
    object that is already has a populated grid and has more intersections than
    a crossword generated with only a single attempt.
    >>> crossword = Crossword("Capitals", definitions=definitions, word_count=10)
    >>> crossword = find_best_crossword(crossword)
    >>> print(crossword)

    NOTE: When inserting large amounts of words, fails with insertion may occur.
    """

    def __init__(
        self,
        name: str,
        definitions: Dict[str, str],
        word_count: int,
        retry: bool = False,
    ) -> None:
        self.retry = retry  # Flag to reattempt insertions when generating through  
                            # ``utils.find_best_crossword``.

        if self.retry:
            self.definitions = self._randomise_definitions(definitions)
        else:  # Randomly sample ``word_count`` amount of definitions and ensure
            # they only contain language characters
            self.definitions = DefinitionsParser._parse_definitions(
                definitions, word_count
            )

        self.name = (
            name  # The name of the crossword (the crossword's directory)
        )
        self.word_count = word_count  # Amount of words to be inserted
        self.generated: bool = False  # Flag to prevent duplicate generation
        self.dimensions: int = (self._get_dimensions())  # Side length of square grid
        self.intersections = []  # Store intersection word indices
        self.data = {}  # Interpreted by ``main.py`` as words are inserted.
        # Example:
        # {(1, 2): {"word": "Hello", "direction": "a", "intersections": [(1, 5)],
        #           "definition": A standard english greeting}}

    def __str__(self) -> str:
        """Display crossword when printing an instance of this class, on which
        ``.generate()`` has been called.
        """
        if not self.generated:
            raise PrintingCrosswordObjectBeforeGeneration

        # Name, word count (insertions), failed insertions, total intersections,
        # crossword grid
        return (
            f"\nCrossword name: {self.name}\n"
            + f"Word count: {self.inserts}, "
            + f"Failed insertions: {self.word_count - self.inserts}\n"
            + f"Total intersections: {self.total_intersections}\n\n"
            + "\n".join(" ".join(cell for cell in row) for row in self.grid)
        )

    def generate(self) -> Union[bool, None]:
        """Create a two-dimensional array (filled with ``CrosswordStyle.EMPTY``
        characters).
        """
        if not self.generated:
            self.grid: List[List[str]] = self._init_grid()
            self._populate_grid(
                list(
                    self.definitions.keys()
                )  # Keys of definitions are the words
            )
            self.generated: bool = True
        else:
            return False

    def _randomise_definitions(
        self, definitions: Dict[str, str]
    ) -> Dict[str, str]:
        """Randomises the existing definitions when attempting reinsertion,
        which prevents ``find_best_crossword`` from favouring certain word
        groups with intrinsically higher intersections.
        """
        return dict(sample(list(definitions.items()), len(definitions)))

    def _get_dimensions(self) -> int:
        """Determine the square dimensions of the crossword based on total word
        count or maximum word length.
        """
        self.total_char_count: int = sum(
            len(word) for word in self.definitions.keys()
        )
        dimensions: int = (
            ceil(
                sqrt(
                    self.total_char_count
                    * DimensionsCalculation.WHITESPACE_SCALAR
                )
            )
            + DimensionsCalculation.DIMENSIONS_CONSTANT
        )
        # Assign the length of the maximum word to dimensions if it is greater
        # than dimensions. This must be done so all words can be placed in the grid.
        max_word_len = max(map(len, self.definitions.keys()))
        dimensions = max(dimensions, max_word_len)

        return dimensions

    def _init_grid(self) -> List[List[str]]:
        """Make a two-dimensional array of ``CrosswordStyle.EMPTY`` characters."""
        return [
            [CrosswordStyle.EMPTY for column in range(self.dimensions)]
            for row in range(self.dimensions)
        ]

    def _place_word(
        self,
        word: str,
        direction: Union[CrosswordDirection.ACROSS, CrosswordDirection.DOWN],
        row: int,
        column: int,
    ) -> None:
        """Place a word in the grid at the given row, column and direction."""
        if direction == CrosswordDirection.ACROSS:
            for i, letter in enumerate(word):
                self.grid[row][column + i] = letter
            return

        elif direction == CrosswordDirection.DOWN:
            for i, letter in enumerate(word):
                self.grid[row + i][column] = letter
            return

    def _get_middle_placement(self, word: str) -> Placement:
        """Returns the placement for the first word in a random orientation in
        the middle of the grid. This naturally makes the generator build off of
        the center, making the crossword look nicer.
        """
        direction: str = choice(
            [CrosswordDirection.ACROSS, CrosswordDirection.DOWN]
        )
        middle: int = self.dimensions // 2

        if direction == CrosswordDirection.ACROSS:
            row = middle
            column: int = middle - len(word) // 2
        elif direction == CrosswordDirection.DOWN:
            row = middle - len(word) // 2
            column = middle

        return {
            "word": word,
            "direction": direction,
            "pos": (row, column),
            "intersections": [],
        }

    def _find_intersections(
        self,
        word: str,
        direction: Union[CrosswordDirection.ACROSS, CrosswordDirection.DOWN],
        row: int,
        column: int,
    ) -> Union[Tuple[None], Tuple[int]]:
        """Find the row and column of all points of intersection that ``word``
        has with ``self.grid``.
        """
        intersections = []  # Elements are stored in Tuple[row, column] form

        if direction == CrosswordDirection.ACROSS:
            for i, letter in enumerate(word):
                if self.grid[row][column + i] == word[i]:  # Intersection found
                    intersections.append(tuple([row, column + i]))

        elif direction == CrosswordDirection.DOWN:
            for i, letter in enumerate(word):
                if self.grid[row + i][column] == word[i]:
                    intersections.append(tuple([row + i, column]))

        return intersections

    def _validate_placement(
        self,
        word: str,
        direction: Union[CrosswordDirection.ACROSS, CrosswordDirection.DOWN],
        row: int,
        column: int,
    ) -> bool:
        """Determine if a word is suitable to be inserted into the grid. Causes
        for this function returning False are as follows:
            1. The word exceeds the limits of the grid if placed at ``row``
               and ``column``.
            2. The word intersects with another word of the same orientation at
               its first or last letter, e.x. ATHENSOFIA (Athens + Sofia)
            3. Other characters are in the way of the word - not
               overlapping/intersecting.
            4. Directly adjacent intersections are present.
        """
        if direction == CrosswordDirection.ACROSS:
            # Case 1
            if column + len(word) > self.dimensions:
                return False

            # Case 2
            if (
                word[0] == self.grid[row][column]
                or word[-1] == self.grid[row][column + len(word) - 1]
            ):
                return False

            for i, letter in enumerate(word):
                # Case 3
                if self.grid[row][column + i] not in [
                    CrosswordStyle.EMPTY,
                    letter,
                ]:
                    return False

                # Case 4
                if self.grid[row][column + i] == word[i] and (
                    (
                        column + i - 1 >= 0
                        and self.grid[row][column + i - 1] == word[i - 1]
                    )
                    or (
                        column + i + 1 < self.dimensions
                        and self.grid[row][column + i + 1] == word[i + 1]
                    )
                ):
                    return False

        if direction == CrosswordDirection.DOWN:
            if row + len(word) > self.dimensions:
                return False

            if (
                word[0] == self.grid[row][column]
                or word[-1] == self.grid[row + len(word) - 1][column]
            ):
                return False

            for i, letter in enumerate(word):
                if self.grid[row + i][column] not in [
                    CrosswordStyle.EMPTY,
                    letter,
                ]:
                    return False

                if self.grid[row + i][column] == word[i] and (
                    (
                        row + i - 1 >= 0
                        and self.grid[row + i - 1][column] == word[i - 1]
                    )
                    or (
                        row + i + 1 < self.dimensions
                        and self.grid[row + i + 1][column] == word[i + 1]
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

        pruned_placements = []

        for placement in placements:
            word_length: int = len(placement["word"])
            row, column = placement["pos"]
            readability_flag = False

            if placement["direction"] == CrosswordDirection.ACROSS:
                check_above: bool = row != 0
                check_below: bool = row != self.dimensions - 1
                check_left: bool = column != 0
                check_right: bool = column + word_length != self.dimensions
                for i in range(word_length):
                    # This letter is at an intersecting point, no need to check it
                    if (row, column + i) in placement["intersections"]:
                        continue
                    if check_above:
                        if (
                            self.grid[row - 1][column + i]
                            != CrosswordStyle.EMPTY
                        ):
                            readability_flag = True
                            break
                    if check_below:
                        if (
                            self.grid[row + 1][column + i]
                            != CrosswordStyle.EMPTY
                        ):
                            readability_flag = True
                            break
                    if check_left and i == 0:
                        if self.grid[row][column - 1] != CrosswordStyle.EMPTY:
                            readability_flag = True
                            break
                    if check_right and i == word_length - 1:
                        if (
                            self.grid[row][column + i + 1]
                            != CrosswordStyle.EMPTY
                        ):
                            readability_flag = True
                            break

            elif placement["direction"] == CrosswordDirection.DOWN:
                check_above: bool = row != 0
                check_below: bool = row + word_length < self.dimensions
                check_left: bool = column != 0
                check_right: bool = column + 1 < self.dimensions
                for i in range(word_length):
                    if (row + i, column) in placement["intersections"]:
                        continue
                    if check_above and i == 0:
                        if self.grid[row - 1][column] != CrosswordStyle.EMPTY:
                            readability_flag = True
                            break
                    if check_below and i == word_length - 1:
                        if (
                            self.grid[row + i + 1][column]
                            != CrosswordStyle.EMPTY
                        ):
                            readability_flag = True
                            break
                    if check_left:
                        if (
                            self.grid[row + i][column - 1]
                            != CrosswordStyle.EMPTY
                        ):
                            readability_flag = True
                            break
                    if check_right:
                        if (
                            self.grid[row + i][column + 1]
                            != CrosswordStyle.EMPTY
                        ):
                            readability_flag = True
                            break

            if not readability_flag:  # No flags were made, so this placement
                                      # can be used
                pruned_placements.append(placement)

        return pruned_placements

    def _get_placements(self, word: str) -> List[Placement]:
        """Find all placements for a given word (across and down), if valid."""
        placements = []
        for direction in [
            CrosswordDirection.ACROSS,
            CrosswordDirection.DOWN,
        ]:
            for row in range(self.dimensions):
                for column in range(self.dimensions):
                    # The word can be inserted, so determine its intersections
                    # and add it to the potential placements
                    if self._validate_placement(word, direction, row, column):
                        intersections = self._find_intersections(
                            word, direction, row, column
                        )
                        placements.append(
                            {
                                "word": word,
                                "direction": direction,
                                "pos": (row, column),
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
        if (
            not insert_backlog
        ):  # First time execution, attempt to insert all words
            self.backlog_has_been_inserted: bool = False
            self.uninserted_words_backlog: List[str] = []
            self.inserts: int = 0
            self.fails: int = 0
            self.total_intersections: int = 0

        if self.inserts == 0:  # Place the first word in the middle of the grid
                               # (not when inserting the backlog of words).
            middle_placement: Placement = self._get_middle_placement(words[0])
            self._place_word(
                middle_placement["word"],
                middle_placement["direction"],
                middle_placement["pos"][0],
                middle_placement["pos"][1],
            )
            self._add_data(middle_placement)
            self.intersections.append(middle_placement["intersections"])
            self.inserts += 1
            del words[0]

        for word in words:  # Insert remaining words after the middle placement
                            # is complete
            placements: List[Placement] = self._get_placements(word)
            placements = self._prune_unreadable_placements(placements)
            if (
                not placements
            ):  # Could not find any placements, go to next word
                self.fails += 1
                continue

            # Sort placements from highest to lowest intersections
            sorted_placements = sorted(
                placements, key=lambda k: k["intersections"], reverse=True
            )
            if not sorted_placements[0]["intersections"]:  # No intersections
                if (
                    not insert_backlog
                ):  # First time execution; append words here
                    # for eventual reinsertion
                    self.uninserted_words_backlog.append(word)
                    continue
                else:  # Reinsertion didn't help much, just pick a random placement
                    placement: Placement = choice(sorted_placements)
            else:
                placement: Placement = sorted_placements[0]

            self._place_word(
                placement["word"],
                placement["direction"],
                placement["pos"][0],
                placement["pos"][1],
            )
            self._add_data(placement)
            self.intersections.append(placement["intersections"])
            self.total_intersections += len(placement["intersections"])
            self.inserts += 1

        if self.backlog_has_been_inserted:  # The backlog was just inserted, so
                                            # end the method
            return

        # There are words present in the backlog and it has not been inserted yet
        if (
            self.uninserted_words_backlog
            and not self.backlog_has_been_inserted
        ):
            self.backlog_has_been_inserted = True
            # Recurse ``_populate_grid`` with ``uninserted_words_backlog``
            self._populate_grid(
                self.uninserted_words_backlog, insert_backlog=True
            )


if __name__ == "__main__":  # Example usage – this module is normally used in
                            # the executional context of ``main.py``
    definitions = load_definitions("computer science", "booleans-easy", "en")

    crossword = Crossword(
        definitions=definitions, word_count=3, name="booleans"
    )
    crossword = find_best_crossword(crossword)

    print(crossword)
