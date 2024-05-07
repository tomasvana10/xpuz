/* ``interaction.js`` implements various functions allow the crossword grid to 
be interacted with by the user. Additionally, this script offers automatic 
detection of crossword completion, and relays this information to the user. 
*/

/* Variables/constants */

// Jinja2 template variables
let grid, directions, dimensions, empty, colourPalette, intersections, errMsgs;
let direction = "ACROSS",
    currentWord = null,
    cellCoords = null,
    staticIndex = null,
    isDown = null,
    wasEmpty = null,
    compoundInputActive = false;
const arrowKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"];
const spacebarKeys = ["Spacebar", " "];
const backspaceKeys = ["Backspace", "Delete"];
const compoundInputPlaceholders = [
    "ㅇ", "+", "ㅏ", "=", "아", "क​", "+", "इ","=", "कै",
];
let currentPlaceholder = 0;

function dummyCellClick(event) {
    return event.stopImmediatePropagation();
}

function setCompoundInput(priorValue) {
    compoundInputActive = true;
    let currentCell = getCellElement(cellCoords);
    currentCell.onclick = (event) => dummyCellClick(event);
    setValue(currentCell, "");

    let compoundInput = document.createElement("input");
    compoundInput.value = priorValue;
    compoundInput.type = "text";
    compoundInput.classList.add("compound_input");
    currentCell.appendChild(compoundInput);
    compoundInput.focus();
}

function cycleCompoundInputPlaceholderText() {
    let compoundInput = document.getElementsByClassName("compound_input")[0];
    if (compoundInput === undefined) {
        return;
    }
    compoundInput.placeholder = compoundInputPlaceholders[currentPlaceholder];
    if (currentPlaceholder === compoundInputPlaceholders.length - 1) {
        currentPlaceholder = 0;
    } else {
        currentPlaceholder += 1;
    }
}
setInterval(cycleCompoundInputPlaceholderText, 750);

function removeCompoundInput() {
    if (!compoundInputActive) {
        return;
    } // failsafe
    let compoundInput = document.getElementsByClassName("compound_input")[0];
    let cellOfCompoundInput = compoundInput.parentElement;
    let enteredText = compoundInput.value;
    try {
        if (!enteredText[0].match(/\p{L}/u)) {
            enteredText = "";
        }
    } catch (err) {
        enteredText = "";
    }
    compoundInput.remove();
    cellOfCompoundInput.childNodes[0].nodeValue = enteredText[0];
    cellOfCompoundInput.onclick = (event) =>
        onCellClick(event, cellOfCompoundInput);
    cellOfCompoundInput.classList.remove("lock_in", "wrong");
    compoundInputActive = false;
    currentPlaceholder = 0;
}

function handleSetCompoundInput() {
    if (cellCoords === null) {
        return alert(errMsgs[0]);
    }
    if (document.getElementsByClassName("compound_input")[0]) {
        return removeCompoundInput();
    }
    let priorValue = getCellElement(cellCoords).childNodes[0].nodeValue;
    setCompoundInput(priorValue);
}

/* Functions for conditional checks and other minor utilities */

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// Returns true if a cell contains no content
const isEmpty = (cell) => !cell?.childNodes[0]?.nodeValue;

// Change the word, cell and definitions list item focus to either on or off
const setFocusMode = (bool) => {
    if (cellCoords !== null) {
        changeWordFocus(bool);
        changeCellFocus(bool);
        changeDefinitionsListItemFocus(bool);
    }
};

// Modify the value of a cell. Uses nodes to prevent any number label elements
// from being deleted
const setValue = (cell, value) => (cell.childNodes[0].nodeValue = value);

// Get the element of a cell by querying the DOM for an element with a specified
// ``data-row`` and ``data-column`` attribute.
const getCellElement = (coords) =>
    document.querySelector(
        `[data-row="${coords[0]}"][data-column="${coords[1]}"]`
    );

// Get the new coordinates for a cell by extracting its ``data-row`` and
// ``data-column`` attributes into an array
const updateCellCoords = (cell) => [
    parseInt(cell.getAttribute("data-row")),
    parseInt(cell.getAttribute("data-column")),
];

// Return true only if shifting the direction in both deletion and insertion
// modes returns the same coordinates (thus the direction must be alternated)
const shouldDirectionBeAlternated = (coords) =>
    shiftCellCoords(coords, direction, "enter").isEqualTo(coords) &&
    shiftCellCoords(coords, direction, "del").isEqualTo(coords);

// Focus or unfocus a cell
const changeCellFocus = (focus) => {
    getCellElement(cellCoords).style.backgroundColor = focus
        ? colourPalette.CELL_FOCUS
        : colourPalette.SUB;
};

// Get the element for a definitions list item by querying the DOM for its
// data-word attribute
const getDefinitionsListItemFromWord = () =>
    document.querySelector(`[data-word="${currentWord}"]`);

// Focus or unfocus a definitions list item
const changeDefinitionsListItemFocus = (focus) =>
    (getDefinitionsListItemFromWord().style.backgroundColor = focus
        ? colourPalette.WORD_FOCUS
        : "");

const alternateDirection = () =>
    (direction = direction === directions[0] ? directions[1] : directions[0]);

const emulateEscapePress = () =>
    document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape" }));

const isCrosswordComplete = () => getGrid().isEqualTo(grid);

const unfocusActiveElement = () => document.activeElement.blur();

// Ensure the user can always see their currently selected word in the definitions
// list
const updateDefinitionsListPos = () => {
    getDefinitionsListItemFromWord(currentWord).focus();
    getDefinitionsListItemFromWord(currentWord).blur();
};

Array.prototype.isEqualTo = function (arr) {
    return JSON.stringify(this) === JSON.stringify(arr);
};

// Used on cell elements to check if their nodeValue (what the user typed) is
// equal to the data-value attribute (the true value)
Element.prototype.hasCorrectValue = function () {
    return (
        this.childNodes[0].nodeValue.toUpperCase() ===
        this.getAttribute("data-value")
    );
};

document.addEventListener("DOMContentLoaded", () => {
    // On page load
    const body = document.querySelector("body");
    grid = eval(body.getAttribute("data-grid")); // Convert Python array to JS array.
    directions = eval(body.getAttribute("data-directions"));
    dimensions = parseInt(body.getAttribute("data-dimensions"));
    empty = body.getAttribute("data-empty");
    colourPalette = JSON.parse(body.getAttribute("data-colour_palette"));
    intersections = JSON.stringify(
        eval(body.getAttribute("data-intersections"))
    );
    errMsgs = eval(body.getAttribute("data-js_err_msgs"));

    // Detect the user clicking either a non empty cell or a definitions list
    // item by modifying the onclick attribute of all the aforementioned elements
    document.querySelectorAll(".non_empty_cell").forEach(
        (element) =>
            (element.onclick = (event) => {
                onCellClick(event, element);
            })
    );
    document.querySelectorAll(".def").forEach(
        (element) =>
            (element.onclick = (event) => {
                onDefinitionsListItemClick(
                    event,
                    element.getAttribute("data-num"),
                    element.getAttribute("data-direction")
                );
            })
    );
    document.getElementById("compound_button").onclick = () => {
        handleSetCompoundInput();
    };

    // Display the onload popup
    onloadPopupToggled = true; // Modifying this flag earlier prevents the user
    // from messing with the crossword while the
    // CSS transition is happening
    sleep(200).then(() => {
        // Buffer popup transition
        document.getElementById("blur").classList.toggle("active");
        document.getElementById("onload_popup").classList.toggle("active");
        // Wait for the CSS transition to finish, then focus the continue button
        sleep(301).then(() => {
            document
                .getElementsByClassName("continue_button")[0]
                .focus({ focusVisible: true });
        });
    });

    doSpecialButtonAction("grid", "clear", false); // Prevent possible issues
    // with HTML
});

document.addEventListener("keydown", (event) => {
    /* Handle user input; either perform special functions or simply modify the 
    grid based on the input. */

    let inputValue = event.key;

    if (inputValue === "!" && event.shiftKey && cellCoords !== null) {
        event.preventDefault();
        return handleSetCompoundInput();
    }

    if (compoundInputActive) {
        // User is performing compound input
        if (
            inputValue === "Enter" ||
            inputValue === "Escape" ||
            (inputValue === "!" && event.shiftKey)
        ) {
            removeCompoundInput();
        }
        return;
    }

    // This god awful condition ensures the proper handling of the enter keybind
    if (
        inputValue === "Enter" &&
        !completionPopupToggled &&
        !onloadPopupToggled &&
        !event.target.classList.contains("def") &&
        event.target.tagName !== "BUTTON" &&
        !event.target.classList.contains("special_button") &&
        !document.activeElement.classList.contains("def") &&
        !document.activeElement.classList.contains("toggle") &&
        !event.target.classList.contains("dropdown_button")
    ) {
        return handleEnterKeybindPress(event);
    }

    // User wants to clear the current word with Shift + Backspace
    if (backspaceKeys.includes(inputValue) && event.shiftKey) {
        return doSpecialButtonAction("word", "clear", false);
    }

    // User wants to select a definitions list item or a dropdown button
    if (
        inputValue === "Enter" &&
        !completionPopupToggled &&
        !onloadPopupToggled
    ) {
        return handleEnterPress(event);
    }

    if (inputValue === "Escape") {
        return handleEscapePress(event);
    }

    // User hasn't selected a cell, so the upcoming inputs cannot be processed
    if (cellCoords === null) {
        return;
    }

    // Move the user's cell focus since they have pressed an arrow key
    if (arrowKeys.includes(inputValue)) {
        return handleArrowPress(inputValue, event);
    }

    // Alternate the user's direction since they are at an intersection
    if (
        intersections.includes(JSON.stringify(cellCoords)) &&
        spacebarKeys.includes(inputValue)
    ) {
        return handleSpacebarPress(event);
    }

    // User is just typing into the grid normally
    handleStandardInput(inputValue);
});

function handleStandardInput(inputValue) {
    /* Handle a normal keyboard input from the user. */

    let mode = backspaceKeys.includes(inputValue) ? "del" : "enter";
    let currentCell = getCellElement(cellCoords);

    if (mode === "enter") {
        // Ensure the user is typing a language character that is not longer
        // than 1 character
        if (!(inputValue.length === 1 && inputValue.match(/\p{L}/u))) {
            return;
        }
        // Cell is not locked/green in colour, therefore it can be modified
        if (!currentCell.classList.contains("lock_in")) {
            if (isEmpty(currentCell)) {
                wasEmpty = true; // Ensures skipCellCoords functions properly
            }
            setValue(currentCell, inputValue);
        }
        // If the cell is wrong/red in colour, it must be reverted as the user
        // has just typed in it
        currentCell.classList.remove("wrong");
    } else if (mode === "del") {
        // The focused cell has content, just delete it
        if (!isEmpty(currentCell) && !currentCell.classList.contains("lock_in"))
            return setValue(currentCell, "");

        // Perform standard deletion, whereby the content of the cell to the
        // right/top of the current cell is deleted, then the focus is shifted
        // to that cell
        if (
            !getCellElement(
                shiftCellCoords(cellCoords, direction, mode)
            ).classList.contains("lock_in")
        )
            setValue(
                getCellElement(shiftCellCoords(cellCoords, direction, mode)),
                ""
            );
    }
    // Detect possible crossword completion after the grid has been modified
    crosswordCompletionHandler();

    changeCellFocus(false);
    // User has the "smart skip" button toggled, so perform a cell skip
    if (mode === "enter" && document.getElementById("ts").checked) {
        cellCoords = skipCellCoords(cellCoords, direction, mode);

        // Just do a normal cell shift
    } else {
        cellCoords = shiftCellCoords(cellCoords, direction, mode);
    }

    // Refocus the entire word, then set the focus of the cell that has just
    // been shifted/skipped to. No need to update the current word as the current
    // word can never change with a standard keyboard input
    changeWordFocus(true);
    changeCellFocus(true);
}

function skipCellCoords(coords, direction) {
    /* Skip to the next empty cell if the current cell is empty and there is an
    empty cell in front of the current cell somewhere along the current word
    (that is separated by filled cells) */

    let newCellCoords = shiftCellCoords(coords, direction, "enter");
    // The next cell is a void/empty cell, so just return the shifted coordinates.
    if (newCellCoords.isEqualTo(coords)) {
        return newCellCoords;
    }

    // The cell wasn't empty, but asynchronous JavaScript doesn't realise that,
    // so this flags helps to prevent skipping in this case
    if (!wasEmpty) {
        return newCellCoords;
    }
    wasEmpty = false;

    // Continue skipping cells until the current cell has content
    while (!isEmpty(getCellElement(newCellCoords))) {
        let oldCellCoords = newCellCoords;
        newCellCoords = shiftCellCoords(newCellCoords, direction, "enter");
        // As soon as the old cell coords are equal to the new ones, we can
        // no longer skip, so exit the while loop
        if (oldCellCoords.isEqualTo(newCellCoords)) {
            break;
        }
    }

    return newCellCoords;
}

function preventZoomIfRequired(event) {
    /* Prevent the user from zooming if they do not have the "click to zoom"
    button toggled on. This must be handled as the zoom functions from zoomooz.js
    must always be in the HTML structure. */

    if (!document.getElementById("tz").checked)
        // Button isn't checked
        event.stopImmediatePropagation(); // Prevent zoomooz from zooming
}

function handleEnterPress(event) {
    /* Handle a tab-related enter press to either select a new definitions list
    item or invoke and close the dropdown of a dropdown button. */

    if (event.target.classList.contains("def")) {
        event.target.click();
        event.target.blur();
    } else if (event.target.classList.contains("toggle")) {
        event.target.click();
    }
}

function handleEnterKeybindPress(event) {
    /* Allow the user to check the current word with "Enter" or reveal it with 
    "Shift + Enter". */

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
    updateDefinitionsListPos();
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
    /* Determine how the program responds to the user pressing an arrow. First, 
    see if a "enter" or "del" type shift is performed and in what direction. 
    Then, ensure the user is not shifting into a ``.empty`` cell. Finally, 
    alternate the direction if necessary and refocus. */

    event.preventDefault();
    let mode = key === "ArrowDown" || key === "ArrowRight" ? "enter" : "del";
    let dir =
        key === "ArrowDown" || key === "ArrowUp"
            ? directions[1]
            : directions[0];
    let newCellCoords = shiftCellCoords(cellCoords, dir, mode, true);
    let skipFlag = false;

    // Attempt to find an unfilled cell in the direction of the arrow press
    // (if shifting into an empty cell)
    try {
        while (getCellElement(newCellCoords).classList.contains("empty_cell")) {
            newCellCoords = shiftCellCoords(newCellCoords, dir, mode, true);
            skipFlag = true;
        }
    } catch (err) {
        // Couldn't find any unfilled cells
        newCellCoords = cellCoords;
    }

    setFocusMode(false);
    // If moving perpendicular to an intersection, only alternate the direction
    // and retain the prior ``cellCoords``
    if (shouldDirectionBeAlternated(newCellCoords)) {
        alternateDirection();
        // Cells were skipped to reach these new coordinates, so update
        // ``cellCoords``
        if (skipFlag) {
            cellCoords = newCellCoords;
        }
        skipFlag = false;
    } else {
        cellCoords = newCellCoords;
    }
    currentWord = updateCurrentWord();
    setFocusMode(true);
    updateDefinitionsListPos();
}

function crosswordCompletionHandler() {
    if (isCrosswordComplete()) {
        sleep(1).then(() => {
            // Allow the input the user just made to be
            // shown by the DOM
            emulateEscapePress();
            toggleCompletionPopup();
        });
    }
}

function doSpecialButtonAction(magnitude, mode, via_button = true) {
    /* Perform reveal/check/clear operations on a selected cell, word, or, the 
    grid. */

    // Since the user is running the function from a dropdown button, close the
    // dropdown that the button belongs to
    if (via_button) {
        onDropdownClick(mode + "_dropdown");
    }

    // The user must have a word selected to be able to check/reveal the
    // current cell/word
    if (cellCoords === null && magnitude !== "grid") {
        return alert(errMsgs[0]);
    }

    switch (magnitude) {
        case "cell": // Just do a single grid operation on the current cell
            doGridOperation(getCellElement(cellCoords), mode);
            break;
        case "word": // Do a grid operation on each element of the word
            for (const cell of getWordElements()) {
                doGridOperation(cell, mode);
            }
            break;
        case "grid": // Do a grid operation on each non empty cell of the grid
            document
                .querySelectorAll(".non_empty_cell")
                .forEach((cell) => doGridOperation(cell, mode));
    }

    crosswordCompletionHandler();
}

function doGridOperation(cell, mode) {
    /* Perform either a reveal, check or clear action on a cell. */

    if (mode === "reveal") {
        cell.classList.remove("wrong");
        setValue(cell, cell.getAttribute("data-value"));
        cell.classList.add("lock_in"); // This cell must now be correct, so lock
        // it in
    } else if (mode === "check") {
        if (!isEmpty(cell)) {
            if (cell.hasCorrectValue()) {
                // This cell is correct, lock it in
                cell.classList.add("lock_in");
            } else {
                cell.classList.add("wrong");
            }
        }
    } else if (mode === "clear") {
        cell.classList.remove("lock_in");
        cell.classList.remove("wrong");
        setValue(cell, "");
    }
}

function shiftCellCoords(coords, dir, mode, force = false) {
    /* Move the input forward or backward based on the ``mode`` parameter. If no 
    such cell exists at these future coordinates (and the force parameter is 
    false), the original coordinates are returned. 
    
    The aforementioned force parameter allows the cell coordinates to be shifted
    into a cell that may be a void cell. */

    let offset = mode == "enter" ? 1 : -1;
    let newCellCoords =
        dir == directions[1]
            ? [coords[0] + offset, coords[1]]
            : [coords[0], coords[1] + offset];
    let newCell = getCellElement(newCellCoords);

    return (newCell !== null && newCell.classList.contains("non_empty_cell")) ||
        force
        ? // The following comments only apply if ``force`` is false
          newCellCoords // Cell at future coords is a non empty cell
        : coords; // Cell at future coords is empty/black, cannot move to it
}

function onDefinitionsListItemClick(event, numLabel, dir) {
    /* Set user input to the start of a word when they click its definition/clue. */

    preventZoomIfRequired(event);
    setFocusMode(false);

    document.activeElement.blur();
    direction = dir;
    // Retrieve cell from parent element of number label list item
    cellCoords = updateCellCoords(
        document.querySelector(`[data-num_label="${numLabel}"]`).parentElement
    );
    currentWord = updateCurrentWord();
    setFocusMode(true);
}

function onCellClick(event, cell) {
    /* Handles how the grid responds to a user clicking on the cell. Ensures 
    the appropriate display of the current cell and word focus on cell click, 
    as well as alternating input directions if clicking at an intersecting point 
    between two words. */
    // User is performing compound input
    if (compoundInputActive && cell !== getCellElement(cellCoords)) {
        removeCompoundInput();
    }

    preventZoomIfRequired(event);
    setFocusMode(false);

    let newCellCoords = updateCellCoords(cell);
    // User is clicking on an intersection for the second time, so alternate
    // the direction
    if (
        intersections.includes(JSON.stringify(newCellCoords)) &&
        newCellCoords.isEqualTo(cellCoords)
    )
        alternateDirection();
    // Cannot shift the cell in the original direction, so it must be alternated
    else if (shouldDirectionBeAlternated(newCellCoords)) alternateDirection();

    cellCoords = newCellCoords;
    currentWord = updateCurrentWord();
    setFocusMode(true);
    updateDefinitionsListPos();
}

function changeWordFocus(focus) {
    /* Retrieve the starting and ending coordinates of a word and change the 
    colour of the cell elements that make up that word to a different colour. */

    for (const element of getWordElements()) {
        element.style.backgroundColor = focus
            ? colourPalette.WORD_FOCUS
            : colourPalette.SUB;
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
    /* Generator function that yields all the consisting cell elements of the 
    current word. */

    let [startCoords, endCoords] = getWordIndices();
    for (let i = startCoords; i <= endCoords; i++) {
        let coords = isDown ? [i, staticIndex] : [staticIndex, i];
        yield getCellElement(coords);
    }
}

function getWordIndices() {
    /* Iterate either across or down through the grid to find the starting and 
    ending indices of a word. */

    let [row, col] = cellCoords;
    isDown = direction === directions[1];
    staticIndex = isDown ? col : row; // The index that never changes (the row
    // if direction is across, etc)
    let [startCoords, endCoords] = isDown ? [row, row] : [col, col];

    // Find starting coords of the word
    while (
        startCoords > 0 &&
        grid[isDown ? startCoords - 1 : row][isDown ? col : startCoords - 1] !=
            empty
    )
        startCoords--;

    // Find ending coords of the word
    while (
        endCoords < dimensions - 1 &&
        grid[isDown ? endCoords + 1 : row][isDown ? col : endCoords + 1] !=
            empty
    )
        endCoords++;

    return [startCoords, endCoords];
}

function getGrid() {
    /* Create an empty replica of the crossword grid, then update it according 
    to the web app grid */

    let webAppGrid = Array.from({ length: dimensions }, () =>
        Array(dimensions).fill(empty)
    );

    document.querySelectorAll(".non_empty_cell").forEach((cell) => {
        let row = parseInt(cell.getAttribute("data-row"));
        let column = parseInt(cell.getAttribute("data-column"));
        let value = cell.childNodes[0].nodeValue.toUpperCase();
        webAppGrid[row][column] = value;
    });

    return webAppGrid;
}
