/* `script.js` implements various functions allow the crossword grid to be interacted with by the user. 
Additionally, this script offers automatic detection of crossword completion, and relays this 
information to the user. 
*/

let grid, dimensions, empty, colour_palette, intersections; // Jinja2 template variables
let direction = "ACROSS",
    cellCoords = null;

const isEmpty = (cell) => !cell?.childNodes[0]?.nodeValue;
const setValue = (cell, value) => cell.childNodes[0].nodeValue = value; // Using nodes prevents any `num_label` elements from being deleted
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
Array.prototype.isEqualTo = function(arr) { return JSON.stringify(this) === JSON.stringify(arr); }   // Add a method to the Array class

document.addEventListener("DOMContentLoaded", () => { // On page load
    const body = document.querySelector("body");

    /// Retrieve Jinja2 template variables
    grid = eval(body.getAttribute("data-grid")); /* Convert Python array to JS array */
    dimensions = parseInt(body.getAttribute("data-dimensions"));
    empty = body.getAttribute("data-empty");
    colour_palette = eval(body.getAttribute("data-colour_palette"));
    intersections = eval(body.getAttribute("data-intersections"));

    // Reset all non-empty cells to empty strings (issue with HTML)
    document.querySelectorAll(".non_empty_cell").forEach(cell => setValue(cell, "")); 
});


document.addEventListener("keydown", (event) => {
    /* Handle user input - either set the value of the current cell to the user's input (if valid) or
    perform cell deletion. */
    if (cellCoords === null) return; // User hasn't selected a cell

    let inputValue = event.key; 
    let mode = (inputValue == "Backspace" || inputValue == "Delete") ? "del" : "enter";
    let currentCell = getInputCellElement(cellCoords);

    if (mode == "enter") {
        if (!(inputValue.length === 1 && inputValue.match(/\p{L}/u))) return; // Input isn't a language char
        setValue(currentCell, inputValue);
    } else {
        // User is focused on cell with text, just delete cell text
        if (!isEmpty(currentCell)) { setValue(currentCell, ""); return; }
        // User is focused on cell with no text, shift input backwards then delete what is in that cell
        setValue(getInputCellElement(shiftCellCoords(cellCoords, direction, "del")), "");
    }
    
    if (checkIfCrosswordIsComplete()) { sleep(1).then(() => alert("You completed the crossword!")); }
    
    // Remove focus from the old cell, get coords of the new cell, then focus the new word and cell
    changeCellFocus(focus=false);
    cellCoords = shiftCellCoords(cellCoords, direction, mode);
    changeWordFocus(focus=true);
    changeCellFocus(focus=true);
});

function shiftCellCoords(coords, dir, mode) {
    /* Move the input forward or backward based on the `mode` parameter. If no such cell exists at
    these future coordinates, the original coordinates are returned. */
    let offset = (mode == "enter") ? 1 : -1;
    let futureCoords = (dir == "DOWN") ? [coords[0] + offset, coords[1]] : [coords[0], coords[1] + offset];
    let futureCell = getInputCellElement(futureCoords);

    return futureCell !== null && futureCell.classList.contains("non_empty_cell")
           ? futureCoords // Cell at future coords is a non empty cell
           : coords; // Cell at future coords is empty/black, cannot move to it
}

function onDefinitionsListItemClick(num_label, dir) {
    /* If the user is already focused on a word, remove both its focus and the individual cell focus, 
    then update the direction, cell coordinates and refocus appropriately. */
    if (cellCoords !== null) { changeWordFocus(focus=false); changeCellFocus(focus=false); }

    // Get new cell element from parent of the number label
    let cell = document.querySelector(`[data-num_label="${num_label}"]`).parentElement;
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
    // Update direction according to the new cell coordinates
    if (JSON.stringify(intersections).includes(JSON.stringify(newCellCoords)) && newCellCoords.isEqualTo(cellCoords)) {
        direction = direction == "ACROSS" ? "DOWN" : "ACROSS"; // Alternate the direction.

    } else if (shiftCellCoords(newCellCoords, direction, "enter").isEqualTo(newCellCoords) 
              && shiftCellCoords(newCellCoords, direction, "del").isEqualTo(newCellCoords)) {
        // If the future cell has no adjacent cells in the current direction then alternate the direction. Otherwise, keep it.
        direction = direction == "ACROSS" ? "DOWN" : "ACROSS"; 
    }
    cellCoords = newCellCoords;
    changeWordFocus(focus=true);
    changeCellFocus(focus=true);
}

function updateCellCoords(cell) {
    return [parseInt(cell.getAttribute("data-row")), parseInt(cell.getAttribute("data-column"))];
}

function changeCellFocus(focus) {
    getInputCellElement(cellCoords).style.backgroundColor = focus ? colour_palette[5] : colour_palette[1];
}

function changeWordFocus(focus) {
    let [row, col] = cellCoords;
    let isDown = direction == "DOWN";
    let [startCoords, endCoords] = isDown ? [row, row] : [col, col];

    // Find starting coords of the word
    while (startCoords > 0 && grid[isDown ? startCoords - 1 : row][isDown ? col : startCoords - 1] != empty) {
        startCoords--;
    }

    // Find ending coords of the word
    while (endCoords < dimensions - 1 && grid[isDown ? endCoords + 1 : row][isDown ? col : endCoords + 1] != empty) {
        endCoords++;
    }

    // Highlight the entire word
    for (let i = startCoords; i <= endCoords; i++) {
        let coords = isDown ? [i, col] : [row, i];
        getInputCellElement(coords).style.backgroundColor = focus ? colour_palette[4] : colour_palette[1];
    }
}

function getInputCellElement(coords) {
    return document.querySelector(`[data-row="${coords[0]}"][data-column="${coords[1]}"]`);
}

function checkIfCrosswordIsComplete() {
    // Compare all table cells with the grid, and if they are identical, return true
    return JSON.stringify(getWebAppGrid()) == JSON.stringify(grid);
}

function getWebAppGrid() {
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