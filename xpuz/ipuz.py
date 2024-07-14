from datetime import date
from json import dump

from xpuz.wrappers import CrosswordWrapper
from xpuz.td import IPuzV2
from xpuz.constants import EMPTY
from xpuz.utils import GUIHelper, _get_saveas_filename


class IPuz(dict):
    def __init__(
        self,
        cwrapper: CrosswordWrapper,
        # Refer to ``utils._interpret_cword_data`` for information on these params
        starting_word_matrix,
        definitions_a,
        definitions_d,
    ) -> None:
        self.cwrapper = cwrapper
        self.crossword = self.cwrapper.crossword

        self.starting_word_matrix = starting_word_matrix
        self.definitions_a, self.definitions_d = definitions_a, definitions_d

    def write(self) -> None:
        filepath = _get_saveas_filename(
            _("Select a destination to export your ipuz to"),
            self.cwrapper.display_name,
            ".json",
            [("JSON files", "*.json")],
        )
        if not filepath:
            return
        if not filepath.endswith(".ipuz.json"):
            filepath += ".ipuz.json"

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
