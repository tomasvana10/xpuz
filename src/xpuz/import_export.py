"""Crossword editor-related utilities for importing and exporting a user's
crosswords through JSON files.
"""

from json import dump, load
from os import PathLike, mkdir, path, rmdir
from typing import Any, List

from xpuz.td import CrosswordData, CrosswordInfo
from xpuz.utils import GUIHelper, _get_saveas_filename, _get_open_filename


class Export(list):
    """Export all the crosswords a user has made into a single JSON file."""

    def __init__(self, blocks: List["UserCrosswordBlock"]) -> None:
        """Initialise the `self.blocks` array and export-related booleans.

        Args:
            blocks: The available user crossword blocks
        """
        self.blocks = blocks
        self.exported: bool = False
        self.no_filepath: bool = False

    def start(self) -> None:
        """Commence the export process and provide information once it is done."""
        self._assemble()
        self._export()

        if self.no_filepath:
            return None

        if self.exported:
            return GUIHelper.show_messagebox(export_success=True)
        else:
            return GUIHelper.show_messagebox(export_failure=True)

    def _export(self) -> None:
        """Write ``self`` to ``filepath``."""
        filepath = _get_saveas_filename(
            _("Select a destination to export your crosswords to"),
            _("my-crosswords"),
            ".json",
            [("JSON files", "*.json")],
        )

        if not filepath:
            self.no_filepath = True
            return

        if not filepath.endswith(".json"):
            filepath += ".json"
        try:
            with open(filepath, "w") as f:
                dump(self, f, indent=4)
        except Exception:
            return

        self.exported = True

    def _assemble(self) -> None:
        """Append all the user crossword crosswords to ``self``."""
        for block in self.blocks:
            cwrapper = block.cwrapper
            self.append(
                [
                    cwrapper.fullname,
                    {
                        "info": cwrapper.info,
                        "definitions": cwrapper.definitions,
                    },
                ]
            )


class Import:
    """Import a valid user-selected file to ``fp``."""

    def __init__(self, master: "CrosswordPane", fp: PathLike) -> None:
        """Initialise import-related booleans and lists.

        Args:
            master: The instance of the crossword pane.
            fp: The filepath to which the crosswords will be imported.
        """
        self.master = master
        self.fp = fp

        self.conflicting_fullnames: List[str] = []
        self.skipped_crossword_fullnames: List[str] = []
        self.imported_crossword_fullnames: List[str] = []
        self.imported: bool = False
        self.invalid_file: bool = False
        self.no_filepath: bool = False

    def start(self) -> None:
        """Commence the import process and provide information once it is done."""
        self._import()

        if self.no_filepath:
            return None

        if self.invalid_file:
            return GUIHelper.show_messagebox(import_failure=True)
        elif (
            self.imported
            and not self.conflicting_fullnames
            and not self.skipped_crossword_fullnames
        ):
            GUIHelper.show_messagebox(import_success=True)
        else:
            GUIHelper.show_messagebox(
                self.conflicting_fullnames,
                self.skipped_crossword_fullnames,
                partial_import_success=True,
            )

    def _import(self) -> None:
        """Read the contents of ``filepath`` and call ``self._write``."""
        filepath = _get_open_filename(
            _(
                "Select a valid crossword JSON file that was exported using xpuz"
            ),
            [("JSON files", "*.json")],
        )

        if not filepath:
            self.no_filepath = True
            return

        with open(filepath) as f:
            try:
                crosswords: Any = load(f)
            except Exception:
                self.invalid_file = True
                return

        if not isinstance(crosswords, list):
            self.invalid_file = True
            return

        self._write(crosswords)

    def _write(self, crosswords: Any) -> None:
        """Write ``crosswords`` to ``self.fp``, collecting information on invalid
        and conflicting crosswords.

        Args:
            crosswords: The crosswords to import.
        """
        for crossword in crosswords:
            if not isinstance(crossword, list) or len(crossword) != 2:
                self.invalid_file = True
                return

            name: str = crossword[0]
            crossword_data = crossword[1]
            toplevel: PathLike = path.join(self.fp, name)
            try:
                mkdir(toplevel)
            except FileExistsError:
                self.conflicting_fullnames.append(name)
                continue

            try:
                info: CrosswordInfo = crossword_data["info"]
                definitions: CrosswordData = crossword_data["definitions"]
                if not all(
                    key in info
                    for key in CrosswordInfo.__dict__["__annotations__"]
                ):
                    self.skipped_crossword_fullnames.append(name)
                    rmdir(toplevel)
                    continue

                self.master.master._write_data(toplevel, info, "info")
                self.master.master._write_data(
                    toplevel, definitions, "definitions"
                )
            except Exception:
                self.skipped_crossword_fullnames.append(name)
                continue

            self.imported_crossword_fullnames.append(name)

        self.imported = True
