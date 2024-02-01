import json
import os
from random import sample, choice
from math import ceil, sqrt
from typing import Dict, Tuple, List, Union

from definitions_parser import DefinitionsParser
from constants import CrosswordDirections, CrosswordStyle, DimensionsCalculation, Paths
from errors import AlreadyGeneratedCrossword, PrintingCrosswordObjectBeforeGeneration
from custom_types import Placement


class Crossword(object):
    '''The Crossword class creates and populates a grid with a given amount of randomly sampled words
    from a larger set of crossword definitions in a crossword-like pattern.

    ~~~~~~
    Usage information:
    > To begin, assign a definitions JSON to a variable by running 
      Crossword.load_definitions(f"{Paths.CWORDS_PATH}/<name>.json)
    
    
    > For simple use, instantiate the class with the required parameters and call the generate() function.
    >>> crossword = Crossword("Capitals", definitions=definitions, word_count=10)
    >>> crossword.generate()
    >>> print(crossword)
    
    
    > For more advanced use, use CrosswordHelper.find_best_crossword, which takes an ungenerated 
      instance of the Crossword class. This will return a crossword object that is already has a 
      populated grid and has more intersections than a crossword generated with only a single attempt.
    >>> crossword = Crossword("Capitals", definitions=definitions, word_count=10)
    >>> crossword = CrosswordHelper.find_best_crossword(crossword)
    >>> print(crossword)
    
    NOTE: When inserting large amounts of words, fails with insertion may occur.
    '''

    def __init__(self, 
                 name: str, 
                 definitions: Dict[str, str], 
                 word_count: int, 
                 retry: bool = False
                 ) -> None:
        self.retry = retry
        if self.retry: # Reattempting insertion, randomise exisiting definitions
            self.definitions = self._randomise_existing_definitions(definitions)
        else: # Randomly sample `word_count` amount of definitions and ensure they only contain
              # language characters
            self.definitions = DefinitionsParser._parse_definitions(definitions, word_count)

        self.name = name
        self.word_count = word_count
        self.generated: bool = False
        self.dimensions: int = self._find_dimensions()
        self.intersections = list() # Will be expanded to store all intersecting word points
        self.data = dict()  # Interpreted by `main.py`; expanded as words are inserted
        ''' example:
            self.data = {
                (1, 2): {"word": "Hello", "direction": "a", 
                         "intersections": [(1, 5)], "definition": A standard english greeting},
            }
        '''
        
    def __str__(self) -> str:
        '''Display crossword when printing an instance of this class, on which `.generate()` has been called.'''
        if not self.generated:
            raise PrintingCrosswordObjectBeforeGeneration
        
        # Name, word count (insertions), failed insertions, total intersections, crossword grid
        return \
            f"\nCrossword name: {self.name}\n" + \
            f"Word count: {self.inserts}, Failed insertions: {self.word_count - self.inserts}\n" + \
            f"Total intersections: {self.total_intersections}\n\n" + \
            "\n".join(" ".join(cell for cell in row) for row in self.grid)

    def generate(self) -> None:
        '''Create a two-dimensional array (filled with CrosswordStyle.EMPTY characters) then populate it.'''
        if not self.generated:
            self.generated = True
            self.grid: List[List[str]] = self._initialise_cword_grid()
            self._populate_grid(list(self.definitions.keys())) # Keys of definitions are the words
        else:
            raise AlreadyGeneratedCrossword

    def _randomise_existing_definitions(self, 
                                        definitions: Dict[str, str]
                                        ) -> Dict[str, str]:
        '''For reattempting generation, existing definitions are randomised, which prevents 
        find_best_crossword from favouring certain word groups with intrinsically higher intersections.
        '''
        return dict(sample(list(definitions.items()), len(definitions)))

    def _find_dimensions(self) -> int:
        '''Determine the square dimensions of the crossword based on total word count or maximum
        word length.
        '''
        self.total_char_count: int = sum(len(word) for word in self.definitions.keys())
        dimensions: int = ceil(sqrt(
                                   self.total_char_count \
                                   * DimensionsCalculation.WHITESPACE_SCALAR)) \
                                   + DimensionsCalculation.DIMENSIONS_CONSTANT
        # In case the maximum word length is longer than the calculated dimensions, this must be done.
        if dimensions < (max_word_len := (len(max(self.definitions.keys(), key=len)))):
            dimensions = max_word_len

        return dimensions

    def _initialise_cword_grid(self) -> List[List[str]]:
        '''Make a two-dimensional array of `CrosswordStyle.EMPTY` characters.'''
        return [[CrosswordStyle.EMPTY for column in range(self.dimensions)] \
                for row in range(self.dimensions)]

    def _place_word(self, 
                    word: str, 
                    direction: int, 
                    row: int, 
                    column: int
                    ) -> None:
        '''Place a word in the grid at the given row, column and direction.'''
        if direction == CrosswordDirections.ACROSS:
            for i in range(len(word)):
                self.grid[row][column + i] = word[i]
            return
        
        elif direction == CrosswordDirections.DOWN:
            for i in range(len(word)):
                self.grid[row + i][column] = word[i]
            return

    def _find_first_word_placement_position(self, 
                                            word: str
                                            ) -> Placement:
        '''Place the first word in a random orientation in the middle of the grid. This naturally makes
        the generator build off of the center, making the crossword look more symmetrical.
        '''
        direction: str = choice([CrosswordDirections.ACROSS, CrosswordDirections.DOWN])
        middle: int = self.dimensions // 2

        if direction == CrosswordDirections.ACROSS:
            row = middle
            column: int = middle - len(word) // 2
            return {"word": word, "direction": CrosswordDirections.ACROSS, 
                    "pos": (row, column), "intersections": list()}

        elif direction == CrosswordDirections.DOWN:
            row = middle - len(word) // 2
            column = middle
            return {"word": word, "direction": CrosswordDirections.DOWN, 
                    "pos": (row, column), "intersections": list()}

    def _find_intersections(self, 
                            word: str, 
                            direction: str, 
                            row: int, 
                            column: int
                            ) -> Union[Tuple[...], Tuple[int]]:
        '''Find the row and column of all points of intersection that the `word` has with the `self.grid`.'''
        intersections = list()

        if direction == CrosswordDirections.ACROSS:
            for i in range(len(word)):
                if self.grid[row][column + i] == word[i]:
                    intersections.append(tuple([row, column + i]))

        elif direction == CrosswordDirections.DOWN:
            for i in range(len(word)):
                if self.grid[row + i][column] == word[i]:
                    intersections.append(tuple([row + i, column]))

        return intersections

    def _can_word_be_inserted(self, 
                              word: str, 
                              direction: str, 
                              row: int, 
                              column: int
                              ) -> bool:
        '''Determine if a word is suitable to be inserted into the grid. Causes for this function 
        returning False are as follows:
            1. The word will exceed the limits of the grid if placed at `row` and `column`.
            2. Other characters being in the way of the word - not overlapping/intersecting.
            3. The word intersects with another word of the same orientation at its first or last letter, 
               e.x. ATHENSOFIA (Athens + Sofia)
        '''
        if direction == CrosswordDirections.ACROSS: # 1.
            if column + len(word) > self.dimensions:
                return False

            for i in range(len(word)): # 2.
                if self.grid[row][column + i] not in [CrosswordStyle.EMPTY, word[i]]:
                    return False
            
            if word[0] == self.grid[row][column] or word[-1] == self.grid[row][column + len(word) - 1]: # 3.
                return False

        if direction == CrosswordDirections.DOWN:
            if row + len(word) > self.dimensions:
                return False

            for i in range(len(word)):
                if self.grid[row + i][column] not in [CrosswordStyle.EMPTY, word[i]]:
                    return False
            
            if word[0] == self.grid[row][column] or word[-1] == self.grid[row + len(word) - 1][column]:
                return False
            
        return True

    def _prune_placements_for_readability(self, 
                                          placements: List[Placement]
                                          ) -> List[Placement]:
        '''Remove all placements that will result in the word being directly adjacent to another word,
        e.x.          or:
            ATHENS       ATHENSSOFIA 
            SOFIA
        '''
        
        pruned_placements = list()

        for placement in placements:
            word_length: int = len(placement["word"])
            row, column = placement["pos"]
            readability_flags: int = 0

            if placement["direction"] == CrosswordDirections.ACROSS:
                check_above: bool = row != 0
                check_below: bool = row != self.dimensions - 1
                check_left: bool = column != 0
                check_right: bool = column + word_length != self.dimensions
                for i in range(word_length):
                    # This letter is at an intersecting point, no need to check anywhere
                    if (row, column + i) in placement["intersections"]:
                        continue
                    if check_above:
                        if self.grid[row - 1][column + i] != CrosswordStyle.EMPTY:
                            readability_flags += 1
                    if check_below:
                        if self.grid[row + 1][column + i] != CrosswordStyle.EMPTY:
                            readability_flags += 1
                    if check_left and i == 0:
                        if self.grid[row][column - 1] != CrosswordStyle.EMPTY:
                            readability_flags += 1
                    if check_right and i == word_length - 1:
                        if self.grid[row][column + i + 1] != CrosswordStyle.EMPTY:
                            readability_flags += 1

            elif placement["direction"] == CrosswordDirections.DOWN:
                check_above: bool = row != 0
                check_below: bool = row + word_length < self.dimensions
                check_left: bool = column != 0 
                check_right: bool = column + 1 < self.dimensions
                for i in range(word_length):
                    if (row + i, column) in placement["intersections"]:
                        continue
                    if check_above and i == 0:
                        if self.grid[row - 1][column] != CrosswordStyle.EMPTY:
                            readability_flags += 1
                    if check_below and i == word_length - 1:
                        if self.grid[row + i + 1][column] != CrosswordStyle.EMPTY:
                            readability_flags += 1
                    if check_left:
                        if self.grid[row + i][column - 1] != CrosswordStyle.EMPTY:
                            readability_flags += 1
                    if check_right:
                        if self.grid[row + i][column + 1] != CrosswordStyle.EMPTY:
                            readability_flags += 1

            if not readability_flags: 
                pruned_placements.append(placement)

        return pruned_placements

    def _find_insertion_coords(self, 
                               word: str
                               ) -> List[Placement]:
        '''Find all valid insertion coords for a given word (across and down) through validation with 
        self._can_word_be_inserted. If it can be inserted, the word's intersections are determined
        and it is appended to the placements array (a list of dictionaries containing information
        about the word - the word itself, its direction, its position and its intersections).
        '''
        placements = list()

        for row in range(self.dimensions):
            for column in range(self.dimensions):
                if self._can_word_be_inserted(word, CrosswordDirections.ACROSS, row, column):
                    intersections = self._find_intersections(word, CrosswordDirections.ACROSS, row, 
                                                             column)
                    placements.append({"word": word,
                                       "direction": CrosswordDirections.ACROSS,
                                       "pos": (row, column),
                                       "intersections": intersections})

                if self._can_word_be_inserted(word, CrosswordDirections.DOWN, row, column):
                    intersections = self._find_intersections(word, CrosswordDirections.DOWN, row, 
                                                             column)
                    placements.append({"word": word,
                                       "direction": CrosswordDirections.DOWN,
                                       "pos": (row, column),
                                       "intersections": intersections})

        return placements

    def _add_data(self, 
                  placement: Placement
                  ) -> None:
        '''Append placement information to self.data'''
        self.data[(placement["pos"][0], placement["pos"][1])] = {
                                                    "word": placement["word"], 
                                                    "direction": placement["direction"],
                                                    "intersections": placement["intersections"],
                                                    "definition": self.definitions[placement["word"]]}

    def _populate_grid(self, 
                       words: List[str], # The keys of self.definitions 
                       insert_backlog: bool = False
                       ) -> None:
        '''Call _find_insertion_coords to determine all the places a word can be inserted and choose
        the placement with the most intersections. If no intersections are present, it appends it to
        the array "uninserted_words_backlog" which will be inserted later when the function is recursed
        with that array as the "words" parameter.
        '''
        if not insert_backlog: # First time execution
            self.backlog_has_been_inserted: bool = False
            self.uninserted_words_backlog: List[str] = list()
            self.inserts: int = 0
            self.fails: int = 0
            self.total_intersections: int = 0

        if self.inserts == 0: # First word will be placed in the middle of the grid
                middle_placement: Placement = self._find_first_word_placement_position(words[0])
                self._place_word(middle_placement["word"], middle_placement["direction"],
                                 middle_placement["pos"][0], middle_placement["pos"][1])
                self._add_data(middle_placement)
                self.intersections.append(middle_placement["intersections"])
                self.inserts += 1
                del words[0]
                
        for word in words: # Insert remaining words after the middle placement is complete
            placements: List[Placement] = self._find_insertion_coords(word)
            placements = self._prune_placements_for_readability(placements)
            if not placements: 
                self.fails += 1
                continue

            # Sort placements for the current word from highest to lowest intersections
            sorted_placements = sorted(placements, key=lambda k: k["intersections"], reverse=True)
            if not sorted_placements[0]["intersections"]: # No intersections present
                if not insert_backlog: # First time execution; append words here for eventual reinsertion
                    self.uninserted_words_backlog.append(word)
                    continue
                else: # Reinsertion didn't help much, just pick a random placement
                    placement: Placement = choice(sorted_placements)
            else: 
                placement: Placement = sorted_placements[0]

            self._place_word(placement["word"], placement["direction"], placement["pos"][0], 
                             placement["pos"][1])
            self._add_data(placement)
            self.intersections.append(placement["intersections"])
            self.total_intersections += len(placement["intersections"])
            self.inserts += 1

        if self.backlog_has_been_inserted: # The backlog was just inserted, so end the function
            return

        # There are words present in the backlog and it has not been inserted yet
        if self.uninserted_words_backlog and not self.backlog_has_been_inserted:
            self.backlog_has_been_inserted = True
            # Recurse _populate_grid with "uninserted_words_backlog"
            self._populate_grid(self.uninserted_words_backlog, insert_backlog=True) 
      
  
class CrosswordHelper():
    '''Contains static methods to help with the loading of necessary JSON files and for performing 
    optimised crossword creation with `find_best_crossword`.
    '''
    @staticmethod
    def find_best_crossword(crossword: Crossword) -> Crossword:
        '''Determines the best crossword out of a amount of instantiated crosswords based on the 
        largest amount of total intersections and smallest amount of fails.
        '''
        name: str = crossword.name
        word_count: int = crossword.word_count
        
        attempts_db: Dict[str, int] = CrosswordHelper._load_attempts_db()
        max_attempts: int = attempts_db[str(word_count)] # Get amount of attempts based on word count
        attempts: int = 0

        reinsert_definitions: Dict[str, str] = crossword.definitions
        try: 
            crossword.generate()
        except: ... # ok buddy
        best_crossword = crossword
        
        while attempts <= max_attempts:
            # Setting the "retry" param to True will make the Crossword class only randomise the 
            # definitions it is given, not sample new random ones
            crossword = Crossword(name=name, definitions=reinsert_definitions, 
                                  word_count=word_count, retry=True)
            crossword.generate()
            
            # Ensure the crossword with the most intersections is always assigned to best_crossword
            if (crossword.total_intersections > best_crossword.total_intersections) and \
                    (crossword.fails <= best_crossword.fails): 
                best_crossword = crossword
            attempts += 1
        
        return best_crossword # NOTE: `generate()`` has already been called on this object

    @staticmethod
    def load_definitions(name: str) -> Dict[str, str]:
        '''Load a definitions json for a given crossword.'''
        try:
            with open(os.path.join(Paths.CWORDS_PATH, name, f"{name}.json"), "r") as file:
                definitions = json.load(file)
        except json.decoder.JSONDecodeError:
            raise EmptyDefinitions
        
        return definitions

    @staticmethod
    def _load_attempts_db() -> Dict[str, int]:
        '''Load a json that specifies the amount of attempts a crossword should be recreated based 
        on the amount of words that crossword will contain.
        '''
        with open(Paths.ATTEMPTS_DB_PATH, "r") as file:
            attempts_db = json.load(file)
        
        return attempts_db


if __name__ == "__main__": # Example usage
    definitions = CrosswordHelper.load_definitions("capitals")
    
    crossword = Crossword(definitions=definitions, word_count=3, name="Capitals")
    crossword = CrosswordHelper.find_best_crossword(crossword)   

    print(crossword)