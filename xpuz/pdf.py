from os import PathLike
from typing import List
from platformdirs import user_downloads_dir
from tkinter import filedialog

from cairo import (
    FONT_SLANT_NORMAL,
    FONT_WEIGHT_BOLD,
    FONT_WEIGHT_NORMAL,
    Context,
    PDFSurface,
)

from xpuz.constants import (
    EMPTY,
    FONTSIZE_DEF,
    FONTSIZE_DIR_TITLE,
    PAGE_DEF_MAX,
    PDF_HEIGHT,
    PDF_MARGIN,
    PDF_WIDTH,
)
from xpuz.wrappers import CrosswordWrapper
from xpuz.utils import GUIHelper


class PDF:
    """Provides the functionality to create a PDF with the an empty crossword
    grid and its definitions, as well as the completed crossword grid.

    DISCLAIMER: Cannot draw crosswords that contains complex glyphs, such as
    Mandarin and Japanese, due to limitations with ``cairo``.
    """

    def __init__(
        self,
        cwrapper: CrosswordWrapper,
        # Refer to ``utils._interpret_cword_data`` for information on these params
        starting_word_positions,
        starting_word_matrix,
        definitions_a,
        definitions_d,
    ) -> None:
        self.cwrapper = cwrapper
        self.crossword = self.cwrapper.crossword
        self.grid: List[List[str]] = self.crossword.grid
        self.dimensions: int = self.crossword.dimensions
        self.drawn: bool = False
        self.display_name = f"{self.cwrapper.translated_name} ({_(self.cwrapper.difficulty)})"

        self.starting_word_positions = starting_word_positions
        self.starting_word_matrix = starting_word_matrix
        self.definitions_a, self.definitions_d = definitions_a, definitions_d
        self.definitions_a_backlog, self.definitions_d_backlog = [], []
        self.backlog_inserted: bool = False
        self.display_name_answer = self.display_name + f" - {_('Answers')}"

        # Calculating relative side length of each cell, then using that value
        # to calculate the remaining measurements and font sizes
        self.cell_dim: float = (PDF_HEIGHT - 2 * PDF_MARGIN) / self.dimensions
        self.grid_dim: float = self.dimensions * self.cell_dim
        self.num_label_fontsize = self.cell_dim * 0.3
        self.cell_fontsize = self.cell_dim * 0.8

    def write(self) -> None:
        filepath = PDF._get_pdf_filepath(self.display_name)
        if not filepath:
            bad_filepath = True
        else:
            if not filepath.endswith(".pdf"):
                filepath += ".pdf"
            bad_filepath = False
            
        try:
            if not bad_filepath:
                self._s: PDFSurface = PDFSurface(filepath, PDF_WIDTH, PDF_HEIGHT)
                self._c: Context = Context(self._s)
                self._c.set_line_width(1)

                self._draw_all()
                self.drawn = True
        except Exception:
            pass
            
        self._on_finish()
    
    @staticmethod
    def _get_pdf_filepath(name: str) -> PathLike:
        return filedialog.asksaveasfilename(
            title=_("Select a destination to download your PDF to"),
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialdir=user_downloads_dir(),
            initialfile=name + ".pdf",
        )
    
    def _on_finish(self) -> None:
        if not self.drawn:
            return GUIHelper.show_messagebox(pdf_write_err=True)
        else:
            fails = self.crossword.fails
            if fails > 0:
                return GUIHelper.show_messagebox(fails, pdf_write_success=True)
            else:
                return GUIHelper.show_messagebox(pdf_write_success=True)

    def _set_font_face(
        self,
        family: str = "Arial",
        slant=FONT_SLANT_NORMAL,
        weight=FONT_WEIGHT_BOLD,
    ) -> None:
        self._c.select_font_face(family, slant, weight)

    def _draw_all(self) -> None:
        """Driver function to draw the PDF."""
        self._draw_grid()
        self._draw_display_name(self.display_name)

        self._s.show_page()
        self._c = Context(self._s)
        self._draw_definitions()

        self._s.show_page()
        self._c = Context(self._s)
        self._draw_grid(with_answers=True)
        self._draw_display_name(self.display_name_answer)

        self._s.finish()

    def _draw_grid(self, with_answers=False) -> None:
        """Draw the crossword grid in the center of the page."""
        offset_x: float = (PDF_WIDTH - 2 * PDF_MARGIN - self.grid_dim) / 2
        offset_y: float = (PDF_HEIGHT - 2 * PDF_MARGIN - self.grid_dim) / 2
        self._c.translate(PDF_MARGIN, PDF_MARGIN)
        # Begin drawing after allowing space for the margin in the prior line
        self._c.translate(offset_x, offset_y)

        # This structure is very similar to the Jinja2 in ``app/templates/index.html``
        for row in range(self.dimensions):
            for col in range(self.dimensions):
                if self.grid[row][col] == EMPTY:  # Void cell
                    self._c.set_source_rgb(0, 0, 0)
                    self._c.rectangle(
                        col * self.cell_dim,
                        row * self.cell_dim,
                        self.cell_dim,
                        self.cell_dim,
                    )
                    self._c.fill()

                else:  # This cell has text
                    self._c.set_source_rgb(1, 1, 1)
                    self._c.rectangle(
                        col * self.cell_dim,
                        row * self.cell_dim,
                        self.cell_dim,
                        self.cell_dim,
                    )
                    self._c.fill()

                    if with_answers:  # Also draw the letter in the cell
                        self._draw_cell_letter(row, col)

                # This is the start of a word, draw a number label
                if (row, col) in self.starting_word_positions:
                    self._draw_number_label(row, col)

        self._draw_grid_lines()  # Separate the cells

    def _draw_cell_letter(self, row: int, col: int) -> None:
        """Draw ``self.grid[row][col]``, using ``row`` and ``col`` as a reference
        to determine the drawing location.
        """
        self._c.set_source_rgb(0, 0, 0)
        self._c.set_font_size(self.cell_fontsize)
        self._set_font_face(weight=FONT_WEIGHT_NORMAL)

        letter = self.crossword.grid[row][col]
        text_extents = self._c.text_extents(letter)

        x_position = (
            col * self.cell_dim + (self.cell_dim - text_extents.width) / 2.2
        )
        y_position = row * self.cell_dim + self.cell_fontsize * 1.2

        self._c.move_to(x_position, y_position)
        self._c.show_text(letter)

    def _draw_number_label(self, row: int, col: int) -> None:
        """Draw a number label in the top left hand corner of the cell at ``row``
        and ``col``.
        """
        self._c.set_source_rgb(0, 0, 0)

        self._c.set_font_size(self.num_label_fontsize)
        self._set_font_face(weight=FONT_WEIGHT_NORMAL)
        self._c.move_to(
            col * self.cell_dim + self.num_label_fontsize / 4,
            row * self.cell_dim + self.num_label_fontsize,
        )
        self._c.show_text(str(self.starting_word_matrix[row][col]))

    def _draw_grid_lines(self) -> None:
        """Draw lines in between all of the cells."""
        self._c.set_source_rgb(0, 0, 0)

        for row in range(
            self.dimensions + 1
        ):  # Account for far right and bottom
            # edges by adding 1
            self._c.move_to(0, row * self.cell_dim)
            self._c.line_to(
                self.dimensions * self.cell_dim, row * self.cell_dim
            )
            self._c.stroke()

        for col in range(self.dimensions + 1):
            self._c.move_to(col * self.cell_dim, 0)
            self._c.line_to(
                col * self.cell_dim, self.dimensions * self.cell_dim
            )
            self._c.stroke()

    def _draw_display_name(self, name: str) -> None:
        """Draw ``name`` at the top of the current page."""
        self._c.set_source_rgb(0, 0, 0)

        self._c.set_font_size(60.0)
        self._set_font_face()
        self._c.move_to(
            (self.grid_dim - self._c.text_extents(self.display_name).width)
            / 2,
            -50,
        )
        self._c.show_text(name)

    def _draw_definitions(self) -> None:
        """Driver function to draw both columns of a crossword's definitions."""
        self._draw_definitions_col(
            self.definitions_a,
            _("Across"),
            PDF_MARGIN,
            PDF_MARGIN * 1.5,
            self.definitions_a_backlog,
        )
        self._draw_definitions_col(
            self.definitions_d,
            _("Down"),
            PDF_WIDTH / 2 + 20,
            PDF_MARGIN * 1.5,
            self.definitions_d_backlog,
        )

        # Some definitions could not fit, so recurse ``self._draw_definitions``
        if not self.backlog_inserted and (
            self.definitions_a_backlog or self.definitions_d_backlog
        ):
            self.backlog_inserted = True
            self._s.show_page()
            self._c = Context(self._s)
            # Update definitions arrays to their respective backlogs
            self.definitions_a = self.definitions_a_backlog
            self.definitions_d = self.definitions_d_backlog
            self._draw_definitions()

    def _draw_definitions_col(
        self,
        definitions,
        dir_title: str,
        start_x: float,
        start_y: float,
        backlog: List,
    ) -> None:
        """Draw either the across or down definitions column.

        DISCLAIMER: Does not provide wrapping for clues.
        """
        definitions_x: float = (
            start_x + ((PDF_WIDTH - 2 * PDF_MARGIN) / 2 - 40) / 2
        )

        # Draw "Across" or "Down"
        self._c.set_source_rgb(0, 0, 0)
        self._c.set_font_size(FONTSIZE_DIR_TITLE)
        self._set_font_face()
        self._c.move_to(
            definitions_x - self._c.text_extents(dir_title).width / 2, start_y
        )
        self._c.show_text(dir_title)

        y = start_y + FONTSIZE_DIR_TITLE + 60
        self._c.set_font_size(FONTSIZE_DEF)
        self._set_font_face(weight=FONT_WEIGHT_NORMAL)

        for i, definition in enumerate(definitions):
            # These definitions would go off the page, so skip them and append
            # them to ``backlog``
            if i + 1 > PAGE_DEF_MAX and not self.backlog_inserted:
                backlog.append(definition)
                continue

            for number, (word, clue) in definition.items():
                text = f"{number}. {clue}"
                self._c.move_to(
                    definitions_x - self._c.text_extents(text).width / 2, y
                )
                self._c.show_text(text)
                y += FONTSIZE_DEF * 2
