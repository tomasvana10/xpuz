import random
import string
import json
import math

import regex # Similar to "re" module but with more functionality

class Directions:
    ACROSS = "a"
    DOWN = "d"


class Style:
    EMPTY = "▮"


class Restrictions:
    KEEP_LANGUAGES_PATTERN = r"\PL"
    

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
        self.clues = dict() 
        self.data = list([list(), list()])  

        if not (all(len(k) >= 3 for k in definitions.keys())):
            raise InsufficientWordLength

    def __str__(self):
        if not self.generated:
            raise PrintingCrosswordObjectBeforeGeneration
        
        return f"\nCrossword name: {self.name}\n" + \
            f"Word count: {self.inserts}, Failed insertions: {self.word_count - self.inserts}\n" + \
            f"Total intersections: {self.total_intersections}\n\n" + \
            "\n".join(" ".join(cell for cell in row) for row in self.grid) + "\n\n" + \
            "\n".join(f"{k}: {v}" for k, v in self.clues.items())

    def generate(self):
        if not self.generated:
            self.generated = True
            self._initialise_crossword_grid()
            self._populate_grid(list(self.definitions.keys()))
        else:
            raise AlreadyGeneratedCrossword

    def _format_definitions(self, definitions):
        if self.retry: 
            return dict(random.sample(list(definitions.items()), len(definitions))) 
        else:
            randomly_sampled_definitions = dict(random.sample(list(definitions.items()), self.word_count))
            formatted_definitions = {regex.sub(Restrictions.KEEP_LANGUAGES_PATTERN, "", k) .upper(): v \
                                    for k, v in randomly_sampled_definitions.items()}
            return formatted_definitions
    
    def _find_dimensions(self):
        total_char_count = sum(len(word) for word in self.definitions.keys())
        dimensions = math.ceil(math.sqrt(total_char_count * 1.85)) + 1
        if dimensions < (max_word_len := (len(max(self.definitions.keys(), key=len)))):
            dimensions = max_word_len

        return dimensions

    def _initialise_crossword_grid(self):
        self.grid = [[Style.EMPTY for i in range(self.dimensions)] for j in range(self.dimensions)]
    
    def _place_word(self, word, direction, row, column):
        if direction == Directions.ACROSS:
            for i in range(len(word)):
                self.grid[row][column + i] = word[i]

        if direction == Directions.DOWN:
            for i in range(len(word)):
                self.grid[row + i][column] = word[i]

    def _find_first_word_placement_position(self, word):
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
        if direction == Directions.ACROSS: 
            if column + len(word) > self.dimensions:
                return False

            for i in range(len(word)): 
                if self.grid[row][column + i] not in [Style.EMPTY, word[i]]:
                    return False
            
            if word[0] == self.grid[row][column] or word[-1] == self.grid[row][column + len(word) - 1]:
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

    def _find_insertion_coords(self, word):
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
        self.clues[((placement["pos"][0] + 1, placement["pos"][1] + 1), 
            placement["direction"])] = self.definitions[word] 

    def _add_data(self, placement):
        if placement["direction"] == Directions.ACROSS:
            self.data[0].append(placement)
            
        elif placement["direction"] == Directions.DOWN:
            self.data[1].append(placement)

    def _populate_grid(self, words, insert_backlog=False):
        if not insert_backlog: 
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
                
        for word in words: 
            placements = self._find_insertion_coords(word)
            if not placements:
                self.fails += 1
                continue

            sorted_placements = sorted(placements, key=lambda k: k["intersections"], reverse=True)
            if not sorted_placements[0]["intersections"]: 
                if not insert_backlog: 
                    self.uninserted_words_backlog.append(word)
                    continue
                else: 
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
            self._populate_grid(self.uninserted_words_backlog, insert_backlog=True) 