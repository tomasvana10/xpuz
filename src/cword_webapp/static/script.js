/* `script.js` implements various functions allow the crossword grid to be interacted with by the user. 
Additionally, this script offers automatic detection of crossword completion, and relays this 
information to the user. 
*/

let grid, dimensions, empty, definitions_a, definitions_d; // Jinja2 template variables
let direction = 'ACROSS',
    cellCoords = null,
    currentCell = null,
    futureCoords = null,
    mode = null;

const FOCUSED_CELL_COLOUR = "#a7d8ff";
const UNFOCUSED_CELL_COLOUR = "whitesmoke"; // for now


document.addEventListener("DOMContentLoaded", () => { // On page load
    const body = document.querySelector("body");

    /// Retrieve Jinja2 template variables
    grid = eval(body.getAttribute("data-grid")); /* Convert Python array to JS array */
    dimensions = parseInt(body.getAttribute("data-dimensions"));
    empty = body.getAttribute("data-empty");
    definitions_a = body.getAttribute("data-definitions_a");
    definitions_d = body.getAttribute("data-definitions_d");
});


document.addEventListener("keydown", (event) => { // Detect user input
    if (cellCoords === null) return; // User hasn't selected a cell

    let inputValue = event.key; 
    mode = (inputValue == "Backspace" || inputValue == "Delete") ? "del" : "enter"
    if (mode != "del") {
        if (!(inputValue.length == 1 && inputValue.match(/\p{L}/u))) return; // Input isn't a language char

        currentCell = getInputCellElement(cellCoords);
        currentCell.childNodes[0].nodeValue = inputValue; // Using nodes prevents any `num_label` elements from being deleted
    } else {
        currentCell = getInputCellElement(cellCoords);
        currentCell.childNodes[0].nodeValue = "";
    };
    
    if (checkIfCrosswordIsComplete()) { alert("You completed the crossword!") };
    
    changeCellFocus(currentCell, focus=false);
    cellCoords = shiftCellCoords(cellCoords, direction, mode);
    currentCell = getInputCellElement(cellCoords);
    changeCellFocus(currentCell, focus=true);
});

function shiftCellCoords(coords, dir, mode) {
    if (mode == "enter") {
        futureCoords = dir == "DOWN"
                            ? [coords[0] + 1, coords[1]]
                            : [coords[0], coords[1] + 1]
    } else if (mode == "del") {
        futureCoords = dir == "DOWN"
                            ? [coords[0] - 1, coords[1]]
                            : [coords[0], coords[1] - 1]
    };
    let futureCell = getInputCellElement(futureCoords);
    
    return futureCell !== null && futureCell.classList.contains('non_empty_cell')
           ? futureCoords /* If the cell at the future coords has the `non_empty_cell` class */
           : coords; /* Keep the coords at the current cell */
};

function onDefinitionsListItemClick(num_label, dir) { // Click on a word's definitions -> set input to start of that word
    if (currentCell !== null) { changeCellFocus(currentCell, focus=false) };
    
    // Retrieve the new cell element from the parent of the number label element
    currentCell = document.querySelector(`[data-num_label="${num_label}"]`).parentElement;
    updateCellCoords(currentCell);
    changeCellFocus(currentCell, focus=true);
    direction = dir; 
};

function onCellClick(cell) {
    if (currentCell !== null) { changeCellFocus(currentCell, focus=false) };

    currentCell = cell
    updateCellCoords(cell);
    changeCellFocus(cell, focus=true);
    direction = shiftCellCoords(cellCoords, 'ACROSS', mode="enter") == cellCoords ? 'DOWN' : 'ACROSS';
};

function updateCellCoords(cell) {
    cellCoords = [parseInt(cell.getAttribute("data-row")), parseInt(cell.getAttribute("data-column"))];
};

function changeCellFocus(cell, focus) {
    cell.style.backgroundColor = focus ? FOCUSED_CELL_COLOUR : UNFOCUSED_CELL_COLOUR;
};

function getInputCellElement(cellCoords) {
    return cellCoords 
            ? document.querySelector(`[data-row="${cellCoords[0]}"][data-column="${cellCoords[1]}"]`) 
            : true;
};

function checkIfCrosswordIsComplete() {
    // Compare all table cells with the grid, and if they are identical, return true
    let webAppGrid = getWebAppGrid(); 
    return webAppGrid.every((row, i) => row.every((cell, j) => cell == grid[i][j]));
};

function getWebAppGrid() {
    // Create an empty replica of the crossword grid, then update it according to the web app grid.
    let nonEmptyCellElements = document.querySelectorAll(".non_empty_cell");
    let webAppGrid = Array.from({length: dimensions}, () => Array(dimensions).fill(empty));

    nonEmptyCellElements.forEach((cell) => {
        let row = parseInt(cell.getAttribute("data-row"));
        let column = parseInt(cell.getAttribute("data-column"));
        let value = cell?.childNodes[0]?.nodeValue.toUpperCase() ?? empty 
        webAppGrid[row][column] = value;
    });

    return webAppGrid;
};