/* `script.js` implements various functions allow the crossword grid to be interacted with by the user. 
Additionally, this script offers automatic detection of crossword completion, and relays this 
information to the user. 
*/

let grid, dimensions, empty, definitions_a, definitions_d; // Jinja2 template variables
let direction = 'ACROSS',
    cellCoords = null,
    currentCell = null;

document.addEventListener("DOMContentLoaded", function() { // On page load
    const body = document.querySelector("body");

    /// Retrieve Jinja2 template variables
    grid = body.getAttribute("data-grid");
    dimensions = body.getAttribute("data-dimensions");
    empty = body.getAttribute("data-empty");
    definitions_a = body.getAttribute("data-definitions_a");
    definitions_d = body.getAttribute("data-definitions_d");
});

document.addEventListener("keydown", function(event) { // Detect user input
    if (cellCoords === null) { // User hasn't selected a cell
        return;
    };

    if (checkIfCrosswordIsComplete()) { // User has completed crossword
        alert("You completed the crossword!"); 
    };  

    let inputCellElement = getInputCellElementFromRowAndColumnData(cellCoords)
    currentCell = inputCellElement

    let inputValue = event.key; // Retrieve the character the user typed
    if (!(inputValue.length == 1 && inputValue.match(/[a-z]/i))) return; // If the input is not a letter (eg. ALT)
    inputCellElement.innerText = inputValue; // Update the grid accordingly

    cellCoords = shiftInputFocus();
    highlightInputFocus(getInputCellElementFromRowAndColumnData(cellCoords));
});

function shiftInputFocus() {
    let futureCoords = direction == 'DOWN' 
                       ? [cellCoords[0] + 1, cellCoords[1]] 
                       : [cellCoords[0], cellCoords[1] + 1];
    let futureCell = getInputCellElementFromRowAndColumnData(futureCoords);
    
    return futureCell !== null && futureCell.classList.contains('non_empty_cell')
           ? futureCoords
           : cellCoords
};

function onDefinitionsListItemClick(label, dir) { // Click on a word's definitions -> set input to start of that word
    // Search for the number label element by using definition list item's num_label data
    let numLabelElement = document.querySelector(`[data-num_label="${label}"]`);
    // Get the parent of the number label element, which is the cell
    let cellOfNumLabelElement = numLabelElement.parentElement;

    cellCoords = updateCellCoords(cellOfNumLabelElement);

    highlightInputFocus(cellOfNumLabelElement);

    direction = dir
};

function updateCellCoords(cell) {
    return [parseInt(cell.getAttribute("data-row")), parseInt(cell.getAttribute("data-column"))]
};

function highlightInputFocus(newCell) {
    //.style.backgroundColor = "white";     
    newCell.style.backgroundColor = "#a7d8ff";
};

function getInputCellElementFromRowAndColumnData(cellCoords) {
    return cellCoords ? document.querySelector(`[data-row="${cellCoords[0]}"][data-column="${cellCoords[1]}"]`) : null;
}

function checkIfCrosswordIsComplete() {
    // Compare all table cells with the grid, and if they are identical, tell the user they have 
    // completed the crossword.
    let webAppGrid = getWebAppGrid(); // Get current web app grid
    console.log(webAppGrid)
    console.log(grid)

    for (let row = 0; row < grid.length; row++) {
        for (let column = 0; column < grid.length; column++) {
            if (webAppGrid[row][column] == empty) { // Empty table cell, don't do anything
                continue;
            };
            if (webAppGrid[row][column] != grid[row][column]) { // Grid element does not match the 
                                                                // web app grid element. They have 
                                                                // not completed the crossword.
                return false;
            };
        };
    };
    return true; // All checks were true, the user has completed the crossword.
};

function getWebAppGrid() {
    let nonEmptyCells = document.querySelectorAll(".non_empty_cell");
    let webAppGrid = Array(parseInt(dimensions)).fill(Array(parseInt(dimensions)).fill(empty));
    console.log('webAppGrid', webAppGrid)
    console.log('nonEmptyCells', nonEmptyCells)

    nonEmptyCells.forEach((cell) => { // Update webAppGrid with `data-value` properties from the grid's cells
        let row = parseInt(cell.getAttribute("data-row"));
        let column = parseInt(cell.getAttribute("data-column"));
        let value = cell.getAttribute("data-value");

        console.log(row, column, value)
        webAppGrid[row][column] = value;
    });

    return webAppGrid;
};

// TO DO

function onCellClick(cell) {
    let row = cell.getAttribute("data-row");
    let column = cell.getAttribute("data-column");

    determineWhereToSetInputFocusOnCellClick(cell, row, column);
};

function determineWhereToSetInputFocusOnCellClick(cell, row, column) {
    // logic

    // update cellInputFocus to the row, column that was determined
    let inputCellElement = getInputCellElementFromRowAndColumnData(crossOriginIsolated)

    highlightInputFocus(inputCellElement);
};