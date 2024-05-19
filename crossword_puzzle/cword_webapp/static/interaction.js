const arrowKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"];
const spacebarKeys = ["Spacebar", " "];
const backspaceKeys = ["Backspace", "Delete"];
const compoundInputPlaceholders = [
  "ㅇ", "+", "ㅏ", "=", "아", "क​", "+", "इ", "=", "कै",
];
const onlyLangRegex = /\p{L}/u; // Ensure user only types language characters

class Interaction {
  /* Class to handle all forms of interaction with the web app, as well as to
  implement ergonomic features to improve the user experience.
  
  Also contains utility functions to perform cell-related calculations.
	*/

  constructor() {
    this.direction = "ACROSS"; // The default direction to choose, if possible
    this.currentWord = null; // e.x. "HELLO"
    this.cellCoords = null; // e.x. [0, 5] (row, column)
    this.wasEmpty = null;

    // Variables modified by every call of ``getWordIndices``
    this.staticIndex = null; // e.x. 5 (if ``direction`` is "ACROSS")
    this.isDown = null;

    // Misc variables
    this.compoundInputActive = null;
    this.completionPopupToggled = false;
    this.onloadPopupToggled = false;
    this.currentDropdown = null;
    this.currentPlaceholder = 0;
    this.doNotHandleStandardCellClick = false;
    this.preventInitialLIZoom = true;
    this.setCoordsToEndOfWord = false;

    // When the DOM is ready, trigger the ``onLoad`` method
    document.addEventListener("DOMContentLoaded", this.onLoad.bind(this));
  }

  onLoad() {
    /* Get crossword-related data from HTML body, provided by Flask. */
    this.body = document.querySelector("body");
    this.grid = eval(this.body.getAttribute("data-grid"));
    this.directions = eval(this.body.getAttribute("data-directions"));
    this.dimensions = parseInt(this.body.getAttribute("data-dimensions"));
    this.empty = this.body.getAttribute("data-empty");
    this.colourPalette = JSON.parse(
      this.body.getAttribute("data-colour_palette")
    );
    this.intersections = JSON.stringify(
      eval(this.body.getAttribute("data-intersections"))
    );
    this.errMsgs = eval(this.body.getAttribute("data-js_err_msgs"));
    this.wordCount = this.body.getAttribute("data-word_count");

    this.skipToggle = document.getElementById("ts");
    this.zoomToggle = document.getElementById("tz");
    this.wordToggle = document.getElementById("tw");
    this.checkToggle = document.getElementById("tc");

    // These elements, when clicked on (with ``.click()``) will force ``zoomooz``
    // to unzoom the most recently zoomed-on element
    this.returnDefZoomElement = document.getElementById("return_def_zoom");
    this.returnGridZoomElement =
      document.getElementsByClassName("empty_cell")[0];

    // Check README.md for this audios CC attribution
    this.jazz = document.getElementById("jazz");
    this.jazz.volume = 0.125;

    // Easter egg typing sounds - licensed under Mixkit Sound Effects Free License
    this.clicks = [...document.getElementsByClassName("click")];
    this.clicks.forEach(click => click.volume = 0.175);
    this.playClicks = false;

    this.setListeners();
    Interaction.configureScrollHeights();
    this.displayOnloadPopup();
    // Clear the grid to prevent possible issues with HTML
    this.doSpecialButtonAction("grid", "clear", false);
    // Cycle placeholder text if a compound input element is available
    setInterval(this.cycleCompoundInputPlaceholderText.bind(this), 750);
  }

  setListeners() {
    /* Add listeners and onclick functions. */

    document.querySelectorAll(".non_empty_cell").forEach(element => {
      element.onclick = event => this.onCellClick(event, element);
      element.classList.add("zoomTarget"); // Prevents the user from having
                                           // to click twice to zoom initially
    });

    document.querySelectorAll(".empty_cell").forEach(element => {
      element.onclick = () => this.removeCompoundInput(false);
    });

    // Detect the user clicking on a word's definition
    document.querySelectorAll(".def").forEach(
      element =>
        (element.onclick = event => {
          this.onDefinitionsListItemClick(
            event,
            element.getAttribute("data-num"),
            element.getAttribute("data-direction")
          );
        })
    );

    // Remove zoom when disabling the zoom checkbox
    this.zoomToggle.addEventListener("change", event => {
      if (!event.target.checked) {
        this.zoomOut();
      }
    });

    document.getElementById("compound_button").onclick = event => {
      event.stopPropagation();
      this.handleSetCompoundInput(false);
    };

    document.addEventListener("keydown", event =>
      this.handleSpecialInput(event)
    );

    document.addEventListener("click", event => this.handleClick(event));

    document.addEventListener("focusout", event =>
      this.handleDropdownFocusOut(event)
    );
  }

  playClick() {
    if (this.playClicks) {
      try {
        return this.clicks[Math.floor(Math.random() * this.clicks.length)].play();
      } catch (err) { } // This error detection prevents an error that I observed
                        // only once, and I forgot what it was, so this handling
                        // will be left empty.
    }
  }

  zoomOut() {
    if (document.querySelector(".non_empty_cell.selectedZoomTarget")) {
      this.returnGridZoomElement.click();
    } else if (document.querySelector(".def.selectedZoomTarget")) {
      this.returnDefZoomElement.click();
    }
  }

  handleSpecialInput(event) {
    /* Check if the user wants to do a special action, for example, performing
    a keybind. If this is the case, this function will process it and prevent
    ``this.handleStandardInput`` from running. 
    */
    if (this.onloadPopupToggled || this.completionPopupToggled) {
      return;
    }

    let inputValue = event.key;
    this.playClick()

    // Handle the setting of a compound input element when pressing [Shift + 1]
    if (inputValue === "!" && event.shiftKey) {
      event.preventDefault();
      return this.handleSetCompoundInput();
    }

    // Remove the compound input
    if (this.compoundInputActive) {
      if (
        // The user has finished their compound input and has pressed either
        // [Shift + 1], "Enter" or "Escape"
        inputValue === "Enter" ||
        inputValue === "Escape" ||
        (inputValue === "!" && event.shiftKey)
      ) {
        this.removeCompoundInput();
      }
      return;
    }

    // Ensure proper handling of the enter keybind
    if (
      inputValue === "Enter" &&
      !event.target.classList.contains("def") &&
      event.target.tagName !== "BUTTON" &&
      !event.target.classList.contains("special_button") &&
      !document.activeElement.classList.contains("def") &&
      !document.activeElement.classList.contains("toggle") &&
      !event.target.classList.contains("dropdown_button")
    ) {
      return this.handleEnterKeybindPress(event);
    }

    // User wants to clear the current word with [Shift + Backspace]
    if (backspaceKeys.includes(inputValue) && event.shiftKey) {
      return this.doSpecialButtonAction("word", "clear", false);
    }

    // User wants to select a definitions list item or a dropdown button
    if (
      inputValue === "Enter" &&
      !this.completionPopupToggled &&
      !this.onloadPopupToggled
    ) {
      return this.handleEnterPress(event);
    }

    if (inputValue === "Escape") {
      return this.handleEscapePress(event);
    }

    // User hasn't selected a cell, so the upcoming inputs cannot be processed
    if (this.cellCoords === null) {
      return;
    }

    if (
      [...arrowKeys.slice(2, 4)].includes(inputValue) &&
      event.shiftKey
    ) {
      return this.shiftWordSelection(event, inputValue);
    }

    // Move the user's cell focus since they have pressed an arrow key
    if (arrowKeys.includes(inputValue)) {
      return this.handleArrowPress(inputValue, event);
    }

    // Alternate the user's direction since they are at an intersection
    if (
      this.intersections.includes(JSON.stringify(this.cellCoords)) &&
      spacebarKeys.includes(inputValue) // Pressing "Spacebar"
    ) {
      return this.handleSpacebarPress(event);
    }

    // User is just typing into the grid normally
    this.handleStandardInput(inputValue);
  }

  handleStandardInput(inputValue) {
    /* Handle a normal keyboard input from the user. */

    let mode = backspaceKeys.includes(inputValue) ? "del" : "enter";
    let currentCell = Interaction.getCellElement(this.cellCoords);

    if (mode === "enter") {
      // Ensure the user is typing a language character that is not longer
      // than 1 character
      if (
        !(
          inputValue.length === 1 && inputValue.match(onlyLangRegex)
        )
      ) {
        return;
      }

      // Check if cell is not locked. If so, it can be modified.
      if (!currentCell.classList.contains("lock_in")) {
        if (Interaction.isEmpty(currentCell)) {
          this.wasEmpty = true; // Ensures skipCellCoords functions properly
        }
        Interaction.setValue(currentCell, inputValue);
        if (this.checkToggle.checked) {
          currentCell.classList.remove("wrong");
          this.doGridOperation(currentCell, "check");
        }
      }
      // If the cell is wrong/red in colour, it must be reverted as the user
      // has just typed in it
      if (!this.checkToggle.checked) {
        currentCell.classList.remove("wrong");
      }
    } else if (mode === "del") {
      // The focused cell has content, just delete it and do nothing
      if (
        !Interaction.isEmpty(currentCell) &&
        !currentCell.classList.contains("lock_in")
      ) {
        currentCell.classList.remove("wrong");
        return Interaction.setValue(currentCell, "");
      }

      // Perform standard deletion, whereby the content of the cell to the
      // right/top of the current cell is deleted, then the focus is shifted
      // to that cell (``priorCell``)
      let priorCell = Interaction.getCellElement(
        this.shiftCellCoords(this.cellCoords, this.direction, mode)
      );
      if (!priorCell.classList.contains("lock_in")) {
        Interaction.setValue(priorCell, "");
        priorCell.classList.remove("wrong");
      }
    }

    // Detect possible crossword completion after the grid has been modified
    this.crosswordCompletionHandler();
    this.handleCellShift(mode, currentCell);
  }

  handleCellShift(mode, currentCell) {
    /* Determines how the focus of a cell within a word is shifted. */

    this.changeCellFocus(false);
    let oldCellCoords = this.cellCoords;
    // User has the "smart skip" button toggled, so perform a cell skip
    if (mode === "enter" && this.skipToggle.checked) {
      this.cellCoords = this.skipCellCoords(
        this.cellCoords,
        this.direction,
        mode
      );
    } else {
      // Just do a normal cell shift
      this.cellCoords = this.shiftCellCoords(
        this.cellCoords,
        this.direction,
        mode
      );
    }

    this.autoShiftWordIfPossible(mode, oldCellCoords);
    this.followCellZoom(currentCell);

    // Refocus the entire word, then set the focus of the cell that has just
    // been shifted/skipped to. No need to update the current word as the current
    // word can never change with a standard keyboard input.
    this.changeWordFocus(true);
    this.changeCellFocus(true);
  }

  autoShiftWordIfPossible(mode, oldCellCoords) {
    /* Automatically shift to the next word if the user is performing a deletion/
    insertion action that will not move them anywhere, for example:

    [ A ] [ B ] [ ...C ] - After the C has been typed, ``shiftWordSelection`` 
    will automatically shift forwards to the next word. If the user shifts onto
    an already filled cell, they must type in it once more in order to shift to
    the next word.

    [ A ] [ ] [ ] - After the A has been deleted, the user must press enter once
    more in order to shift backwards to the previous word.
    */
    if (this.wordToggle.checked) {
      let arrow =
        mode === "del" ? arrowKeys[2] : arrowKeys[3];
      if (
        oldCellCoords.isEqualTo(this.cellCoords) &&
        (!Interaction.isEmpty(Interaction.getCellElement(this.cellCoords)) ||
          mode === "del")
      ) {
        this.shiftWordSelection(null, arrow);
      }
    }
  }

  shiftWordSelection(event = null, arrow) {
    /* Cycle to the next word based on the sequence in which the words are placed
    on the grid. 
    */
    event?.preventDefault(); // This method is not always called by a listener,
                             // so optional chaining is used
    let offset = arrow === arrowKeys[2] ? -1 : 1;
    let def = this.getDefinitionsListItemFromWord();
    let newWordNum = Number(def.getAttribute("data-num")) + offset;
    let newDef = document.querySelector(`[data-num="${newWordNum}"`);
    if (!newDef) {
      // User is at the first or last word, so go to either the last
      // word (if deleting) or the first word (if inserting)
      let num = offset === 1 ? "1" : this.wordCount;
      newDef = document.querySelector(`[data-num="${num}"]`);
    }
    let oldCellCoords = this.cellCoords;
    if (offset === -1) {
      this.setCoordsToEndOfWord = true;
    }
    newDef.focus();
    newDef.click();
    newDef.blur();
    this.followCellZoom(oldCellCoords);
  }

  skipCellCoords(coords, direction) {
    /* Skip to the next empty cell if the current cell is empty and there is an
    empty cell in front of the current cell somewhere along the current word
    (that is separated by filled cells).
    */

    let newCellCoords = this.shiftCellCoords(coords, direction, "enter");
    // The next cell is a void/empty cell, so just return the shifted coordinates.
    if (newCellCoords.isEqualTo(coords)) {
      return newCellCoords;
    }

    // The cell wasn't empty, but asynchronous JavaScript doesn't realise that,
    // so this flags helps to prevent skipping in this case
    if (!this.wasEmpty) {
      return newCellCoords;
    }
    this.wasEmpty = false;

    // Continue skipping cells until the current cell has content
    while (!Interaction.isEmpty(Interaction.getCellElement(newCellCoords))) {
      let oldCellCoords = newCellCoords;
      newCellCoords = this.shiftCellCoords(newCellCoords, direction, "enter");
      // As soon as the old cell coords are equal to the new ones, we can
      // no longer skip, so exit the while loop (or else everything will die)
      if (oldCellCoords.isEqualTo(newCellCoords)) {
        break;
      }
    }

    // Account for a case like this:  [ <Focus> ] [ H ] [ I ]
    // Whereby we prevent [ I ] (the end of the word) from being focused to
    // when skipping (instead we just shift the cell coords once).
    if (!Interaction.isEmpty(Interaction.getCellElement(newCellCoords))) {
      return this.shiftCellCoords(coords, direction, "enter");
    } else {
      return newCellCoords;
    }
  }

  shiftCellCoords(coords, dir, mode, force = false) {
    /* Move the input forward or backward based on the ``mode`` parameter. If no 
    such cell exists at these future coordinates (and the force parameter is 
    false), the original coordinates are returned. 
      
    The aforementioned force parameter allows the cell coordinates to be shifted
    into a cell that may be a void cell. 
    */

    let offset = mode == "enter" ? 1 : -1;
    let newCellCoords =
      dir === this.directions[1]
        ? [coords[0] + offset, coords[1]]
        : [coords[0], coords[1] + offset];
    let newCell = Interaction.getCellElement(newCellCoords);

    return (newCell !== null && newCell.classList.contains("non_empty_cell")) ||
      force
      ? // The following comments only apply if ``force`` is false
        newCellCoords // Cell at future coords is a non empty cell
      : coords; // Cell at future coords is empty/black, cannot move to it
  }

  onDefinitionsListItemClick(event, numLabel, dir) {
    /* Set user input to the start of a word when they click its definition/clue. */

    // Retrieve cell from parent element of number label list item
    let currentCell = document.querySelector(
      `[data-num_label="${numLabel}"]`
    ).parentElement;

    this.preventZoomIfRequired(event);
    this.removeCompoundInputIfRequired(currentCell);

    this.setFocusMode(false);
    document.activeElement.blur();
    // User has compound input set at, say, 26 down, and they have just clicked
    // on the definition for 26 down, so refocus their compound input
    if (this.compoundInputActive) {
      document.getElementsByClassName("compound_input")[0].focus();
    }
    this.direction = dir;
    this.cellCoords = Interaction.updateCellCoords(currentCell);
    if (this.setCoordsToEndOfWord) { // When user is deleting with auto-word on.
      this.cellCoords = Interaction.updateCellCoords(
        [...this.getWordElements()].slice(-1)[0]
      )
      this.setCoordsToEndOfWord = false;
    }
    this.currentWord = this.updateCurrentWord();
    this.setFocusMode(true);
  }

  onCellClick(event, cell) {
    /* Handles how the grid responds to a user clicking on the cell. Ensures 
    the appropriate display of the current cell and word focus on cell click, 
    as well as alternating input directions if clicking at an intersecting point 
    between two words. 
    */
    if (this.doNotHandleStandardCellClick) {
      return (this.doNotHandleStandardCellClick = false);
    }

    this.preventZoomIfRequired(event);
    this.removeCompoundInputIfRequired(cell);

    this.setFocusMode(false);
    let newCellCoords = Interaction.updateCellCoords(cell);
    // User is clicking on an intersection for the second time, so alternate
    // the direction
    if (
      this.intersections.includes(JSON.stringify(newCellCoords)) &&
      newCellCoords.isEqualTo(this.cellCoords)
    )
      this.alternateDirection();
    // Cannot shift the cell in the original direction, so it must be alternated
    else if (this.shouldDirectionBeAlternated(newCellCoords))
      this.alternateDirection();

    this.cellCoords = newCellCoords;
    this.currentWord = this.updateCurrentWord();
    this.setFocusMode(true);
    this.updateDefinitionsListPos();
  }

  handleArrowPress(key, event) {
    /* Determine how the program responds to the user pressing an arrow. First, 
    see if a "enter" or "del" type shift is performed and in what direction. 
    Then, ensure the user is not shifting into a ``.empty`` cell. Finally, 
    alternate the direction if necessary and refocus. 
    */

    event.preventDefault();
    let mode = key === "ArrowDown" || key === "ArrowRight" ? "enter" : "del";
    let dir =
      key === "ArrowDown" || key === "ArrowUp"
        ? this.directions[1]
        : this.directions[0];
    let oldCellCoords = Interaction.getCellElement(this.cellCoords);
    let newCellCoords = this.shiftCellCoords(this.cellCoords, dir, mode, true);
    let skipFlag = false;

    // Attempt to find an unfilled cell in the direction of the arrow press
    // (if shifting into an empty cell)
    try {
      while (
        Interaction.getCellElement(newCellCoords).classList.contains(
          "empty_cell"
        )
      ) {
        newCellCoords = this.shiftCellCoords(newCellCoords, dir, mode, true);
        skipFlag = true;
      }
    } catch (err) {
      // Couldn't find any unfilled cells
      newCellCoords = this.cellCoords;
    }

    this.setFocusMode(false);
    // If moving perpendicular to an intersection, only alternate the direction
    // and retain the prior ``cellCoords``
    if (this.shouldDirectionBeAlternated(newCellCoords)) {
      this.alternateDirection();
      // Cells were skipped to reach these new coordinates, so update
      // ``cellCoords``
      if (skipFlag) {
        this.cellCoords = newCellCoords;
      }
      skipFlag = false;
    } else {
      this.cellCoords = newCellCoords;
    }
    this.followCellZoom(oldCellCoords);
    this.currentWord = this.updateCurrentWord();
    this.setFocusMode(true);
    this.updateDefinitionsListPos();
  }

  handleEnterPress(event) {
    /* Handle a tab-related enter press to either select a new definitions list
    item or invoke and close the dropdown of a dropdown button. 
    */

    if (event.target.classList.contains("def")) {
      event.target.click();
      event.target.blur();
      if (this.zoomToggle.checked) {
        // Allow users with no keyboard to initiate
        // zooming via pressing enter on a definition
        this.doNotHandleStandardCellClick = true;
        Interaction.getCellElement(this.cellCoords).click();
      }
    } else if (event.target.classList.contains("toggle")) {
      event.target.click();
    }
  }

  handleEnterKeybindPress(event) {
    /* Allow the user to check the current word with "Enter" or reveal it with 
    [Shift + Enter]. 
    */

    Interaction.unfocusActiveElement();
    this.hideDropdowns();
    let mode = event.shiftKey ? "reveal" : "check";
    this.doSpecialButtonAction("word", mode, false);
  }

  handleSpacebarPress(event) {
    /* Alternate direction when pressing the spacebar at an intersection. */

    event.preventDefault();
    this.setFocusMode(false);
    this.alternateDirection();
    this.currentWord = this.updateCurrentWord();
    this.setFocusMode(true);
    this.updateDefinitionsListPos();
  }

  handleEscapePress(event) {
    /* Remove focus from everything. */

    event?.preventDefault();
    Interaction.unfocusActiveElement();
    this.hideDropdowns();
    this.setFocusMode(false);
    this.zoomOut();
    this.cellCoords = null;
    this.currentWord = null;
  }

  crosswordCompletionHandler() {
    if (this.isCrosswordComplete()) {
      Interaction.sleep(1).then(() => {
        // Allow the input the user just made
        // to be shown by the DOM
        this.handleEscapePress(null);
        this.displayCompletionPopup();
        this.jazz.play();
      });
    }
  }

  doSpecialButtonAction(
    magnitude,
    mode,
    viaButton = true,
    onlyUnchecked = false
  ) {
    /* Perform reveal/check/clear operations on a selected cell, word, or, the 
    grid. 
    */

    // Since the user is running the function from a dropdown button, close the
    // dropdown that the button belongs to
    if (viaButton) {
      this.onDropdownClick(mode + "_dropdown");
    }

    // The user must have a word selected to be able to check/reveal the
    // current cell/word
    if (this.cellCoords === null && magnitude !== "grid") {
      return alert(this.errMsgs[0]);
    }

    switch (magnitude) {
      case "cell": // Just do a single grid operation on the current cell
        let currentCell = Interaction.getCellElement(this.cellCoords);
        this.doGridOperation(currentCell, mode);
        if (mode === "reveal") {
          // Automatically go to the next cell
          this.handleCellShift("enter", currentCell);
        }
        break;
      case "word": // Do a grid operation on each element of the word
        for (const cell of this.getWordElements()) {
          this.doGridOperation(cell, mode);
        }
        if (mode === "reveal" && this.wordToggle.checked) {
          // Automatically go to the next word
          this.shiftWordSelection(null, "ArrowDown");
        }
        break;
      case "grid": // Do a grid operation on each non empty cell of the grid
        document
          .querySelectorAll(".non_empty_cell")
          .forEach(cell => this.doGridOperation(cell, mode, onlyUnchecked));
    }

    this.crosswordCompletionHandler();
  }

  doGridOperation(cell, mode, onlyUnchecked = false) {
    /* Perform either a reveal, check or clear action on a single cell. */

    if (mode === "reveal") {
      cell.classList.remove("wrong");
      Interaction.setValue(cell, cell.getAttribute("data-value"));
      cell.classList.add("lock_in"); // This cell must now be correct, so lock
                                     // it in
    } else if (mode === "check") {
      if (!Interaction.isEmpty(cell)) {
        if (cell.hasCorrectValue()) {
          // This cell is correct, lock it in
          cell.classList.add("lock_in");
        } else {
          cell.classList.add("wrong");
        }
      }
    } else if (mode === "clear") {
      if (
        // Clearing unrevealed
        (onlyUnchecked && !cell.classList.contains("lock_in")) ||
        !onlyUnchecked // < Normal clear
      ) {
        cell.classList.remove("lock_in");
        cell.classList.remove("wrong");
        Interaction.setValue(cell, "");
      }
    }
  }

  shouldDirectionBeAlternated(coords) {
    /* Return true if shifting the cell coords in both enter and delete mode
    returns values that are identical to the current cell coordinates (passed
    as the ``coords`` parameter). This likely means the user clicked on a new
    word that is a different direction to the current one, or they skipped over
    void cells as a result of ``this.handleArrowPress``.
    */

    return (
      this.shiftCellCoords(coords, this.direction, "enter").isEqualTo(coords) &&
      this.shiftCellCoords(coords, this.direction, "del").isEqualTo(coords)
    );
  }

  setFocusMode(focus) {
    if (this.cellCoords !== null) {
      this.changeWordFocus(focus);
      this.changeCellFocus(focus);
      this.changeDefinitionsListItemFocus(focus);
    }
  }

  changeWordFocus(focus) {
    /* Retrieve the starting and ending coordinates of a word and change the 
    colour of the cell elements that make up that word to either blue (focused)
    or white/black (unfocused).
    */

    for (const element of this.getWordElements()) {
      element.style.backgroundColor = focus
        ? this.colourPalette.WORD_FOCUS
        : this.colourPalette.SUB;
    }
  }

  changeCellFocus(focus) {
    return (Interaction.getCellElement(this.cellCoords).style.backgroundColor =
      focus ? this.colourPalette.CELL_FOCUS : this.colourPalette.SUB);
  }

  changeDefinitionsListItemFocus(focus) {
    return (this.getDefinitionsListItemFromWord().style.backgroundColor = focus
      ? this.colourPalette.WORD_FOCUS
      : "");
  }

  updateCurrentWord() {
    /* Return the current word in uppercase. */

    let word = "";
    for (const element of this.getWordElements()) {
      word += element.getAttribute("data-value");
    }

    return word.toUpperCase();
  }

  *getWordElements() {
    /* Generator function that yields all the consisting cell elements of the 
    current word. 
    */

    let [startCoords, endCoords] = this.getWordIndices();
    for (let i = startCoords; i <= endCoords; i++) {
      let coords = this.isDown ? [i, this.staticIndex] : [this.staticIndex, i];
      yield Interaction.getCellElement(coords);
    }
  }

  getWordIndices() {
    /* Iterate either across or down through the grid to find the starting and 
    ending indices of a word. 
    */

    let [row, col] = this.cellCoords;
    this.isDown = this.direction === this.directions[1];
    this.staticIndex = this.isDown ? col : row; // The index that never changes (the row
                                                // if direction is across, etc)
    let [startCoords, endCoords] = this.isDown ? [row, row] : [col, col];

    // Find starting coords of the word
    while (
      startCoords > 0 &&
      this.grid[this.isDown ? startCoords - 1 : row][
        this.isDown ? col : startCoords - 1
      ] != this.empty
    )
      startCoords--;

    // Find ending coords of the word
    while (
      endCoords < this.dimensions - 1 &&
      this.grid[this.isDown ? endCoords + 1 : row][
        this.isDown ? col : endCoords + 1
      ] != this.empty
    )
      endCoords++;

    return [startCoords, endCoords];
  }

  alternateDirection() {
    return (this.direction =
      this.direction === this.directions[0]
        ? this.directions[1]
        : this.directions[0]);
  }

  getDefinitionsListItemFromWord() {
    return document.querySelector(`[data-word="${this.currentWord}"]`);
  }

  updateDefinitionsListPos() {
    let def = this.getDefinitionsListItemFromWord(this.currentWord);
    def.focus();
    def.blur();
  }

  isCrosswordComplete() {
    return this.getGrid().isEqualTo(this.grid);
  }

  getGrid() {
    /* Create an empty replica of the crossword grid, then update it according 
    to the web app grid 
    */

    let webAppGrid = Array.from({ length: this.dimensions }, () =>
      Array(this.dimensions).fill(this.empty)
    );

    document.querySelectorAll(".non_empty_cell").forEach(cell => {
      let row = parseInt(cell.getAttribute("data-row"));
      let column = parseInt(cell.getAttribute("data-column"));
      let value = cell.childNodes[0].nodeValue.toUpperCase();
      webAppGrid[row][column] = value;
    });

    return webAppGrid;
  }

  setCompoundInput(priorValue) {
    /* Remove the value of the current cell and add an input element to its
    children.
    */
    this.compoundInputActive = true;
    if (!priorValue) {
      this.wasEmpty = true;
    }
    let currentCell = Interaction.getCellElement(this.cellCoords);
    currentCell.onclick = event => Interaction.dummyCellClick(event);
    Interaction.setValue(currentCell, "");

    let compoundInput = document.createElement("input");
    compoundInput.value = priorValue;
    compoundInput.type = "text";
    compoundInput.classList.add("compound_input");
    currentCell.appendChild(compoundInput);
    compoundInput.focus();
  }

  handleSetCompoundInput(andShiftForwarder = true) {
    if (this.cellCoords === null) {
      // User must select a cell
      return alert(this.errMsgs[0]);
    }
    // User already has a compound input selected, so they want to remove it
    if (document.getElementsByClassName("compound_input")[0]) {
      return this.removeCompoundInput(andShiftForwarder);
    }
    let nodes = Interaction.getCellElement(this.cellCoords).childNodes;
    let priorValue = nodes[0].nodeValue;
    if (nodes.length > 1) {
      nodes[1].style.display = "none"; // Hide number label if possible
    }
    this.setCompoundInput(priorValue);
  }

  removeCompoundInput(andShift = true) {
    if (!this.compoundInputActive) {
      return;
    } // Maybe the user triggered this method with a click but no compound input
    // element exists
    let compoundInput = document.getElementsByClassName("compound_input")[0];
    let cellOfCompoundInput = compoundInput.parentElement;
    let enteredText = compoundInput.value;
    try {
      if (!enteredText[0].match(onlyLangRegex)) {
        enteredText = "";
      }
    } catch (err) {
      enteredText = "";
    }
    compoundInput.remove();
    let nodes = cellOfCompoundInput.childNodes;
    nodes[0].nodeValue = enteredText[0];
    if (nodes.length > 1) {
      nodes[1].style.display = "inline"; // Reset number label display
    }
    cellOfCompoundInput.onclick = event =>
      this.onCellClick(event, cellOfCompoundInput);
    cellOfCompoundInput.classList.remove("lock_in", "wrong");

    this.compoundInputActive = false;
    this.currentPlaceholder = 0;

    if (this.checkToggle.checked) {
      this.doGridOperation(cellOfCompoundInput, "check");
    }
    if (andShift) {
      this.handleCellShift("enter", cellOfCompoundInput); // Shift focus for
                                                          // ease of use
    }
  }

  cycleCompoundInputPlaceholderText() {
    /* Cycle placeholder text whenever a compound input element is active. */
    let compoundInput = document.getElementsByClassName("compound_input")[0];
    if (compoundInput === undefined) {
      return;
    }
    compoundInput.placeholder =
      compoundInputPlaceholders[this.currentPlaceholder];
    if (
      this.currentPlaceholder ===
      compoundInputPlaceholders.length - 1
    ) {
      this.currentPlaceholder = 0;
    } else {
      this.currentPlaceholder += 1;
    }
  }

  removeCompoundInputIfRequired(cell) {
    /* Remove the compound input if it is already active and the ``cell`` element
    is not equal to the current cell.
    */
    if (
      this.compoundInputActive &&
      cell !== Interaction.getCellElement(this.cellCoords)
    ) {
      this.removeCompoundInput();
    }
  }

  followCellZoom(priorCell) {
    /* If the priorCell was zoomed too, then now zoom to the current cell. */
    if (
      document.querySelectorAll(".non_empty_cell.selectedZoomTarget").length ===
      1
    ) {
      let currentCell = Interaction.getCellElement(this.cellCoords);
      if (currentCell !== priorCell) {
        this.doNotHandleStandardCellClick = true;
        return currentCell.click();
      }
    }
  }

  handleClick(event) {
    /* Close dropdowns and remove compound input (if possible) when clicking 
    outside of the dropdown area. 
    */
    if (!event.target.closest(".special_button, .dropdown, .dropdown_button")) {
      this.hideDropdowns();
      this.removeCompoundInput(false);
    }
  }

  handleDropdownFocusOut(event) {
    /* Hide dropdowns based on specific conditions. */
    /* The following condition evaluates to true if:
        1. Focusing into something that is not a "dropdown_button" OR
        2. Focusing out of something that is a "dropdown_button" AND
            - You are focusing into something that is a "special_button" AND
            - You are focusing into something that has an id that does not match 
              the start of the currentDropdown
        3. You are focusing out of a "special_button" into something that is 
           either another special button or something that isn't a "dropdown_button"
    */
    if (
      !event.relatedTarget?.classList.contains("dropdown_button") ||
      (event.target?.classList.contains("dropdown_button") &&
        event.relatedTarget?.classList.contains("special_button") &&
        !event.relatedTarget?.id.startsWith(
          this.currentDropdown?.substring(0, this.currentDropdown?.indexOf("_"))
        )) ||
      (event.target.id?.endsWith("button") &&
        (event.relatedTarget?.id?.endsWith("button") ||
          !event.relatedTarget?.classList?.contains("dropdown_button")))
    ) {
      this.hideDropdowns();
    }
  }

  hideDropdowns() {
    document
      .querySelectorAll(".dropdown")
      .forEach(element => element.classList.remove("show_dropdown"));
    document
      .querySelectorAll(".special_button")
      .forEach(
        element => (element.innerHTML = element.innerHTML.replace("▲", "▼"))
      );
    this.currentDropdown = null;
  }

  onDropdownClick(id) {
    /* Opens the dropdown a user clicks on or closes it if they already have it 
    open. 
    */
    this.removeCompoundInput(false);
    let dropdown = document.getElementById(id);

    if (id === this.currentDropdown) {
      this.hideDropdowns();
      this.currentDropdown = null;
      return;
    }

    this.hideDropdowns();
    let dropdownButton = document.getElementById(
      id.replace("_dropdown", "_button")
    );
    dropdownButton.innerHTML = dropdownButton.innerHTML.replace("▼", "▲");
    dropdown.classList.add("show_dropdown");
    this.currentDropdown = id;
  }

  displayOnloadPopup() {
    this.onloadPopupToggled = true;

    Interaction.sleep(200).then(() => {
      document.getElementById("blur").classList.toggle("active");
      document.getElementById("onload_popup").classList.toggle("active");
      Interaction.sleep(301).then(() => {
        document
          .getElementsByClassName("continue_button")[0]
          .focus({ focusVisible: true });
      });
    });
  }

  displayCompletionPopup() {
    this.completionPopupToggled = !this.completionPopupToggled;
    document.getElementById("blur").classList.toggle("active");
    document.getElementById("completion_popup").classList.toggle("active");
    if (this.completionPopupToggled) {
      // Focus the close button
      Interaction.sleep(501).then(
        () =>
          document
            .getElementsByClassName("close_button")[0]
            .focus({ focusVisible: true }) // Ensure the user can see the focus
      );
    }
  }

  closeOnloadPopup(firstTime = false) {
    this.onloadPopupToggled = false;
    document.getElementById("blur").classList.toggle("active");
    document.getElementById("onload_popup").classList.toggle("active");
    if (firstTime) {
      document.querySelector(`[data-num="1"`).click();
    }
  }

  preventZoomIfRequired(event) {
    /* Prevent the user from zooming if they do not have the "click to zoom"
      button toggled on. This must be handled as the zoom functions from zoomooz.js
      must always be in the HTML structure. */

    if (!document.getElementById("tz").checked || this.preventInitialLIZoom) {
      this.preventInitialLIZoom = false;
      event.stopImmediatePropagation(); // Prevent ``zoomooz`` from zooming
    }
  }

  static dummyCellClick(event) {
    return event.stopImmediatePropagation();
  }

  static unfocusActiveElement() {
    document.activeElement.blur();
  }

  static emulateEscapePress() {
    return document.dispatchEvent(
      new KeyboardEvent("keyboard", { key: "Escape" })
    );
  }

  static sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  static isEmpty(cell) {
    return !cell?.childNodes[0]?.nodeValue;
  }

  static setValue(cell, value) {
    return (cell.childNodes[0].nodeValue = value);
  }

  static getCellElement(coords) {
    return document.querySelector(
      `[data-row="${coords[0]}"][data-column="${coords[1]}"]`
    );
  }

  static updateCellCoords(cell) {
    return [
      parseInt(cell.getAttribute("data-row")),
      parseInt(cell.getAttribute("data-column")),
    ];
  }

  static configureScrollHeights() {
    /* Configure proper heights of ``zoomooz`` zoom viewports as well as 
    bugged overflow content in the definitions zoom container. 
    */

    let definitionsA = document.querySelector(".definitions_a");
    let definitionsD = document.querySelector(".definitions_d");
    document.getElementById("return_def_zoom").style.height =
      Math.max(definitionsA.scrollHeight, definitionsD.scrollHeight) + "px";

    // Prevent the unecessary scrollbar in the zoomContainer
    let defZoomContainer = document.getElementById("no_scroll");
    if (defZoomContainer.scrollHeight - 1 > defZoomContainer.clientHeight)
      // For some reason the scrollHeight is 1 greater than the clientHeight
      defZoomContainer.style.overflowY = "auto";
  }
}

Array.prototype.isEqualTo = function (arr) {
  return JSON.stringify(this) === JSON.stringify(arr);
};
Element.prototype.hasCorrectValue = function () {
  return (
    this.childNodes[0].nodeValue.toUpperCase() ===
    this.getAttribute("data-value")
  );
};

let interaction = new Interaction();

// Enable easter egg through console
function egg() {
  interaction.playClicks = !interaction.playClicks;
  if (interaction.playClicks) {
    return "EASTER EGG ON";
  } else {
    return "EASTER EGG OFF";
  }
}