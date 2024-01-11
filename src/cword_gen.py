import random
import string
import json
import math
import pathlib

import regex # Similar to "re" module but with more functionality


class Directions:
    ACROSS = "a"
    DOWN = "d"


class Style:
    EMPTY = "▮"


class Restrictions:
    KEEP_LANGUAGES_PATTERN = r"\PL" # The opposite of \p{l} which matches characters from any language


class Paths:
    ATTEMPTS_DB_PATH = pathlib.Path(__file__).resolve().parents[0] / "data/attempts_db.json"
    CROSSWORDS_PATH = pathlib.Path(__file__).resolve().parents[0] / "cwords"

# Errors
class EmptyDefinitions(Exception):
    def __init__(self):
        super().__init__("Definitions must not be empty")
class InsufficientDefinitionsAndOrWordCount(Exception):
    def __init__(self):
        super().__init__("Length of definitions and/or word count must be greater than or equal to 3")
class ShorterDefinitionsThanWordCount(Exception):
    def __init__(self):
        super().__init__("Length of definitions must be greater than or equal to the crossword word count")
class InsufficientWordLength(Exception):
    def __init__(self):
        super().__init__("All words must be greater than or equal to 3 characters in length")
class EscapeCharacterInWord(Exception):
    def __init__(self):
        super().__init__("All keys in words must not contain an escape character")
class AlreadyGeneratedCrossword(Exception):
    def __init__(self):
        super().__init__("This crossword object already contains a generated crossword")
class PrintingCrosswordObjectBeforeGeneration(Exception):
    def __init__(self):
        super().__init__("Call generate() on this instance before printing it")


class Crossword(object):
    '''The Crossword class creates and populates a grid with a given amount of randomly sampled words
    from a larger set of crossword definitions. Complete with error detection.
    
    > To begin, assign a definitions JSON to a variable by running Crossword.load_definitions(f"{Paths.CROSSWORDS_PATH}/<name>.json)
    > For simple use, instantiate the class with the required parameters and call the generate() function.
    > For more advanced use, use CrosswordHelper.find_best_crossword, which takes an ungenerated instance of the Crossword
      class. This will return a crossword object that is already has a populated grid and has more intersections than 
      a crossword generated with only a single attempt.
    
    When inserting large amounts of words, fails with insertion may occur.'''
     
    def __init__(self, name, definitions, word_count, retry=False):
        if not definitions:
            raise EmptyDefinitions
        if len(definitions) < 3 or word_count < 3:
            raise InsufficientDefinitionsAndOrWordCount
        if len(definitions) < word_count:
            raise ShorterDefinitionsThanWordCount
        if any("\\" in word for word in definitions.keys()):
            raise EscapeCharacterInWord

        self.generated = False
        self.retry = retry
        self.name = name
        self.word_count = word_count
        self.definitions = self._format_definitions(definitions)
        self.dimensions = self._find_dimensions()
        self.clues = dict() # Presentable to end-user
        self.data = list([list(), list()])  # For internal usage in main app

        if not (all(len(k) >= 3 for k in definitions.keys())):
            raise InsufficientWordLength

    def __str__(self):
        '''Display crossword when printing an instance of this class'''
        if not self.generated:
            raise PrintingCrosswordObjectBeforeGeneration
        
        return f"\nCrossword name: {self.name}\n" + \
            f"Word count: {self.inserts}, Failed insertions: {self.word_count - self.inserts}\n" + \
            f"Total intersections: {self.total_intersections}\n\n" + \
            "\n".join(" ".join(cell for cell in row) for row in self.grid) + "\n\n" + \
            "\n".join(f"{k}: {v}" for k, v in self.clues.items())

    def generate(self):
        '''Create an "EMPTY" two-dimensional array then populate it'''
        if not self.generated:
            self.generated = True
            self._initialise_crossword_grid()
            self._populate_grid(list(self.definitions.keys()))
        else:
            raise AlreadyGeneratedCrossword

    def _format_definitions(self, definitions):
        '''Randomly pick definitions from a larger sample, then remove all but language characters'''
        if self.retry: # For reattempting insertion, existing definitions are randomised, which 
                       # prevents find_best_crossword from favouring certain word groups with 
                       # intrinsically higher intersections
            return dict(random.sample(list(definitions.items()), len(definitions))) 
        else:
            randomly_sampled_definitions = dict(random.sample(list(definitions.items()), self.word_count))
            formatted_definitions = {regex.sub(Restrictions.KEEP_LANGUAGES_PATTERN, "", k) .upper(): v \
                                    for k, v in randomly_sampled_definitions.items()}
            return formatted_definitions

    def _find_dimensions(self):
        '''Determine the square dimensions of the crossword based on total word count or maximum
        word length'''
        total_char_count = sum(len(word) for word in self.definitions.keys())
        dimensions = math.ceil(math.sqrt(total_char_count * 1.85)) + 1
        if dimensions < (max_word_len := (len(max(self.definitions.keys(), key=len)))):
            dimensions = max_word_len

        return dimensions

    def _initialise_crossword_grid(self):
        '''Make a two-dimensional array of "EMPTY" characters'''
        self.grid = [[Style.EMPTY for i in range(self.dimensions)] for j in range(self.dimensions)]

    def _place_word(self, word, direction, row, column):
        '''Place a word in the grid at the given row, column and direction'''
        if direction == Directions.ACROSS:
            for i in range(len(word)):
                self.grid[row][column + i] = word[i]

        if direction == Directions.DOWN:
            for i in range(len(word)):
                self.grid[row + i][column] = word[i]

    def _find_first_word_placement_position(self, word):
        '''Place the first word in a random orientation in the middle of the grid'''
        direction = random.choice([Directions.ACROSS, Directions.DOWN])
        middle = self.dimensions // 2

        if direction == Directions.ACROSS:
            row = middle
            column = middle - len(word) // 2
            return {"word": word, "direction": Directions.ACROSS, 
                    "pos": (row, column), "intersections": list()}

        if direction == Directions.DOWN:
            row = middle - len(word) // 2
            column = middle
            return {"word": word, "direction": Directions.DOWN, 
                    "pos": (row, column), "intersections": list()}

    def _find_intersections(self, word, direction, row, column):
        '''Find the indexes of all points of intersection that the parameter "word" has with the grid'''
        intersections = list()

        if direction == Directions.ACROSS:
            for i in range(len(word)):
                if self.grid[row][column + i] == word[i]:
                    intersections.append(tuple([row, column + i]))

        if direction == Directions.DOWN:
            for i in range(len(word)):
                if self.grid[row + i][column] == word[i]:
                    intersections.append(tuple([row + i, column]))

        return intersections

    def _can_word_be_inserted(self, word, direction, row, column):
        '''Determine if a word is suitable to be inserted into the grid. Causes for this function 
        returning False include:
            1. The word being too long for the dimensions of the grid
            2. Other characters being in the way of the word (not intersecting)
            3. The word intersects with another word of the same orientation at its final letter, 
               e.x. ATHENSOFIA (Athens + Sofia)'''
        if direction == Directions.ACROSS: # 1
            if column + len(word) > self.dimensions:
                return False

            for i in range(len(word)): # 2
                if self.grid[row][column + i] not in [Style.EMPTY, word[i]]:
                    return False
            
            if word[0] == self.grid[row][column] or word[-1] == self.grid[row][column + len(word) - 1]: # 3
                return False

        if direction == Directions.DOWN:
            if row + len(word) > self.dimensions:
                return False

            for i in range(len(word)):
                if self.grid[row + i][column] not in [Style.EMPTY, word[i]]:
                    return False
            
            if word[0] == self.grid[row][column] or word[-1] == self.grid[row + len(word) - 1][column]:
                return False
            
        return True

    def _prune_placements_for_readability(self, placements):
        '''Remove all placements that will result in the word being directly adjacent to another word,
        e.x.          or:
            ATHENS       ATHENSSOFIA 
            SOFIA'''
        
        pruned_placements = list()

        for placement in placements:
            word_length = len(placement["word"])
            row, column = placement["pos"]
            readability_flags = 0

            if placement["direction"] == Directions.ACROSS:
                check_above = row != 0
                check_below = row != self.dimensions - 1
                check_left = column != 0
                check_right = column + word_length != self.dimensions
                for i in range(word_length):
                    if (row, column + i) in placement["intersections"]:
                        continue
                    if check_above:
                        if self.grid[row - 1][column + i] != Style.EMPTY:
                            readability_flags += 1
                    if check_below:
                        if self.grid[row + 1][column + i] != Style.EMPTY:
                            readability_flags += 1
                    if check_left and i == 0:
                        if self.grid[row][column - 1] != Style.EMPTY:
                            readability_flags += 1
                    if check_right and i == word_length - 1:
                        if self.grid[row][column + i + 1] != Style.EMPTY:
                            readability_flags += 1

            if placement["direction"] == Directions.DOWN:
                check_above = row != 0
                check_below = row + word_length < self.dimensions
                check_left = column != 0 
                check_right = column + 1 < self.dimensions
                for i in range(word_length):
                    if (row + i, column) in placement["intersections"]:
                        continue
                    if check_above and i == 0:
                        if self.grid[row - 1][column] != Style.EMPTY:
                            readability_flags += 1
                    if check_below and i == word_length - 1:
                        if self.grid[row + i + 1][column] != Style.EMPTY:
                            readability_flags += 1
                    if check_left:
                        if self.grid[row + i][column - 1] != Style.EMPTY:
                            readability_flags += 1
                    if check_right:
                        if self.grid[row + i][column + 1] != Style.EMPTY:
                            readability_flags += 1

            if not readability_flags: 
                pruned_placements.append(placement)

        return pruned_placements

    def _find_insertion_coords(self, word):
        '''Find all valid insertion coords for a given word (across and down) through validation with 
        self._can_word_be_inserted. If it can be inserted, the word's intersections are determined
        and it is appended to the placements array (a list of dictionaries containing information
        about the word - the word itself, its direction, its position and its intersections)'''
        placements = list()

        for row in range(self.dimensions):
            for column in range(self.dimensions):
                if self._can_word_be_inserted(word, Directions.ACROSS, row, column):
                    intersections = self._find_intersections(word, Directions.ACROSS, row, column)
                    placements.append({
                        "word": word,
                        "direction": Directions.ACROSS,
                        "pos": (row, column),
                        "intersections": intersections})

                if self._can_word_be_inserted(word, Directions.DOWN, row, column):
                    intersections = self._find_intersections(word, Directions.DOWN, row, column)
                    placements.append({
                        "word": word,
                        "direction": Directions.DOWN,
                        "pos": (row, column),
                        "intersections": intersections})

        return placements

    def _add_clue(self, placement, word):
        '''Add a clue to the self.clues dictionary. Increments each index of "pos" by 1 to be more
        understandable for the user as python indexes from 0'''
        self.clues[((placement["pos"][0] + 1, placement["pos"][1] + 1), 
            placement["direction"])] = self.definitions[word] # Retrieve the clue value for the 
                                                              # word key in self.definitions

    def _add_data(self, placement):
        '''Append placement data to either list 0 or 1 (across or down) in the self.data array'''
        if placement["direction"] == Directions.ACROSS:
            self.data[0].append(placement)
            
        elif placement["direction"] == Directions.DOWN:
            self.data[1].append(placement)

    def _populate_grid(self, words, insert_backlog=False):
        '''Call _find_insertion_coords to determine all the places a word can be inserted and choose
        the placement with the most intersections. If no intersections are present, it appends it to
        the array "uninserted_words_backlog" which will be inserted later when the function is recursed
        with that array as the "words" parameter'''
        if not insert_backlog: # First time execution
            self.backlog_has_been_inserted = False
            self.uninserted_words_backlog = list()
            self.inserts = 0
            self.fails = 0
            self.total_intersections = 0

        if self.inserts == 0:
                middle_placement = self._find_first_word_placement_position(words[0])
                self._place_word(middle_placement["word"], middle_placement["direction"],
                                 middle_placement["pos"][0], middle_placement["pos"][1])
                self._add_clue(middle_placement, words[0])
                self._add_data(middle_placement)
                del words[0] 
                self.inserts += 1
                
        for word in words: # Insert remaining words after the middle placement is complete
            placements = self._find_insertion_coords(word)
            placements = self._prune_placements_for_readability(placements)
            if not placements:
                self.fails += 1
                continue

            # Sort placements for the given word from highest to lowest intersections
            sorted_placements = sorted(placements, key=lambda k: k["intersections"], reverse=True)
            if not sorted_placements[0]["intersections"]: # No intersections present
                if not insert_backlog: # First time execution; append words here for eventual reinsertion
                    self.uninserted_words_backlog.append(word)
                    continue
                else: # Reinsertion didn't help much, just pick a random placement
                    placement = random.choice(sorted_placements)
            else: 
                placement = sorted_placements[0]

            self._place_word(placement["word"], placement["direction"], 
                             placement["pos"][0], placement["pos"][1])
            self._add_clue(placement, word)
            self._add_data(placement)
            self.total_intersections += len(placement["intersections"])
            self.inserts += 1

        if self.backlog_has_been_inserted: 
            return

        if self.uninserted_words_backlog and not self.backlog_has_been_inserted:
            self.backlog_has_been_inserted = True
            # Recurse _populate_grid with "uninserted_words_backlog"
            self._populate_grid(self.uninserted_words_backlog, insert_backlog=True) 
            
class CrosswordHelper():
    '''Contains static methods to help with the loading of necessary JSON files and for performing optimised crossword
    creation with `find_best_crossword`'''
    @staticmethod
    def find_best_crossword(crossword):
        '''Determines the best crossword out of a amount of instantiated crosswords based on the largest 
        amount of total intersections and smallest amount of fails'''
        name = crossword.name
        word_count = crossword.word_count
        
        attempts_db = CrosswordHelper._load_attempts_db(Paths.ATTEMPTS_DB_PATH)
        max_attempts = attempts_db[str(word_count)] # Get specified amount of attempts based on word count
        attempts = 0

        reinsert_definitions = crossword.definitions
        crossword.generate()
        best_crossword = crossword
        
        while attempts < max_attempts:
            # Setting the "retry" param to True will make the Crossword class only randomise the 
            # definitions it is given, not sample new random ones
            crossword = Crossword(name=name, definitions=reinsert_definitions, word_count=word_count, retry=True)
            crossword.generate()
            # Ensure the crossword with the most intersections is always assigned to best_crossword
            if crossword.total_intersections > best_crossword.total_intersections and crossword.fails <= best_crossword.fails: 
                best_crossword = crossword
            attempts += 1
        
        return best_crossword

    @staticmethod
    def load_definitions(file_path):
        '''Load a definitions json from the current directory'''
        try:
            with open(file_path, "r") as file:
                definitions = json.load(file)
        except json.decoder.JSONDecodeError:
            raise EmptyDefinitions
        
        return definitions

    @staticmethod
    def _load_attempts_db(file_path):
        '''Load a json that specifies the amount of attempts a crossword should be recreated based on
        the amount of words that crossword will contain'''
        with open(file_path, "r") as file:
            attempts_db = json.load(file)
        
        return attempts_db


if __name__ == "__main__": # Example usage
    definitions = CrosswordHelper.load_definitions(f"{Paths.CROSSWORDS_PATH}/capitals.json")
    
    crossword = Crossword(definitions=definitions, word_count=100, name="Capitals")
    crossword = CrosswordHelper.find_best_crossword(crossword)   
    
    # You can also generate a single crossword:
    # crossword = Crossword(definitions=definitions, word_count=10, name="Capitals")
    # crossword.generate

    print(crossword)