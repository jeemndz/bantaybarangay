/* =========================================================
   BANTAYBARANGAY TOP NAVIGATION
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    initializeTopNavigation();

});


/* =========================================================
   INITIALIZE
========================================================= */

function initializeTopNavigation() {

    closeAllDropdowns();
    closeMobileNav();
    updateMobileMenuIcon();

}


/* =========================================================
   TOGGLE DROPDOWN
========================================================= */

function toggleDropdown(id, event) {

    if (event) {

        event.preventDefault();
        event.stopPropagation();

    }

    const dropdown =
        document.getElementById(id);

    if (!dropdown) {

        console.warn(
            "Dropdown not found:",
            id
        );

        return;

    }

    const shouldOpen =
        dropdown.classList.contains("hidden");

    closeAllDropdowns();

    if (shouldOpen) {

        dropdown.classList.remove("hidden");

    }

}


/* =========================================================
   CLOSE ALL DROPDOWNS
========================================================= */

function closeAllDropdowns() {

    document
        .querySelectorAll('[id$="Dropdown"]')
        .forEach(function (dropdown) {

            dropdown.classList.add("hidden");

        });

}


/* =========================================================
   MOBILE NAVIGATION
========================================================= */

function toggleMobileNav(event) {

    if (event) {

        event.preventDefault();
        event.stopPropagation();

    }

    const mobileNav =
        document.getElementById("mobileNav");

    if (!mobileNav) {
        return;
    }

    closeAllDropdowns();

    mobileNav.classList.toggle("hidden");

    updateMobileMenuIcon();

}


/* =========================================================
   CLOSE MOBILE NAVIGATION
========================================================= */

function closeMobileNav() {

    const mobileNav =
        document.getElementById("mobileNav");

    if (!mobileNav) {
        return;
    }

    mobileNav.classList.add("hidden");

    updateMobileMenuIcon();

}


/* =========================================================
   MOBILE MENU ICON
========================================================= */

function updateMobileMenuIcon() {

    const mobileNav =
        document.getElementById("mobileNav");

    const openIcon =
        document.getElementById(
            "mobileMenuOpenIcon"
        );

    const closeIcon =
        document.getElementById(
            "mobileMenuCloseIcon"
        );

    if (
        !mobileNav ||
        !openIcon ||
        !closeIcon
    ) {
        return;
    }

    const isHidden =
        mobileNav.classList.contains("hidden");

    openIcon.classList.toggle(
        "hidden",
        !isHidden
    );

    closeIcon.classList.toggle(
        "hidden",
        isHidden
    );

}


/* =========================================================
   DOCUMENT CLICK HANDLER
========================================================= */

document.addEventListener("click", function (event) {

    /*
     * If user clicks inside a dropdown,
     * don't immediately close it.
     */
    const dropdown =
        event.target.closest(
            '[id$="Dropdown"]'
        );

    if (dropdown) {

        /*
         * Links inside dropdowns should
         * navigate normally.
         */
        if (event.target.closest("a")) {

            return;

        }

        event.stopPropagation();

        return;

    }


    /*
     * Don't close the dropdown when clicking
     * the button that opened it.
     */
    const dropdownButton =
        event.target.closest(
            "[data-dropdown-button]"
        );

    if (dropdownButton) {

        return;

    }


    closeAllDropdowns();

});


/* =========================================================
   MOBILE LINK CLICK
========================================================= */

document.addEventListener("click", function (event) {

    const mobileLink =
        event.target.closest(
            "#mobileNav a"
        );

    if (!mobileLink) {
        return;
    }

    closeMobileNav();

});


/* =========================================================
   ESCAPE KEY
========================================================= */

document.addEventListener("keydown", function (event) {

    if (event.key !== "Escape") {
        return;
    }

    closeAllDropdowns();
    closeMobileNav();

});


/* =========================================================
   RESPONSIVE RESET
========================================================= */

window.addEventListener("resize", function () {

    if (window.innerWidth >= 1024) {

        closeMobileNav();

    }

});


/* =========================================================
   PAGE SHOW RESET
========================================================= */

window.addEventListener("pageshow", function () {

    closeAllDropdowns();
    updateMobileMenuIcon();

});