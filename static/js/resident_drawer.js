document.addEventListener("DOMContentLoaded", function () {

    console.log("BantayBarangay resident JS loaded");


    /* ========================================================
       RESIDENT DRAWER ELEMENTS
    ======================================================== */

    const drawer =
        document.getElementById("residentDrawer");

    const drawerOverlay =
        document.getElementById("residentDrawerOverlay");

    const closeDrawerTop =
        document.getElementById("closeResidentDrawer");

    const closeDrawerBottom =
        document.getElementById("closeResidentDrawerFooter");

    const drawerEditButton =
        document.getElementById("drawerEditResident");

    const residentRows =
        document.querySelectorAll(".resident-row");


    /* ========================================================
       DRAWER FIELDS
    ======================================================== */

    const drawerFields = {

        id:
            document.getElementById(
                "drawerResidentId"
            ),

        name:
            document.getElementById(
                "drawerResidentName"
            ),

        gender:
            document.getElementById(
                "drawerResidentGender"
            ),

        birthdate:
            document.getElementById(
                "drawerResidentBirthdate"
            ),

        address:
            document.getElementById(
                "drawerResidentAddress"
            ),

        barangay:
            document.getElementById(
                "drawerResidentBarangay"
            ),

        city:
            document.getElementById(
                "drawerResidentCity"
            ),

        contact:
            document.getElementById(
                "drawerResidentContact"
            ),

        email:
            document.getElementById(
                "drawerResidentEmail"
            ),

        status:
            document.getElementById(
                "drawerResidentStatus"
            ),

        created:
            document.getElementById(
                "drawerResidentCreated"
            )

    };


    /* ========================================================
       INACTIVE MODAL ELEMENTS
    ======================================================== */

    const inactiveModal =
        document.getElementById(
            "inactiveResidentModal"
        );

    const inactiveModalCard =
        document.getElementById(
            "inactiveResidentModalCard"
        );

    const inactiveResidentName =
        document.getElementById(
            "inactiveResidentName"
        );

    const cancelInactiveButton =
        document.getElementById(
            "cancelInactiveResident"
        );

    const confirmInactiveButton =
        document.getElementById(
            "confirmInactiveResident"
        );

    const inactiveButtons =
        document.querySelectorAll(
            "[data-inactive-resident]"
        );


    /* ========================================================
       SEARCH
    ======================================================== */

    const searchInput =
        document.getElementById(
            "residentSearch"
        );


    /* ========================================================
       STATE
    ======================================================== */

    let drawerIsOpen = false;

    let inactiveModalIsOpen = false;

    let activeResidentRow = null;

    let selectedInactiveResidentId = null;

    let selectedInactiveButton = null;


    /* ========================================================
       DEBUG INFORMATION
    ======================================================== */

    console.log(
        "Drawer:",
        drawer
    );

    console.log(
        "Drawer overlay:",
        drawerOverlay
    );

    console.log(
        "Resident rows found:",
        residentRows.length
    );


    /* ========================================================
       VALUE HELPER
    ======================================================== */

    function cleanValue(value) {

        if (
            value === undefined ||
            value === null ||
            value === "" ||
            value === "None" ||
            value === "null" ||
            value === "undefined"
        ) {

            return "—";

        }

        return String(value).trim() || "—";

    }


    /* ========================================================
       SET FIELD TEXT
    ======================================================== */

    function setField(element, value) {

        if (!element) {
            return;
        }

        element.textContent =
            cleanValue(value);

    }


    /* ========================================================
       UPDATE DRAWER STATUS BADGE
    ======================================================== */

    function updateStatusBadge(status) {

        if (!drawerFields.status) {
            return;
        }


        const statusValue =
            cleanValue(status);

        const normalizedStatus =
            statusValue.toLowerCase();


        drawerFields.status.textContent =
            statusValue;


        /*
         * Reset all Tailwind status styles.
         */

        drawerFields.status.className =
            "inline-flex items-center rounded-full " +
            "px-3 py-1 text-xs font-semibold";


        /* VERIFIED */

        if (normalizedStatus === "verified") {

            drawerFields.status.classList.add(
                "bg-emerald-100",
                "text-emerald-700"
            );

            return;

        }


        /* PENDING */

        if (
            normalizedStatus === "pending" ||
            normalizedStatus === "pending review"
        ) {

            drawerFields.status.classList.add(
                "bg-amber-100",
                "text-amber-700"
            );

            return;

        }


        /* REJECTED */

        if (normalizedStatus === "rejected") {

            drawerFields.status.classList.add(
                "bg-red-100",
                "text-red-700"
            );

            return;

        }


        /* INACTIVE */

        if (normalizedStatus === "inactive") {

            drawerFields.status.classList.add(
                "bg-slate-200",
                "text-slate-700"
            );

            return;

        }


        /* DEFAULT */

        drawerFields.status.classList.add(
            "bg-slate-100",
            "text-slate-700"
        );

    }


    /* ========================================================
       POPULATE DRAWER
    ======================================================== */

    function populateDrawer(row) {

        if (!row) {
            return;
        }


        const data =
            row.dataset;


        setField(
            drawerFields.id,
            data.residentId
        );


        setField(
            drawerFields.name,
            data.name
        );


        setField(
            drawerFields.gender,
            data.gender
        );


        setField(
            drawerFields.birthdate,
            data.birthdate
        );


        setField(
            drawerFields.address,
            data.address
        );


        setField(
            drawerFields.barangay,
            data.barangay
        );


        setField(
            drawerFields.city,
            data.city
        );


        setField(
            drawerFields.contact,
            data.contact
        );


        setField(
            drawerFields.email,
            data.email
        );


        updateStatusBadge(
            data.status
        );


        setField(
            drawerFields.created,
            data.created
        );


        /* EDIT URL */

        if (drawerEditButton) {

            if (data.editUrl) {

                drawerEditButton.href =
                    data.editUrl;


                drawerEditButton.classList.remove(
                    "pointer-events-none",
                    "opacity-50"
                );


                drawerEditButton.removeAttribute(
                    "aria-disabled"
                );

            } else {

                drawerEditButton.href = "#";


                drawerEditButton.classList.add(
                    "pointer-events-none",
                    "opacity-50"
                );


                drawerEditButton.setAttribute(
                    "aria-disabled",
                    "true"
                );

            }

        }

    }


    /* ========================================================
       OPEN DRAWER
    ======================================================== */

    function openDrawer(row) {

        if (!drawer) {

            console.error(
                "Cannot open drawer: #residentDrawer not found."
            );

            return;

        }


        if (!drawerOverlay) {

            console.error(
                "Cannot open drawer: #residentDrawerOverlay not found."
            );

            return;

        }


        if (!row) {
            return;
        }


        console.log(
            "Opening resident:",
            row.dataset.residentId
        );


        activeResidentRow = row;

        drawerIsOpen = true;


        /* Populate resident information */

        populateDrawer(row);


        /* -----------------------------------------
           SHOW OVERLAY
        ----------------------------------------- */

        drawerOverlay.classList.remove(
            "invisible",
            "opacity-0"
        );


        drawerOverlay.classList.add(
            "visible",
            "opacity-100"
        );


        drawerOverlay.setAttribute(
            "aria-hidden",
            "false"
        );


        /* -----------------------------------------
           SHOW DRAWER
        ----------------------------------------- */

        drawer.classList.remove(
            "translate-x-full"
        );


        drawer.classList.add(
            "translate-x-0"
        );


        drawer.setAttribute(
            "aria-hidden",
            "false"
        );


        /* -----------------------------------------
           LOCK BACKGROUND
        ----------------------------------------- */

        document.body.classList.add(
            "overflow-hidden"
        );


        /* -----------------------------------------
           FOCUS CLOSE BUTTON
        ----------------------------------------- */

        window.setTimeout(
            function () {

                if (closeDrawerTop) {
                    closeDrawerTop.focus();
                }

            },
            100
        );

    }


    /* ========================================================
       CLOSE DRAWER
    ======================================================== */

    function closeDrawer() {

        if (!drawer) {
            return;
        }


        if (!drawerIsOpen) {
            return;
        }


        drawerIsOpen = false;


        /* -----------------------------------------
           HIDE DRAWER
        ----------------------------------------- */

        drawer.classList.remove(
            "translate-x-0"
        );


        drawer.classList.add(
            "translate-x-full"
        );


        drawer.setAttribute(
            "aria-hidden",
            "true"
        );


        /* -----------------------------------------
           HIDE OVERLAY
        ----------------------------------------- */

        if (drawerOverlay) {

            drawerOverlay.classList.remove(
                "visible",
                "opacity-100"
            );


            drawerOverlay.classList.add(
                "invisible",
                "opacity-0"
            );


            drawerOverlay.setAttribute(
                "aria-hidden",
                "true"
            );

        }


        /* -----------------------------------------
           UNLOCK PAGE
        ----------------------------------------- */

        if (!inactiveModalIsOpen) {

            document.body.classList.remove(
                "overflow-hidden"
            );

        }


        /* -----------------------------------------
           RESTORE FOCUS
        ----------------------------------------- */

        const previousRow =
            activeResidentRow;


        activeResidentRow = null;


        window.setTimeout(
            function () {

                if (previousRow) {
                    previousRow.focus();
                }

            },
            300
        );

    }


    /* ========================================================
       INTERACTIVE ELEMENT CHECK
    ======================================================== */

    function isInteractiveElement(target) {

        if (!(target instanceof Element)) {
            return false;
        }


        return Boolean(

            target.closest(
                "a, button, input, select, " +
                "textarea, label, [data-prevent-drawer]"
            )

        );

    }


    /* ========================================================
       RESIDENT ROW EVENTS
    ======================================================== */

    residentRows.forEach(
        function (row) {


            /* -----------------------------------------
               CLICK
            ----------------------------------------- */

            row.addEventListener(
                "click",
                function (event) {


                    /*
                     * Do not open drawer when clicking
                     * Edit, Inactive, or another control.
                     */

                    if (
                        isInteractiveElement(
                            event.target
                        )
                    ) {

                        return;

                    }


                    openDrawer(row);

                }
            );


            /* -----------------------------------------
               KEYBOARD
            ----------------------------------------- */

            row.addEventListener(
                "keydown",
                function (event) {


                    if (
                        event.key !== "Enter" &&
                        event.key !== " "
                    ) {

                        return;

                    }


                    if (
                        isInteractiveElement(
                            event.target
                        )
                    ) {

                        return;

                    }


                    event.preventDefault();


                    openDrawer(row);

                }
            );

        }
    );


    /* ========================================================
       DRAWER CLOSE BUTTONS
    ======================================================== */

    if (closeDrawerTop) {

        closeDrawerTop.addEventListener(
            "click",
            closeDrawer
        );

    }


    if (closeDrawerBottom) {

        closeDrawerBottom.addEventListener(
            "click",
            closeDrawer
        );

    }


    /* ========================================================
       DRAWER OVERLAY
    ======================================================== */

    if (drawerOverlay) {

        drawerOverlay.addEventListener(
            "click",
            closeDrawer
        );

    }


    /* ========================================================
       SEARCH RESIDENTS
    ======================================================== */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            function () {


                const query =
                    searchInput.value
                        .trim()
                        .toLowerCase();


                residentRows.forEach(
                    function (row) {


                        const searchableValues = [

                            row.dataset.residentId,

                            row.dataset.name,

                            row.dataset.gender,

                            row.dataset.address,

                            row.dataset.barangay,

                            row.dataset.city,

                            row.dataset.contact,

                            row.dataset.email,

                            row.dataset.status

                        ];


                        const searchableText =
                            searchableValues
                                .map(
                                    function (value) {

                                        return (
                                            value || ""
                                        ).toLowerCase();

                                    }
                                )
                                .join(" ");


                        const matches =
                            searchableText.includes(
                                query
                            );


                        row.style.display =
                            matches
                                ? ""
                                : "none";

                    }
                );

            }
        );

    }


    /* ========================================================
       OPEN INACTIVE MODAL
    ======================================================== */

    function openInactiveModal(button) {

        if (!inactiveModal) {

            console.error(
                "Inactive modal was not found."
            );

            return;

        }


        selectedInactiveButton =
            button;


        selectedInactiveResidentId =
            button.dataset.residentId || null;


        const residentName =
            button.dataset.residentName ||
            "this resident";


        if (inactiveResidentName) {

            inactiveResidentName.textContent =
                residentName;

        }


        inactiveModalIsOpen = true;


        /* -----------------------------------------
           SHOW MODAL BACKDROP
        ----------------------------------------- */

        inactiveModal.classList.remove(
            "invisible",
            "opacity-0"
        );


        inactiveModal.classList.add(
            "visible",
            "opacity-100"
        );


        inactiveModal.setAttribute(
            "aria-hidden",
            "false"
        );


        /* -----------------------------------------
           SHOW MODAL CARD
        ----------------------------------------- */

        if (inactiveModalCard) {

            inactiveModalCard.classList.remove(
                "scale-95",
                "opacity-0"
            );


            inactiveModalCard.classList.add(
                "scale-100",
                "opacity-100"
            );

        }


        document.body.classList.add(
            "overflow-hidden"
        );


        window.setTimeout(
            function () {

                if (cancelInactiveButton) {
                    cancelInactiveButton.focus();
                }

            },
            100
        );

    }


    /* ========================================================
       CLOSE INACTIVE MODAL
    ======================================================== */

    function closeInactiveModal() {

        if (!inactiveModal) {
            return;
        }


        inactiveModalIsOpen = false;


        /* -----------------------------------------
           HIDE MODAL CARD
        ----------------------------------------- */

        if (inactiveModalCard) {

            inactiveModalCard.classList.remove(
                "scale-100",
                "opacity-100"
            );


            inactiveModalCard.classList.add(
                "scale-95",
                "opacity-0"
            );

        }


        /* -----------------------------------------
           HIDE BACKDROP
        ----------------------------------------- */

        inactiveModal.classList.remove(
            "visible",
            "opacity-100"
        );


        inactiveModal.classList.add(
            "invisible",
            "opacity-0"
        );


        inactiveModal.setAttribute(
            "aria-hidden",
            "true"
        );


        if (!drawerIsOpen) {

            document.body.classList.remove(
                "overflow-hidden"
            );

        }


        const previousButton =
            selectedInactiveButton;


        selectedInactiveResidentId = null;

        selectedInactiveButton = null;


        window.setTimeout(
            function () {

                if (previousButton) {
                    previousButton.focus();
                }

            },
            200
        );

    }


    /* ========================================================
       INACTIVE BUTTON EVENTS
    ======================================================== */

    inactiveButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    event.stopPropagation();


                    openInactiveModal(
                        button
                    );

                }
            );

        }
    );


    /* ========================================================
       CANCEL INACTIVE
    ======================================================== */

    if (cancelInactiveButton) {

        cancelInactiveButton.addEventListener(
            "click",
            closeInactiveModal
        );

    }


    /* ========================================================
       CLICK OUTSIDE INACTIVE MODAL
    ======================================================== */

    if (inactiveModal) {

        inactiveModal.addEventListener(
            "click",
            function (event) {

                if (
                    event.target === inactiveModal
                ) {

                    closeInactiveModal();

                }

            }
        );

    }


    /* ========================================================
       CONFIRM INACTIVE
    ======================================================== */

    if (confirmInactiveButton) {

        confirmInactiveButton.addEventListener(
            "click",
            function () {


                if (!selectedInactiveResidentId) {
                    return;
                }


                /*
                =================================================
                BACKEND CONNECTION GOES HERE
                =================================================

                Right now this is intentionally UI-only.

                DO NOT call your resident_delete endpoint here.

                Once you create a Django URL such as:

                    resident_inactive

                this section can POST to that endpoint and
                update the resident without deleting the record.
                */


                console.log(
                    "Inactive requested for resident:",
                    selectedInactiveResidentId
                );


                closeInactiveModal();

            }
        );

    }


    /* ========================================================
       GLOBAL ESCAPE KEY
    ======================================================== */

    document.addEventListener(
        "keydown",
        function (event) {


            if (event.key !== "Escape") {
                return;
            }


            /*
             * Modal has priority if it is open.
             */

            if (inactiveModalIsOpen) {

                closeInactiveModal();

                return;

            }


            if (drawerIsOpen) {

                closeDrawer();

            }

        }
    );


    /* ========================================================
       OPTIONAL GLOBAL DRAWER API
    ======================================================== */

    window.BantayBarangayResidentDrawer = {

        open:
            function (row) {

                openDrawer(row);

            },

        close:
            function () {

                closeDrawer();

            },

        isOpen:
            function () {

                return drawerIsOpen;

            }

    };


    /* ========================================================
       INITIAL CHECK
    ======================================================== */

    if (!drawer) {

        console.error(
            "Resident drawer error: " +
            "#residentDrawer does not exist."
        );

    }


    if (!drawerOverlay) {

        console.error(
            "Resident drawer error: " +
            "#residentDrawerOverlay does not exist."
        );

    }

});