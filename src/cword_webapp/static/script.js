/* `script.js` implements various functions allow the crossword grid to be interacted with by the user. 
Additionally, this script offers automatic detection of crossword completion, and relays this 
information to the user. 
*/

let grid, dimensions, empty, colour_palette, intersections; // Jinja2 template variables
let direction = "ACROSS",
    cellCoords = null,
    staticIndex = null,
    isDown = null;
const arrowKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"];

const isEmpty = (cell) => !cell?.childNodes[0]?.nodeValue || cell.childNodes[0].nodeValue === " ";
const setValue = (cell, value) => cell.childNodes[0].nodeValue = value; // Using nodes prevents any `num_label` elements from being deleted
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
Array.prototype.isEqualTo = function(arr) { return JSON.stringify(this) === JSON.stringify(arr); };


document.addEventListener("DOMContentLoaded", () => { // On page load
    const body = document.querySelector("body");

    grid = eval(body.getAttribute("data-grid")); /* Convert Python array to JS array */
    dimensions = parseInt(body.getAttribute("data-dimensions"));
    empty = body.getAttribute("data-empty");
    colour_palette = JSON.parse(body.getAttribute("data-colour_palette"));
    intersections = eval(body.getAttribute("data-intersections"));

    // Reset all non-empty cells to empty strings (issue with HTML)
    document.querySelectorAll(".non_empty_cell").forEach(cell => setValue(cell, "")); 
});


document.addEventListener("keydown", (event) => {
    /* Handle user input - either set the value of the current cell to the user's input (if valid),
    perform cell deletion, or remove the word/cell focus entirely. */
    if (cellCoords === null) return; // User hasn't selected a cell

    let inputValue = event.key === "Spacebar" ? " " : event.key; // Must account for the browser returning "Spacebar" 
    if (arrowKeys.includes(inputValue)) { handleArrowPress(inputValue); }
    if (inputValue === "Escape") { changeCellFocus(focus=false); changeWordFocus(focus=false); cellCoords = null; return; }
    let mode = (inputValue === "Backspace" || inputValue === "Delete") ? "del" : "enter";
    let currentCell = getCellElement(cellCoords);

    if (mode === "enter") {
        if (!(inputValue.length === 1 && (inputValue.match(/\p{L}/u) || inputValue === " "))) return;
        setValue(currentCell, inputValue);
    } else {
        // User is focused on cell with text, just delete cell text
        if (!isEmpty(currentCell)) { setValue(currentCell, ""); return; }
        // User is focused on cell with no text, shift input backwards then delete what is in that cell
        setValue(getCellElement(shiftCellCoords(cellCoords, direction, mode)), "");
    }
    
    if (isCrosswordComplete()) { sleep(1).then(() => alert("You completed the crossword!")); }
    
    changeCellFocus(focus=false);
    cellCoords = shiftCellCoords(cellCoords, direction, mode);
    changeWordFocus(focus=true);
    changeCellFocus(focus=true);
});

function handleArrowPress(key) {
    /* Determine how the program responds to the user pressing an arrow. First, see if a "enter" or
    "del" shift is performed and in what direction. Then, ensure the user is not shifting into a
    `.empty` cell. Finally, alternate the direction if necessary and refocus. */
    let mode = (key === "ArrowDown" || key === "ArrowRight") ? "enter" : "del";
    let dir = (key === "ArrowDown" || key === "ArrowUp") ? "DOWN" : "ACROSS";
    // Force shift the cell coords to see if the coordinates of a .empty_cell are returned
    let newCellCoords = shiftCellCoords(cellCoords, dir, mode, true);
    if (getCellElement(newCellCoords).classList.contains("empty_cell")) { return; }

    changeWordFocus(focus=false);
    changeCellFocus(focus=false);
    direction = (dir !== direction) ? dir : direction; // User is switching from a row to a column or vice versa
    cellCoords = newCellCoords;
    changeWordFocus(focus=true);  
    changeCellFocus(focus=true);
}

function shiftCellCoords(coords, dir, mode, force=false) {
    /* Move the input forward or backward based on the `mode` parameter. If no such cell exists at
    these future coordinates (and the force param is false), the original coordinates are returned. */
    let offset = (mode == "enter") ? 1 : -1;
    let futureCoords = (dir == "DOWN") ? [coords[0] + offset, coords[1]] : [coords[0], coords[1] + offset];
    let futureCell = getCellElement(futureCoords);

    return futureCell !== null && futureCell.classList.contains("non_empty_cell") || force
           ? futureCoords // Cell at future coords is a non empty cell
           : coords; // Cell at future coords is empty/black, cannot move to it
}

function onDefinitionsListItemClick(numLabel, dir) {
    /* If the user is already focused on a word, remove both its focus and the individual cell focus, 
    then update the direction, cell coordinates and refocus appropriately. */
    if (cellCoords !== null) { changeWordFocus(focus=false); changeCellFocus(focus=false); }

    // Get new cell element from parent of the number label
    let cell = document.querySelector(`[data-num_label="${numLabel}"]`).parentElement;
    direction = dir;
    cellCoords = updateCellCoords(cell);
    changeWordFocus(focus=true);
    changeCellFocus(focus=true);
}

function onCellClick(cell) {
    /* Handles how the grid responds to a user clicking on the cell. Ensures the appropriate display
    of the current cell and word focus on cell click, as well as alternating input directions if
    clicking at an intersecting point between two words. */
    if (cellCoords !== null) { changeWordFocus(focus=false); changeCellFocus(focus=false); }

    let newCellCoords = updateCellCoords(cell);
    // User is clicking on an intersection for the second time, so alternate the direction
    if (JSON.stringify(intersections).includes(JSON.stringify(newCellCoords)) && newCellCoords.isEqualTo(cellCoords)) 
        direction = direction === "ACROSS" ? "DOWN" : "ACROSS"; // Alternate the direction.

    // Cannot shift the cell in the original direction, so it must be alternated
    else if (shiftCellCoords(newCellCoords, direction, "enter").isEqualTo(newCellCoords) 
            && shiftCellCoords(newCellCoords, direction, "del").isEqualTo(newCellCoords)) 
        direction = direction === "ACROSS" ? "DOWN" : "ACROSS"; 
    
    cellCoords = newCellCoords;
    changeWordFocus(focus=true);
    changeCellFocus(focus=true);
}

function updateCellCoords(cell) {
    return [parseInt(cell.getAttribute("data-row")), parseInt(cell.getAttribute("data-column"))];
}

function changeCellFocus(focus) {
    getCellElement(cellCoords).style.backgroundColor = focus ? colour_palette.CELL_FOCUS : colour_palette.SUB;
}

function changeWordFocus(focus) {
    let [startCoords, endCoords] = getWordIndices();
    for (let i = startCoords; i <= endCoords; i++) {
        let coords = isDown ? [i, staticIndex] : [staticIndex, i];
        getCellElement(coords).style.backgroundColor = focus ? colour_palette.WORD_FOCUS : colour_palette.SUB;
    }
}

function getWordIndices() {
    let [row, col] = cellCoords;
    isDown = direction === "DOWN";
    staticIndex = isDown ? col : row;
    let [startCoords, endCoords] = isDown ? [row, row] : [col, col];

    // Find starting coords of the word
    while (startCoords > 0 && grid[isDown ? startCoords - 1 : row][isDown ? col : startCoords - 1] != empty)
        startCoords--;

    // Find ending coords of the word
    while (endCoords < dimensions - 1 && grid[isDown ? endCoords + 1 : row][isDown ? col : endCoords + 1] != empty) 
        endCoords++;

    return [startCoords, endCoords];
}

function getCellElement(coords) {
    return document.querySelector(`[data-row="${coords[0]}"][data-column="${coords[1]}"]`);
}

function isCrosswordComplete() {
    return getGrid().isEqualTo(grid);
}

function getGrid() {
    // Create an empty replica of the crossword grid, then update it according to the web app grid.
    let webAppGrid = Array.from({ length: dimensions }, () => Array(dimensions).fill(empty));

    document.querySelectorAll(".non_empty_cell").forEach((cell) => {
        let row = parseInt(cell.getAttribute("data-row"));
        let column = parseInt(cell.getAttribute("data-column"));
        let value = cell.childNodes[0].nodeValue.toUpperCase();
        webAppGrid[row][column] = value;
    });

    return webAppGrid;
}