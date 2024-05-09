class Interaction {
  /* Class to handle all forms of interaction with the web app.
  
  Also contains utility functions to perform cell-related calculations.
	*/

  static arrowKeys = ["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"];
  static spacebarKeys = ["Spacebar", " "];
  static backspaceKeys = ["Backspace", "Delete"];
  static compoundInputPlaceholders = [
    "ㅇ", "+", "ㅏ", "=", "아", "क​", "+", "इ", "=", "कै",
  ];
  static onlyLangRegex = /\p{L}/u; // Ensure user only types language characters

  constructor() {
    this.direction = "ACROSS"; // Default direction when first clicking (if the
                               // first click is at an intersection).
    this.currentWord = null; // e.x. "HELLO"
    this.cellCoords = null; // e.x. [0, 5]
    this.staticIndex = null; // e.x. 5

    this.isDown = null;
    this.wasEmpty = null;
    this.compoundInputActive = null;
    this.completionPopupToggled = false;
    this.onloadPopupToggled = false;
    this.currentDropdown = null;
    this.currentPlaceholder = 0;

    // When the DOM is ready, trigger the ``onLoad`` method
    document.addEventListener("DOMContentLoaded", this.onLoad.bind(this));
  }

  onLoad() {
    // Get data from HTML body
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

    this.setListeners();
    this.displayOnloadPopup();
    // Clear the grid to prevent possible issues with HTML
    this.doSpecialButtonAction("grid", "clear", false);
    // Cycle placeholder text if a compound input element is available
    setInterval(this.cycleCompoundInputPlaceholderText.bind(this), 750);
  }

  setListeners() {
    /* Add listeners and onclick functions. */

    document
      .querySelectorAll(".non_empty_cell")
      .forEach(
        element => (element.onclick = event => this.onCellClick(event, element))
      );

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

    document.getElementById("compound_button").onclick = () => {
      this.handleSetCompoundInput();
    };

    document.addEventListener("keydown", event =>
      this.handleSpecialInput(event)
    );

    document.addEventListener("click", event =>
      this.handleClickForDropdowns(event)
    );

    document.addEventListener("focusout", event =>
      this.handleDropdownFocusOut(event)
    );
  }

  handleSpecialInput(event) {
    /* Check if the user wants to do a special action, for example, performing
    a keybind. If this is the case, this function will process it and prevent
    ``this.handleStandardInput`` from running. 
    */

    let inputValue = event.key;

    // Handle the setting of a compound input element when pressing [Shift + 1]
    if (inputValue === "!" && event.shiftKey && this.cellCoords !== null) {
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
      !this.completionPopupToggled &&
      !this.onloadPopupToggled &&
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
    if (Interaction.backspaceKeys.includes(inputValue) && event.shiftKey) {
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

    // Move the user's cell focus since they have pressed an arrow key
    if (Interaction.arrowKeys.includes(inputValue)) {
      return this.handleArrowPress(inputValue, event);
    }

    // Alternate the user's direction since they are at an intersection
    if (
      this.intersections.includes(JSON.stringify(this.cellCoords)) &&
      Interaction.spacebarKeys.includes(inputValue) // Pressing "Spacebar"
    ) {
      return this.handleSpacebarPress(event);
    }

    // User is just typing into the grid normally
    this.handleStandardInput(inputValue);
  }

  handleStandardInput(inputValue) {
    /* Handle a normal keyboard input from the user. */

    let mode = Interaction.backspaceKeys.includes(inputValue) ? "del" : "enter";
    let currentCell = Interaction.getCellElement(this.cellCoords);

    if (mode === "enter") {
      // Ensure the user is typing a language character that is not longer
      // than 1 character
      if (
        !(
          inputValue.length === 1 && inputValue.match(Interaction.onlyLangRegex)
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
      }
      // If the cell is wrong/red in colour, it must be reverted as the user
      // has just typed in it
      currentCell.classList.remove("wrong");

    } else if (mode === "del") {
      // The focused cell has content, just delete it and do nothing
      if (
        !Interaction.isEmpty(currentCell) &&
        !currentCell.classList.contains("lock_in")
      )
        return Interaction.setValue(currentCell, "");

      // Perform standard deletion, whereby the content of the cell to the
      // right/top of the current cell is deleted, then the focus is shifted
      // to that cell
      if (
        !Interaction.getCellElement(
          this.shiftCellCoords(this.cellCoords, this.direction, mode)
        ).classList.contains("lock_in")
      )
        Interaction.setValue(
          Interaction.getCellElement(
            this.shiftCellCoords(this.cellCoords, this.direction, mode)
          ),
          ""
        );
    }

    // Detect possible crossword completion after the grid has been modified
    this.crosswordCompletionHandler();
    this.handleCellShift(mode);
  }

  handleCellShift(mode) {
    /* Determines how the focus of a cell within a word is shifted. */

    this.changeCellFocus(false);
    // User has the "smart skip" button toggled, so perform a cell skip
    if (mode === "enter" && document.getElementById("ts").checked) {
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

    // Refocus the entire word, then set the focus of the cell that has just
    // been shifted/skipped to. No need to update the current word as the current
    // word can never change with a standard keyboard input.
    this.changeWordFocus(true);
    this.changeCellFocus(true);
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
      // no longer skip, so exit the while loop
      if (oldCellCoords.isEqualTo(newCellCoords)) {
        break;
      }
    }

    return newCellCoords;
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
      `[data-num_label="${numLabel}"]`).parentElement

    Interaction.preventZoomIfRequired(event);
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
    this.currentWord = this.updateCurrentWord();
    this.setFocusMode(true);
  }

  onCellClick(event, cell) {
    /* Handles how the grid responds to a user clicking on the cell. Ensures 
      the appropriate display of the current cell and word focus on cell click, 
      as well as alternating input directions if clicking at an intersecting point 
      between two words. 
    */

    Interaction.preventZoomIfRequired(event);
    this.removeCompoundInputIfRequired(cell)

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
    this.currentWord = this.updateCurrentWord();
    this.setFocusMode(true);
    this.updateDefinitionsListPos();
  }

  handleEnterPress(event) {
    /* Handle a tab-related enter press to either select a new definitions list
      item or invoke and close the dropdown of a dropdown button. */

    if (event.target.classList.contains("def")) {
      event.target.click();
      event.target.blur();
    } else if (event.target.classList.contains("toggle")) {
      event.target.click();
    }
  }

  handleEnterKeybindPress(event) {
    /* Allow the user to check the current word with "Enter" or reveal it with 
      [Shift + Enter]. */

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

    event.preventDefault();
    Interaction.unfocusActiveElement();
    this.hideDropdowns();
    this.setFocusMode(false);
    this.cellCoords = null;
    this.currentWord = null;
  }

  crosswordCompletionHandler() {
    if (this.isCrosswordComplete()) {
      Interaction.sleep(1).then(() => {
        // Allow the input the user just made to be shown by the DOM
        Interaction.emulateEscapePress();
        this.toggleCompletionPopup();
      });
    }
  }

  doSpecialButtonAction(magnitude, mode, viaButton = true) {
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
        this.doGridOperation(Interaction.getCellElement(this.cellCoords), mode);
        break;
      case "word": // Do a grid operation on each element of the word
        for (const cell of this.getWordElements()) {
          this.doGridOperation(cell, mode);
        }
        break;
      case "grid": // Do a grid operation on each non empty cell of the grid
        document
          .querySelectorAll(".non_empty_cell")
          .forEach(cell => this.doGridOperation(cell, mode));
    }

    this.crosswordCompletionHandler();
  }

  doGridOperation(cell, mode) {
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
      cell.classList.remove("lock_in");
      cell.classList.remove("wrong");
      Interaction.setValue(cell, "");
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
      current word. */

    let [startCoords, endCoords] = this.getWordIndices();
    for (let i = startCoords; i <= endCoords; i++) {
      let coords = this.isDown ? [i, this.staticIndex] : [this.staticIndex, i];
      yield Interaction.getCellElement(coords);
    }
  }

  getWordIndices() {
    /* Iterate either across or down through the grid to find the starting and 
      ending indices of a word. */

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
    this.getDefinitionsListItemFromWord(this.currentWord).focus();
    this.getDefinitionsListItemFromWord(this.currentWord).blur();
  }

  isCrosswordComplete() {
    return this.getGrid().isEqualTo(this.grid);
  }

  getGrid() {
    /* Create an empty replica of the crossword grid, then update it according 
      to the web app grid */

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
    if (!priorValue) { this.wasEmpty = true; }
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

  handleSetCompoundInput() {
    if (this.cellCoords === null) { // User must select a cell
      return alert(this.errMsgs[0]);
    }
    // User already has a compound input selected, so they want to remove it
    if (document.getElementsByClassName("compound_input")[0]) {
      return this.removeCompoundInput();
    }
    let priorValue = Interaction.getCellElement(this.cellCoords).childNodes[0]
      .nodeValue;
    this.setCompoundInput(priorValue);
  }

  removeCompoundInput(andShift=true) {
    if (!this.compoundInputActive) { return; } // failsafe
    let compoundInput = document.getElementsByClassName("compound_input")[0];
    let cellOfCompoundInput = compoundInput.parentElement;
    let enteredText = compoundInput.value;
    try {
      if (!enteredText[0].match(Interaction.onlyLangRegex)) {
        enteredText = "";
      }
    } catch (err) {
      enteredText = "";
    }
    compoundInput.remove();
    cellOfCompoundInput.childNodes[0].nodeValue = enteredText[0];
    cellOfCompoundInput.onclick = event =>
      this.onCellClick(event, cellOfCompoundInput);
    cellOfCompoundInput.classList.remove("lock_in", "wrong");
    this.compoundInputActive = false;
    this.currentPlaceholder = 0;
    if (andShift) {
      this.handleCellShift("enter"); // Shift focus for ease of use
    }
  }

  cycleCompoundInputPlaceholderText() {
    /* Cycle placeholder text whenever a compound input element is active. */
    let compoundInput = document.getElementsByClassName("compound_input")[0];
    if (compoundInput === undefined) {
      return;
    }
    compoundInput.placeholder =
      Interaction.compoundInputPlaceholders[this.currentPlaceholder];
    if (
      this.currentPlaceholder ===
      Interaction.compoundInputPlaceholders.length - 1
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

  handleClickForDropdowns(event) {
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
    open. */
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

  toggleCompletionPopup() {
    this.completionPopupToggled = !this.completionPopupToggled;
    document.getElementById("blur").classList.toggle("active");
    document.getElementById("completion_popup").classList.toggle("active");
    if (this.completionPopupToggled) {
      // Focus the close button
      Interaction.sleep(501).then(
        () =>
          document
            .getElementsByClassName("close_button")[0]
            .focus({ focusVisible: true }) // Ensure the user can see
        // the focus
      );
    }
  }

  closeOnloadPopup() {
    this.onloadPopupToggled = false;
    document.getElementById("blur").classList.toggle("active");
    document.getElementById("onload_popup").classList.toggle("active");
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

  static preventZoomIfRequired(event) {
    /* Prevent the user from zooming if they do not have the "click to zoom"
      button toggled on. This must be handled as the zoom functions from zoomooz.js
      must always be in the HTML structure. */

    if (!document.getElementById("tz").checked)
      // Button isn't checked
      event.stopImmediatePropagation(); // Prevent zoomooz from zooming
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
