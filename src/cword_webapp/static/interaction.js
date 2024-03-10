/* `interaction.js` implements various functions allow the crossword grid to be interacted with by the user. 
Additionally, this script offers automatic detection of crossword completion, and relays this information to the user. 
*/

let grid, directions, dimensions, empty, colourPalette, intersections, errMsgs; // Jinja2 template variables
let direction = "ACROSS", 
    currentWord = null,
    cellCoords = null,
    staticIndex = null,
    isDown = null,
    wasEmpty = null;
const arrowKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"];
const spacebarKeys = ["Spacebar", " "];
const backspaceKeys = ["Backspace", "Delete"];

/* Functions for conditional checks and other minor utilities */
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
const isEmpty = (cell) => !cell?.childNodes[0]?.nodeValue;
const setFocusMode = (bool) => { if (cellCoords !== null) { changeWordFocus(bool); changeCellFocus(bool); changeDefinitionsListItemFocus(bool); } };
const setValue = (cell, value) => cell.childNodes[0].nodeValue = value; // Using nodes prevents any `num_label` elements from being deleted
const getCellElement = (coords) => document.querySelector(`[data-row="${coords[0]}"][data-column="${coords[1]}"]`);
const updateCellCoords = (cell) => [parseInt(cell.getAttribute("data-row")), parseInt(cell.getAttribute("data-column"))]; 
const shouldDirectionBeAlternated = (coords) => shiftCellCoords(coords, direction, "enter").isEqualTo(coords) && shiftCellCoords(coords, direction, "del").isEqualTo(coords); 
const changeCellFocus = (focus) => { getCellElement(cellCoords).style.backgroundColor = focus ? colourPalette.CELL_FOCUS : colourPalette.SUB; };
const getDefinitionsListItemFromWord = () => document.querySelector(`[data-word="${currentWord}"]`);
const changeDefinitionsListItemFocus = (focus) => getDefinitionsListItemFromWord().style.backgroundColor = focus ? colourPalette.WORD_FOCUS : ""; 
const alternateDirection = () => direction = direction === directions[0] ? directions[1] : directions[0];
const emulateEscapePress = () => document.dispatchEvent(new KeyboardEvent("keydown", {"key": "Escape"}));
const isCrosswordComplete = () => getGrid().isEqualTo(grid);
const unfocusActiveElement = () => document.activeElement.blur();

Array.prototype.isEqualTo = function(arr) { return JSON.stringify(this) === JSON.stringify(arr); };

// Used on cell elements to check if their nodeValue (what the user typed) is equal to the data-value attribute (the true value)
Element.prototype.hasCorrectValue = function() { 
    return this.childNodes[0].nodeValue.toUpperCase() === this.getAttribute("data-value"); 
};


document.addEventListener("DOMContentLoaded", () => { // On page load
    const body = document.querySelector("body");
    grid = eval(body.getAttribute("data-grid")); /* Convert Python array to JS array */
    directions = eval(body.getAttribute("data-directions"));
    dimensions = parseInt(body.getAttribute("data-dimensions"));
    empty = body.getAttribute("data-empty");
    colourPalette = JSON.parse(body.getAttribute("data-colour_palette"));
    intersections = JSON.stringify(eval(body.getAttribute("data-intersections")));
    errMsgs = eval(body.getAttribute("data-js_err_msgs"));

    document.querySelectorAll(".non_empty_cell").forEach(element => element.addEventListener("click", event => {
        onCellClick(event, element);
    }));
    document.querySelectorAll(".def").forEach(element => element.addEventListener("click", event => {
        onDefinitionsListItemClick(event, element.getAttribute("data-num"), element.getAttribute("data-direction"));
    }));

    onloadPopupToggled = true;
    sleep(200).then(() => { // Buffer popup transition
        document.getElementById("blur").classList.toggle("active");
        document.getElementById("onload_popup").classList.toggle("active");
        // Must wait for the transition to finish before focusing the continue button
        sleep(301).then(() => { document.getElementsByClassName("continue_button")[0].focus({ focusVisible: true}); });
    });

    doSpecialButtonAction("grid", "clear", false); // Prevent possible issues with HTML    
});


document.addEventListener("keydown", event => {
    /* Handle user input; either perform special functions or simply modify the grid based on the input. */
    let inputValue = event.key;

    if (inputValue === "Enter" && !completionPopupToggled && !onloadPopupToggled 
        && (!event.target.classList.contains("def") && event.target.tagName !== "BUTTON") 
        && !event.target.classList.contains("special_button") && !document.activeElement.classList.contains("def")
        && !document.activeElement.classList.contains("toggle")
        && !event.target.classList.contains("dropdown_button")) { 
            return handleEnterKeybindPress(event); 
    }
    if (backspaceKeys.includes(inputValue) && event.shiftKey) { return doSpecialButtonAction("word", "clear", false); }

    if (inputValue === "Enter" && !completionPopupToggled && !onloadPopupToggled) { return handleEnterPress(event); }
    if (inputValue === "Escape") { return handleEscapePress(event); }

    if (cellCoords === null) { return; } // User hasn't selected a cell, so the following inputs cannot be processed
    if (arrowKeys.includes(inputValue)) { return handleArrowPress(inputValue, event); }
    if (intersections.includes(JSON.stringify(cellCoords)) && spacebarKeys.includes(inputValue)) { return handleSpacebarPress(event); }

    handleStandardInput(inputValue);
});

function handleStandardInput(inputValue) {
    let mode = (backspaceKeys.includes(inputValue)) ? "del" : "enter";
    let currentCell = getCellElement(cellCoords);

    if (mode === "enter") {
        if (!(inputValue.length === 1 && (inputValue.match(/\p{L}/u)))) { return; } // Regex matches `letter` characters
        if (!currentCell.classList.contains("lock_in")) { 
            if (isEmpty(currentCell)) { wasEmpty = true; }
            setValue(currentCell, inputValue); 
        }
        currentCell.classList.remove("wrong"); 
    } else if (mode === "del") {
        if (!isEmpty(currentCell) && !currentCell.classList.contains("lock_in"))
                return setValue(currentCell, "");  // Focused cell has content, just delete it
        if (!getCellElement(shiftCellCoords(cellCoords, direction, mode)).classList.contains("lock_in")) 
            setValue(getCellElement(shiftCellCoords(cellCoords, direction, mode)), ""); // Perform standard deletion
    }
    crosswordCompletionHandler();
    
    changeCellFocus(false);
    if (mode === "enter" && document.getElementById("ts").checked) { 
        cellCoords = skipCellCoords(cellCoords, direction, mode);
    } else { cellCoords = shiftCellCoords(cellCoords, direction, mode); }
    changeWordFocus(true); changeCellFocus(true);
}

function skipCellCoords(coords, direction) {
    let newCellCoords = shiftCellCoords(coords, direction, "enter");
    if (newCellCoords.isEqualTo(coords)) { return newCellCoords; }
    if (!wasEmpty) { return newCellCoords; }
    wasEmpty = false;

    while (!isEmpty(getCellElement(newCellCoords))) {
        let oldCellCoords = newCellCoords
        newCellCoords = shiftCellCoords(newCellCoords, direction, "enter");
        if (oldCellCoords.isEqualTo(newCellCoords)) { break; }
    }

    return newCellCoords
}

function preventZoomIfRequired(event) {
    if (!document.getElementById("tz").checked) // User doesn't have click to zoom enabled
        event.stopImmediatePropagation(); // Prevent zoomooz from zooming
}

function handleEnterPress(event) {
    if (event.target.classList.contains("def")) { 
        event.target.click();
        event.target.blur(); 
    } else if (event.target.classList.contains("toggle")) {
        event.target.click();
    }
}

function handleEnterKeybindPress(event) {
    /* Allow the user to check the current word with "Enter" or reveal it with "Shift + Enter". */
    unfocusActiveElement();
    hideDropdowns();
    let mode = event.shiftKey ? "reveal" : "check";
    doSpecialButtonAction("word", mode, false);
}

function handleSpacebarPress(event) {
    /* Alternate direction when pressing the spacebar at an intersection. */    
    event.preventDefault();
    setFocusMode(false);
    alternateDirection();
    currentWord = updateCurrentWord();
    setFocusMode(true);
}

function handleEscapePress(event) { 
    /* Remove focus from everything. */
    event.preventDefault();
    unfocusActiveElement();
    hideDropdowns(); 
    setFocusMode(false);
    cellCoords = null; 
    currentWord = null;
}

function handleArrowPress(key, event) {
    /* Determine how the program responds to the user pressing an arrow. First, see if a "enter" or
    "del" type shift is performed and in what direction. Then, ensure the user is not shifting into a
    `.empty` cell. Finally, alternate the direction if necessary and refocus. */
    event.preventDefault();
    let mode = (key === "ArrowDown" || key === "ArrowRight") ? "enter" : "del";
    let dir = (key === "ArrowDown" || key === "ArrowUp") ? directions[1] : directions[0];
    let newCellCoords = shiftCellCoords(cellCoords, dir, mode, true);
    let skipFlag = false;

    // Attempt to find an unfilled cell in the direction of the arrow press (if shifting into an empty cell)
    try {
        while (getCellElement(newCellCoords).classList.contains("empty_cell")) {
            newCellCoords = shiftCellCoords(newCellCoords, dir, mode, true);
            skipFlag = true;
        }
    } catch(err) { newCellCoords = cellCoords; } // Couldn't find any unfilled cells

    setFocusMode(false);
    // If moving perpendicular to an intersection, only alternate the direction and retain the prior `cellCoords`
    if (shouldDirectionBeAlternated(newCellCoords)) {
        alternateDirection();
        // Cells were skipped to reach these new coordinates, so update `cellCoords`
        if (skipFlag) { cellCoords = newCellCoords; }
        skipFlag = false;
    } else { cellCoords = newCellCoords; }
    currentWord = updateCurrentWord();
    setFocusMode(true);
}

function crosswordCompletionHandler() {
    if (isCrosswordComplete()) { 
        sleep(1).then(() => { 
            emulateEscapePress(); 
            toggleCompletionPopup(); 
        });
    }
}

function doSpecialButtonAction(magnitude, mode, via_button=true) {
    /* Perform reveal/check/clear operations on a selected cell, word, or, the grid. */
    if (via_button) { onDropdownClick(mode + "_dropdown"); }
    if (cellCoords === null && magnitude !== "grid") { return alert(errMsgs[0]); }

    switch (magnitude) {
        case "cell":
            doGridOperation(getCellElement(cellCoords), mode); break;
        case "word":
            for (const cell of getWordElements()) { doGridOperation(cell, mode); } break;
        case "grid":
            document.querySelectorAll(".non_empty_cell").forEach(cell => doGridOperation(cell, mode));
    }

    crosswordCompletionHandler();
}

function doGridOperation(cell, mode) {
    if (mode === "reveal") {
        cell.classList.remove("wrong");
        setValue(cell, cell.getAttribute("data-value"));
        cell.classList.add("lock_in"); // LOCK IN!!!
    } else if (mode === "check") {
        if (!isEmpty(cell)) {
            if (cell.hasCorrectValue()) {
                cell.classList.add("lock_in");
            } else { cell.classList.add("wrong"); }
        }
    } else if (mode === "clear") {
        cell.classList.remove("lock_in");
        cell.classList.remove("wrong");
        setValue(cell, "");
    }
}

function shiftCellCoords(coords, dir, mode, force=false) {
    /* Move the input forward or backward based on the `mode` parameter. If no such cell exists at
    these future coordinates (and the force param is false), the original coordinates are returned. */
    let offset = (mode == "enter") ? 1 : -1;
    let newCellCoords = (dir == directions[1]) ? [coords[0] + offset, coords[1]] : [coords[0], coords[1] + offset];
    let newCell = getCellElement(newCellCoords);

    return newCell !== null && newCell.classList.contains("non_empty_cell") || force
           // The following comments only apply if `force` is false
           ? newCellCoords // Cell at future coords is a non empty cell
           : coords; // Cell at future coords is empty/black, cannot move to it
}

function onDefinitionsListItemClick(event, numLabel, dir) {
    /* Set user input to the start of a word when they click its definition/clue. */
    preventZoomIfRequired(event);
    setFocusMode(false);

    document.activeElement.blur();
    direction = dir;
    // Retrieve cell from parent element of number label list item
    cellCoords = updateCellCoords(document.querySelector(`[data-num_label="${numLabel}"]`).parentElement);
    currentWord = updateCurrentWord();
    setFocusMode(true);
}

function onCellClick(event, cell) {
    /* Handles how the grid responds to a user clicking on the cell. Ensures the appropriate display
    of the current cell and word focus on cell click, as well as alternating input directions if
    clicking at an intersecting point between two words. */
    preventZoomIfRequired(event);
    setFocusMode(false); 

    let newCellCoords = updateCellCoords(cell);
    // User is clicking on an intersection for the second time, so alternate the direction
    if (intersections.includes(JSON.stringify(newCellCoords)) && newCellCoords.isEqualTo(cellCoords)) 
        alternateDirection();

    // Cannot shift the cell in the original direction, so it must be alternated
    else if (shouldDirectionBeAlternated(newCellCoords))
        alternateDirection();
        
    cellCoords = newCellCoords;
    currentWord = updateCurrentWord();
    setFocusMode(true);
}

function changeWordFocus(focus) {
    /* Retrieve the starting and ending coordinates of a word and change the colour of the cell elements
    that make up that word to a different colour. */
    for (const element of getWordElements()) {
        element.style.backgroundColor = focus ? colourPalette.WORD_FOCUS : colourPalette.SUB;
    }
}

function updateCurrentWord() {
    /* Return the current word in uppercase. */
    let word = "";
    for (const element of getWordElements()) {
        word += element.getAttribute("data-value");
    }

    return word.toUpperCase();
}

function* getWordElements() {
    /* Generator function that yields all the consisting cell elements of the current word. */
    let [startCoords, endCoords] = getWordIndices();
    for (let i = startCoords; i <= endCoords; i++) { 
        let coords = isDown ? [i, staticIndex] : [staticIndex, i];
        yield getCellElement(coords);
    }
}

function getWordIndices() {
    /* Iterate either across or down through the grid to find the starting and ending indices of a word. */
    let [row, col] = cellCoords;
    isDown = direction === directions[1];
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

function getGrid() {
    /* Create an empty replica of the crossword grid, then update it according to the web app grid */
    let webAppGrid = Array.from({ length: dimensions }, () => Array(dimensions).fill(empty));

    document.querySelectorAll(".non_empty_cell").forEach((cell) => {
        let row = parseInt(cell.getAttribute("data-row"));
        let column = parseInt(cell.getAttribute("data-column"));
        let value = cell.childNodes[0].nodeValue.toUpperCase();
        webAppGrid[row][column] = value;
    });

    return webAppGrid;
}