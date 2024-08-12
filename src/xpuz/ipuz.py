"""Module implementing ``ipuz`` export functionality."""

from datetime import date
from json import dump
from typing import List, Dict, Tuple

from xpuz.wrappers import CrosswordWrapper
from xpuz.td import IPuzV2
from xpuz.constants import EMPTY
from xpuz.utils import GUIHelper, _get_saveas_filename


class IPuz(dict):
    """Export a generated crossword in ``ipuz`` format."""

    def __init__(
        self,
        cwrapper: CrosswordWrapper,
        starting_word_matrix: List[List[int]],
        definitions_a: List[Dict[int, Tuple[str]]],
        definitions_d: List[Dict[int, Tuple[str]]],
    ) -> None:
        """Initialise crossword data and the crossword wrapper object.

        Args:
            cwrapper: The crossword wrapper.
            starting_word_matrix: 
                [read this function](utils.md#xpuz.utils._interpret_cword_data)
            definitions_a: 
                [read this function](utils.md#xpuz.utils._interpret_cword_data)
            definitions_d: 
                [read this function](utils.md#xpuz.utils._interpret_cword_data)
        """
        self.cwrapper = cwrapper
        self.crossword = self.cwrapper.crossword

        self.starting_word_matrix = starting_word_matrix
        self.definitions_a, self.definitions_d = definitions_a, definitions_d

    def write(self) -> None:
        """Compile the data of the generated crossword into ``self``, and write
        it to ``filepath``.
        """
        filepath = _get_saveas_filename(
            _("Select a destination to export your ipuz to"),
            self.cwrapper.display_name,
            ".json",
            [("JSON files", "*.json")],
        )
        if not filepath:
            return
        if not filepath.endswith(".json"):
            filepath += ".ipuz.json"
        else:
            filepath = filepath.replace(".json", ".ipuz.json")

        self = IPuzV2.create(
            dimensions={
                "width": self.crossword.dimensions,
                "height": self.crossword.dimensions,
            },
            puzzle=self.starting_word_matrix,
            solution=list(
                map(
                    lambda row: [
                        cell if cell != EMPTY else None for cell in row
                    ],
                    self.crossword.grid,
                )
            ),
            clues={
                "Across": [
                    [
                        list(definition.keys())[0],
                        list(definition.values())[0][1],
                    ]
                    for definition in self.definitions_a
                ],
                "Down": [
                    [
                        list(definition.keys())[0],
                        list(definition.values())[0][1],
                    ]
                    for definition in self.definitions_d
                ],
            },
            date=date.today().strftime("%m/%d/%Y"),
            difficulty=self.cwrapper.translated_difficulty,
            title=self.cwrapper.translated_name,
        )

        with open(filepath, "w") as f:
            dump(self, f, indent=None)
        GUIHelper.show_messagebox(ipuz_write_success=True)
