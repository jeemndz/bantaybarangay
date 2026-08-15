document.addEventListener("DOMContentLoaded", function () {

    // ==============================
    // SIDEBAR MENU ITEMS
    // ==============================

    const menuItems = document.querySelectorAll(".sidebar-menu a");

    menuItems.forEach(function (item) {

        item.addEventListener("click", function () {

            // Remove active state from all menu items
            menuItems.forEach(function (menu) {
                menu.classList.remove("active");
            });

            // Add active state to clicked item
            this.classList.add("active");

        });

    });


    // ==============================
    // SETTINGS DROPDOWN
    // ==============================

    const settingsToggle = document.querySelector(".settings-toggle");
    const settingsMenu = document.querySelector(".settings-menu");

    if (settingsToggle && settingsMenu) {

        settingsToggle.addEventListener("click", function (event) {

            event.preventDefault();

            settingsMenu.classList.toggle("show");

        });

    }


    // ==============================
    // MOBILE SIDEBAR
    // ==============================

    const sidebar = document.querySelector(".sidebar");
    const sidebarToggle = document.querySelector(".sidebar-toggle");

    if (sidebar && sidebarToggle) {

        sidebarToggle.addEventListener("click", function () {

            sidebar.classList.toggle("sidebar-open");

        });

    }


    // ==============================
    // CLOSE MOBILE SIDEBAR
    // WHEN CLICKING MAIN CONTENT
    // ==============================

    const mainContent = document.querySelector(".main-content");

    if (mainContent && sidebar) {

        mainContent.addEventListener("click", function () {

            if (window.innerWidth <= 700) {
                sidebar.classList.remove("sidebar-open");
            }

        });

    }

});