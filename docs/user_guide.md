## GUI
How to operate the GUI once you have opened it with `xpuz-ctk`.

### Home Screen
???+ info "Configuring global settings"
    1. Click on the down arrow next to a dropdown
    2. Find your desired option and click on it.

???+ info "View/edit crosswords"
    1. Click `Browser` or `Editor`, respectively.

### Crossword Browser
???+ info "Play a crossword"
    1. Click `View` on whichever category you like (e.g. `Geography`).
    2. Select a crossword by clicking on the box next to `Select`. You can scroll using your scroll wheel.
    3. Select a word count. The `Maximum` option is selected by default, but you can select the `Custom` option, click on the dropdown and select however many words you want to see in your crossword.
    4. Load the crossword by pressing `Create`.
    5. Once it is loaded, open the crossword in your browser by pressing `Play`. This may take a bit if your browser isn't open already. If you have issues, visit [Troubleshooting](troubleshooting.md)

???+ info "Changing crossword game view"
    1. Follow steps `1` to `4` for **Play a crossword**.
    2. Choose a view option from the `Game view` option menu.
    3. Press `Play`.

???+ info "Export a crossword to `ipuz` or `PDF`"
    1. Follow steps `1` to `4` for **Play a crossword**.
    2. Choose an export option from the `Export as` option menu.
    3. Press the download button on the right of the option menu and choose a destination to save your crossword. Ensure it is a valid OS path with no illegal characters.

### Crossword Editor
???+ info "Make a new crossword"
    1. Press `+` in the bottom right of the first preview panel.
    2. Give your crossword a name, symbol, and change the difficulty if you wish.
    3. Press `Add`.

???+ info "Edit a crossword"
    1. Select a crossword under `Your crosswords` by pressing the box button next to its name.
    2. Update your crossword's name, symbol or difficulty.
    3. Press `Save`.

???+ info "Making/editing a crossword's words"
    1. Select a crossword and the right pane for word editing will be enabled. The processes of editing and creating words is identical to the steps explained in the prior information blocks.

???+ info "Export your crosswords to a single file in `JSON` format"
    1. Ensure you have at least one crossword in your user crosswords.
    2. Press the button with the downwards pointing arrow.
    3. Choose a destination and press save.
    4. Share it around!

???+ info "Import crosswords from `*.JSON`"
    1. Press the button with the upward pointing arrow.
    2. Find and select a valid `JSON` file that was exported through `xpuz`'s editor.
    3. All the valid crossword entries will be imported. If there are any crosswords with an identical name and difficulty, they will not be imported and a message box will display the conflicting crosswords in question.

## Crossword Game

### controls <small>for interacting with a crossword</small> { #controls data-toc-label="controls" }

| Key/Keybind/Action | What it does |
| ------------------ | ------------ |
| Click on cell | Select the cell |
| Click on empty space | Unzoom |
| Click twice at intersecting point | Alternate direction |
| Click on word definition | Select the corresponding word |
| Click on dropdown | Open dropdown |
| Click on dropdown button | Perform relevant dropdown action |
| Click on toggle | Enable toggle feature |
| Click on `Compound` or ++shift+1++ | Toggle compound input for your current cell |
| `Any Key` | Enter a value into the grid (if it is a language character) and move your focus. |
| ++back++ | Delete the value in your current cell and shift your focus back if possible. |
| ++arrow-up++, ++arrow-down++, etc. | Move your cell focus, skipping over void cells if possible to reach an available cell. |
| ++esc++ | Remove word focus and/or zoom |
| ++space++ | Alternate your typing direction if you are at an intersection. |
| ++tab++ and ++shift+tab++ | Cycle your element focus forward or backward. |
| ++enter++ | Press whatever you are focused on with Tab. Otherwise, check the current word. |
| ++shift+enter++ | Reveal the current word |
| ++shift+backspace++ | Delete the current word |
| ++shift+arrow-down++ | Move to the next word (or move to the first word if have the last word selected). |
| ++shift+arrow-up++ | Move to the previous word (or move to the last word if you have the first word selected). |

### special operations <small>accessed through dropdowns</small> { #special-operations data-toc-label="special operations" }

| Operation | What it does |
| --------- | ------------ |
| `Reveal` | Reveal the current cell, word or the grid. It will then become green and uneditable. |
| `Check` | Check the current cell, word or the grid. If it is correct, it will become green and uneditable. If it is incorrect, it will become red and it will retain its ability to be deleted.
| `Clear` | Clear the current word or the grid. Alternatively, you can clear all unrevealed cells, meaning those that aren't green. |

### toggles <small>to enable/disable special features</small> { #toggles data-toc-label="toggles" }

| Toggle | What it does |
| ------ | ------------ |
| `Auto-skip` | Automatically skip over filled cells when typing. |
| `Auto-word` | Automatically move to the next word. There are many ways this feature can be activated, but its functionality has been fine-tuned to only occur when you have most likely finished typing a word. |
| `Auto-check` | Automatically check if your input if correct/wrong. If it is wrong, the cell text becomes red and can be deleted. If it is correct, the cell text becomes green and can no longer be modified. |
| `Zoom` | Automatically zooms into a grid cell if when clicking on it or invoking a word definition with `Tab` focus. Automatically zooms into a word definition if you click on it. To unzoom, either click on the zoomed element or click on something that cannot be interacted with in any way (like a void cell or the background). |

### inclusivity features <small>to improve your experience</small> { #inclusivity-features data-toc-label="inclusivity-features" }
- **Compound input**

If your language requires you to merge two or more characters into one, you can activate compound input to do this. When you are done, press enter, and the leftmost character you typed will be inserted into your current cell.

- **Tab accessibility**

Simply press tab to focus on different elements. If you are on the element you want to interact with, simply press `Enter` to invoke it. Grid zooming will activate if you have it enabled by tabbing to and invoking a word's definition.