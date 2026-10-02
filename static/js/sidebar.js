document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // ELEMENTS
    // =========================================================

    const sidebar =
        document.getElementById("sidebar");

    const sidebarToggle =
        document.getElementById("sidebarToggle");

    const sidebarClose =
        document.getElementById("sidebarClose");

    const sidebarBackdrop =
        document.getElementById("sidebarBackdrop");

    const mainContent =
        document.querySelector(".main-content");


    // =========================================================
    // MOBILE BREAKPOINT
    // =========================================================

    const MOBILE_BREAKPOINT = 1024;


    function isMobile() {

        return window.innerWidth < MOBILE_BREAKPOINT;

    }


    // =========================================================
    // OPEN SIDEBAR
    // =========================================================

    function openSidebar() {

        if (!sidebar || !isMobile()) {
            return;
        }


        sidebar.classList.add(
            "sidebar-open"
        );


        if (sidebarBackdrop) {

            sidebarBackdrop.classList.add(
                "show"
            );

            sidebarBackdrop.setAttribute(
                "aria-hidden",
                "false"
            );

        }


        if (sidebarToggle) {

            sidebarToggle.setAttribute(
                "aria-expanded",
                "true"
            );

            sidebarToggle.setAttribute(
                "aria-label",
                "Close navigation menu"
            );

        }


        document.body.classList.add(
            "sidebar-is-open"
        );


        document.body.style.overflow =
            "hidden";

    }


    // =========================================================
    // CLOSE SIDEBAR
    // =========================================================

    function closeSidebar() {

        if (!sidebar) {
            return;
        }


        sidebar.classList.remove(
            "sidebar-open"
        );


        if (sidebarBackdrop) {

            sidebarBackdrop.classList.remove(
                "show"
            );

            sidebarBackdrop.setAttribute(
                "aria-hidden",
                "true"
            );

        }


        if (sidebarToggle) {

            sidebarToggle.setAttribute(
                "aria-expanded",
                "false"
            );

            sidebarToggle.setAttribute(
                "aria-label",
                "Open navigation menu"
            );

        }


        document.body.classList.remove(
            "sidebar-is-open"
        );


        document.body.style.overflow =
            "";

    }


    // =========================================================
    // TOGGLE SIDEBAR
    // =========================================================

    function toggleSidebar() {

        if (!sidebar || !isMobile()) {
            return;
        }


        if (
            sidebar.classList.contains(
                "sidebar-open"
            )
        ) {

            closeSidebar();

        } else {

            openSidebar();

        }

    }


    // =========================================================
    // OPEN / CLOSE BUTTON
    // =========================================================

    if (sidebarToggle) {

        sidebarToggle.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                toggleSidebar();

            }
        );

    }


    if (sidebarClose) {

        sidebarClose.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                closeSidebar();

            }
        );

    }


    // =========================================================
    // BACKDROP
    // =========================================================

    if (sidebarBackdrop) {

        sidebarBackdrop.addEventListener(
            "click",
            function () {

                closeSidebar();

            }
        );

    }


    // =========================================================
    // SIDEBAR MENU ITEMS
    // =========================================================

    const menuItems =
        document.querySelectorAll(
            ".sidebar-nav a.nav-item"
        );


    // =========================================================
    // ACTIVE MENU
    // =========================================================

    function setActiveMenu(item) {

        menuItems.forEach(
            function (menu) {

                menu.classList.remove(
                    "active"
                );


                /*
                 * Remove active Tailwind classes
                 * if another stylesheet added them.
                 */

                menu.classList.remove(
                    "bg-emerald-700",
                    "text-white",
                    "shadow-sm"
                );


                menu.classList.add(
                    "text-emerald-100"
                );


                const icon =
                    menu.querySelector(
                        "svg"
                    );


                if (icon) {

                    icon.classList.remove(
                        "text-white",
                        "text-emerald-100"
                    );

                    icon.classList.add(
                        "text-emerald-300"
                    );

                }

            }
        );


        if (!item) {
            return;
        }


        item.classList.remove(
            "text-emerald-100"
        );


        item.classList.add(
            "active"
        );


        const icon =
            item.querySelector(
                "svg"
            );


        if (icon) {

            icon.classList.remove(
                "text-emerald-300"
            );

            icon.classList.add(
                "text-white"
            );

        }

    }


    // =========================================================
    // DETERMINE ACTIVE PAGE
    // =========================================================

    const currentPath =
        window.location.pathname;


    let activeItem = null;


    menuItems.forEach(
        function (item) {

            const href =
                item.getAttribute(
                    "href"
                );


            if (
                !href ||
                href === "#"
            ) {

                return;

            }


            try {

                const itemUrl =
                    new URL(
                        href,
                        window.location.origin
                    );


                if (
                    itemUrl.pathname ===
                    currentPath
                ) {

                    activeItem = item;

                }

            } catch (error) {

                console.warn(
                    "Unable to determine sidebar URL:",
                    href
                );

            }

        }
    );


    if (activeItem) {

        setActiveMenu(
            activeItem
        );

    }


    // =========================================================
    // MENU CLICK
    // =========================================================

    menuItems.forEach(
        function (item) {

            item.addEventListener(
                "click",
                function () {

                    const href =
                        this.getAttribute(
                            "href"
                        );


                    if (
                        !href ||
                        href === "#"
                    ) {

                        return;

                    }


                    setActiveMenu(
                        this
                    );


                    /*
                     * Automatically close the
                     * mobile sidebar after navigation.
                     */

                    if (isMobile()) {

                        closeSidebar();

                    }

                }
            );

        }
    );


    // =========================================================
    // SETTINGS DROPDOWN
    // =========================================================

    const settingsToggle =
        document.getElementById(
            "settingsMenuButton"
        );

    const settingsMenu =
        document.getElementById(
            "settingsSubmenu"
        );

    const settingsArrow =
        document.getElementById(
            "settingsMenuArrow"
        );


    if (
        settingsToggle &&
        settingsMenu &&
        settingsArrow
    ) {


        let settingsOpen =
            settingsToggle.getAttribute(
                "aria-expanded"
            ) === "true";


        function updateSettingsMenu() {

            settingsToggle.setAttribute(
                "aria-expanded",
                settingsOpen
                    ? "true"
                    : "false"
            );


            if (settingsOpen) {

                settingsMenu.classList.add(
                    "is-open"
                );


                settingsArrow.classList.add(
                    "rotate"
                );

            } else {

                settingsMenu.classList.remove(
                    "is-open"
                );


                settingsArrow.classList.remove(
                    "rotate"
                );

            }

        }


        settingsToggle.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                settingsOpen =
                    !settingsOpen;

                updateSettingsMenu();

            }
        );


        updateSettingsMenu();

    }


    // =========================================================
    // CLOSE WHEN CLICKING MAIN CONTENT
    // =========================================================

    if (mainContent) {

        mainContent.addEventListener(
            "click",
            function () {

                if (isMobile()) {

                    closeSidebar();

                }

            }
        );

    }


    // =========================================================
    // ESCAPE KEY
    // =========================================================

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                isMobile() &&
                sidebar &&
                sidebar.classList.contains(
                    "sidebar-open"
                )
            ) {

                closeSidebar();

            }

        }
    );


    // =========================================================
    // WINDOW RESIZE
    // =========================================================

    let previousMobileState =
        isMobile();


    window.addEventListener(
        "resize",
        function () {

            const currentMobileState =
                isMobile();


            /*
             * Only reset the sidebar when
             * crossing the desktop/mobile
             * breakpoint.
             */

            if (
                previousMobileState !==
                currentMobileState
            ) {

                if (!currentMobileState) {

                    /*
                     * Desktop
                     */

                    closeSidebar();

                } else {

                    /*
                     * Mobile
                     */

                    closeSidebar();

                }

            }


            previousMobileState =
                currentMobileState;

        }
    );


    // =========================================================
    // INITIAL STATE
    // =========================================================

    if (isMobile()) {

        closeSidebar();

    } else {

        if (sidebar) {

            sidebar.classList.remove(
                "sidebar-open"
            );

        }


        if (sidebarBackdrop) {

            sidebarBackdrop.classList.remove(
                "show"
            );

        }


        document.body.style.overflow =
            "";

    }

});