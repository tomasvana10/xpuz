let grid, dimensions;

document.addEventListener("DOMContentLoaded", function() {
    const body = document.querySelector("body");
    grid = body.getAttribute("data-grid");
    dimensions = body.getAttribute("data-dimensions");
});

function checkIfCrosswordIsComplete() {
    // Compare all table cells with the grid, and if they are identical, tell the user they have 
    // completed the crossword.
}

function onCellClick () {
    // Called by a class "non-empty" <td> element

    // Behaviour: 

    // Clicking on a cell that has no intersecting words >> Set input to start of word, 
    // or leftmost/topmost empty cell 

    // Clicking on a cell that has an intersecting word >> First click replicates the above behaviour,
    // second click sets the focus to the other intersecting word with the same behaviour as above. This
    // is an alternating feature.
}

function onKeyPress () {
    // If no cell is currently selected, return

    // If cell is selected, enter the typed character, then move the input either across or down.

    // If there is no next cell, keep the input in the same cell
}