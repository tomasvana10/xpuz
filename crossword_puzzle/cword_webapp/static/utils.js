let completionPopupToggled = false;
let onloadPopupToggled = false;
let currentDropdown = null;

document.addEventListener("click", (event) => {
    // Close dropdowns if clicking outside of the dropdown area
    if (!event.target.closest(".special_button, .dropdown, .dropdown_button")) {
        hideDropdowns();
    }
});

document.addEventListener("focusout", (event) => {
    // Hide dropdowns based on specific conditions
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
                currentDropdown?.substring(0, currentDropdown?.indexOf("_"))
            )) ||
        (event.target.id?.endsWith("button") &&
            (event.relatedTarget?.id?.endsWith("button") ||
                !event.relatedTarget?.classList?.contains("dropdown_button")))
    ) {
        hideDropdowns();
    }
});

const hideDropdowns = () => {
    document
        .querySelectorAll(".dropdown")
        .forEach((element) => element.classList.remove("show_dropdown"));
    currentDropdown = null;
};

function toggleCompletionPopup() {
    completionPopupToggled = !completionPopupToggled;
    document.getElementById("blur").classList.toggle("active");
    document.getElementById("completion_popup").classList.toggle("active");
    if (completionPopupToggled) {
        // Focus the close button
        sleep(501).then(
            () =>
                document
                    .getElementsByClassName("close_button")[0]
                    .focus({ focusVisible: true }) // Ensure the user can see 
                                                   // the focus
        );
    }
}

function onDropdownClick(id) {
    /* Opens the dropdown a user clicks on or closes it if they already have it 
    open. */

    let dropdown = document.getElementById(id);
    if (id === currentDropdown) {
        dropdown.classList.remove("show_dropdown");
        currentDropdown = null;
        return;
    }

    hideDropdowns();
    dropdown.classList.add("show_dropdown");
    currentDropdown = id;
}

function closeOnloadPopup() {
    onloadPopupToggled = false;
    document.getElementById("blur").classList.toggle("active");
    document.getElementById("onload_popup").classList.toggle("active");
}
