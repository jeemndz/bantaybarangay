document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // SIDEBAR MENU ITEMS
    // ==========================================

    const menuItems = document.querySelectorAll(
        ".sidebar-nav a.nav-item"
    );

    /*
     * Apply the active green style
     */
    function setActiveMenu(item) {

        menuItems.forEach(function (menu) {

            // Remove active styles
            menu.classList.remove(
                "bg-emerald-700",
                "text-white",
                "shadow-sm"
            );

            // Restore normal text
            menu.classList.add(
                "text-emerald-100"
            );

            // Restore normal icon color
            const icon = menu.querySelector("svg");

            if (icon) {

                icon.classList.remove(
                    "text-white",
                    "text-emerald-100"
                );

                icon.classList.add(
                    "text-emerald-300"
                );
            }

        });


        // Add active styles
        if (item) {

            item.classList.remove(
                "text-emerald-100"
            );

            item.classList.add(
                "bg-emerald-700",
                "text-white",
                "shadow-sm"
            );


            // Active icon
            const icon = item.querySelector("svg");

            if (icon) {

                icon.classList.remove(
                    "text-emerald-300"
                );

                icon.classList.add(
                    "text-emerald-100"
                );
            }

        }

    }


    // ==========================================
    // DETERMINE ACTIVE PAGE
    // ==========================================

    const currentPath = window.location.pathname;

    menuItems.forEach(function (item) {

        const href = item.getAttribute("href");

        if (!href || href === "#") {
            return;
        }

        /*
         * Create a URL so Django URLs are compared
         * correctly.
         */
        try {

            const itemUrl = new URL(
                href,
                window.location.origin
            );

            if (
                itemUrl.pathname === currentPath
            ) {

                setActiveMenu(item);

            }

        } catch (error) {

            console.warn(
                "Unable to determine sidebar URL:",
                href
            );

        }

    });


    // ==========================================
    // MENU CLICK
    // ==========================================

    menuItems.forEach(function (item) {

        item.addEventListener("click", function (event) {

            const href = this.getAttribute("href");

            /*
             * Don't activate # links.
             */
            if (!href || href === "#") {
                return;
            }

            setActiveMenu(this);

        });

    });

    
    // ==========================================
    // SETTINGS DROPDOWN
    // ==========================================

    const settingsToggle = document.querySelector(
        ".settings-toggle"
    );

    const settingsMenu = document.querySelector(
        ".settings-menu"
    );

    if (settingsToggle && settingsMenu) {

        settingsToggle.addEventListener("click", function (event) {

            event.preventDefault();

            settingsMenu.classList.toggle("hidden");

        });

    }


    // ==========================================
    // MOBILE SIDEBAR
    // ==========================================

    const sidebar = document.querySelector(".sidebar");

    const sidebarToggle = document.querySelector(
        ".sidebar-toggle"
    );

    if (sidebar && sidebarToggle) {

        sidebarToggle.addEventListener("click", function () {

            sidebar.classList.toggle("-translate-x-full");
            sidebar.classList.toggle("translate-x-0");

        });

    }


    // ==========================================
    // CLOSE MOBILE SIDEBAR
    // ==========================================

    const mainContent = document.querySelector(".main-content");

    if (mainContent && sidebar) {

        mainContent.addEventListener("click", function () {

            if (window.innerWidth < 1024) {

                sidebar.classList.remove("translate-x-0");

                sidebar.classList.add("-translate-x-full");

            }

        });

    }


    // ==========================================
    // RESPONSIVE SIDEBAR
    // ==========================================

    window.addEventListener("resize", function () {

        if (window.innerWidth >= 1024) {

            sidebar.classList.remove("-translate-x-full");

            sidebar.classList.add("translate-x-0");

        } else {

            sidebar.classList.remove("translate-x-0");

            sidebar.classList.add("-translate-x-full");

        }

    });

});