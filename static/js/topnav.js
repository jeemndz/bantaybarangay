/* =========================================================
   BANTAYBARANGAY TOPNAV
========================================================= */


/* =========================================================
   DROPDOWN
========================================================= */

function toggleDropdown(id) {

    const dropdown = document.getElementById(id);

    if (!dropdown) {
        return;
    }

    // Close other dropdowns
    document.querySelectorAll('[id$="Dropdown"]').forEach(function(menu) {

        if (menu.id !== id) {
            menu.classList.add("hidden");
        }

    });

    // Toggle selected dropdown
    dropdown.classList.toggle("hidden");

}


/* =========================================================
   MOBILE NAVIGATION
========================================================= */

function toggleMobileNav() {

    const mobileNav =
        document.getElementById("mobileNav");

    if (!mobileNav) {
        return;
    }

    mobileNav.classList.toggle("hidden");

}


/* =========================================================
   CLOSE DROPDOWNS WHEN CLICKING OUTSIDE
========================================================= */

document.addEventListener("click", function(event) {

    const clickedButton =
        event.target.closest("button");

    const clickedDropdown =
        event.target.closest('[id$="Dropdown"]');

    if (
        !clickedButton &&
        !clickedDropdown
    ) {

        document
            .querySelectorAll('[id$="Dropdown"]')
            .forEach(function(menu) {

                menu.classList.add("hidden");

            });

    }

});