/* =========================================================
   BANTAYBARANGAY
   DOCUMENT REQUEST & ISSUANCE
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeDocumentRequestModule();

    }
);


/* =========================================================
   INITIALIZE MODULE
========================================================= */

function initializeDocumentRequestModule() {

    initializeRequestRows();

    initializeFilters();

    initializeDateFilters();

    initializeRefreshButton();

    initializeAutoRefreshCountdown();

    initializeDocumentActions();

    initializePagination();

}


/* =========================================================
   REQUEST ROWS
========================================================= */

function initializeRequestRows() {

    const rows =
        document.querySelectorAll(
            ".dr-request-row"
        );

    rows.forEach(function (row) {

        row.addEventListener(
            "click",
            function (event) {

                /*
                 * Do not select the row when one of the
                 * action buttons is clicked.
                 */
                if (
                    event.target.closest(
                        ".dr-action-btn"
                    )
                ) {
                    return;
                }

                selectRequestRow(row);

            }
        );


        const viewButton =
            row.querySelector(
                ".dr-view-btn"
            );


        if (viewButton) {

            viewButton.addEventListener(
                "click",
                function (event) {

                    event.stopPropagation();

                    selectRequestRow(row);

                }
            );

        }

    });

}


/* =========================================================
   SELECT REQUEST
========================================================= */

function selectRequestRow(row) {

    if (!row) {
        return;
    }


    document
        .querySelectorAll(
            ".dr-request-row"
        )
        .forEach(function (item) {

            item.classList.remove(
                "selected"
            );

        });


    row.classList.add(
        "selected"
    );


    updateDossier(row);

}


/* =========================================================
   UPDATE DOSSIER
========================================================= */

function updateDossier(row) {

    const requestNumber =
        row.dataset.request || "";

    const residentName =
        row.dataset.name || "";

    const documentName =
        row.dataset.document || "";

    const received =
        row.dataset.received || "";

    const address =
        row.dataset.address || "";

    const residentId =
        row.dataset.id || "";

    const voter =
        row.dataset.voter || "";

    const fee =
        row.dataset.fee || "";


    setText(
        "detailRequest",
        requestNumber
    );


    setText(
        "detailReceived",
        "Received: " + received
    );


    setText(
        "detailName",
        residentName
    );


    setText(
        "detailId",
        residentId
    );


    setText(
        "detailVoter",
        voter
    );


    setText(
        "detailFee",
        fee
    );


    setText(
        "previewResidentName",
        residentName.toUpperCase()
    );


    setText(
        "previewAddress",
        address
    );


    setText(
        "previewDocumentTitle",
        documentName.toUpperCase()
    );


    setText(
        "detailAvatar",
        getInitials(
            residentName
        )
    );

}


/* =========================================================
   SET TEXT
========================================================= */

function setText(id, value) {

    const element =
        document.getElementById(id);


    if (!element) {
        return;
    }


    element.textContent = value;

}


/* =========================================================
   GET INITIALS
========================================================= */

function getInitials(name) {

    if (!name) {
        return "--";
    }


    const parts =
        name
            .trim()
            .split(/\s+/)
            .filter(Boolean);


    if (parts.length === 1) {

        return parts[0]
            .substring(0, 2)
            .toUpperCase();

    }


    return (
        parts[0][0] +
        parts[parts.length - 1][0]
    ).toUpperCase();

}


/* =========================================================
   FILTERS
========================================================= */

function initializeFilters() {

    const categoryFilter =
        document.getElementById(
            "categoryFilter"
        );

    const statusFilter =
        document.getElementById(
            "statusFilter"
        );

    const flaggedFilter =
        document.getElementById(
            "flaggedFilter"
        );


    if (categoryFilter) {

        categoryFilter.addEventListener(
            "change",
            applyRequestFilters
        );

    }


    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            applyRequestFilters
        );

    }


    if (flaggedFilter) {

        flaggedFilter.addEventListener(
            "change",
            applyRequestFilters
        );

    }

}


/* =========================================================
   APPLY FILTERS
========================================================= */

function applyRequestFilters() {

    const categoryFilter =
        document.getElementById(
            "categoryFilter"
        );

    const statusFilter =
        document.getElementById(
            "statusFilter"
        );

    const flaggedFilter =
        document.getElementById(
            "flaggedFilter"
        );


    const category =
        categoryFilter
            ? categoryFilter.value
            : "all";


    const status =
        statusFilter
            ? statusFilter.value
            : "all";


    const flaggedOnly =
        flaggedFilter
            ? flaggedFilter.checked
            : false;


    const rows =
        document.querySelectorAll(
            ".dr-request-row"
        );


    let visibleCount = 0;


    rows.forEach(function (row) {

        const rowCategory =
            row.dataset.category;

        const rowStatus =
            row.dataset.status;

        const rowFlagged =
            row.dataset.flagged === "true";


        const categoryMatch =
            category === "all" ||
            category === rowCategory;


        const statusMatch =
            status === "all" ||
            status === rowStatus;


        const flaggedMatch =
            !flaggedOnly ||
            rowFlagged;


        const visible =
            categoryMatch &&
            statusMatch &&
            flaggedMatch;


        if (visible) {

            row.style.display = "";

            visibleCount++;

        } else {

            row.style.display = "none";

            row.classList.remove(
                "selected"
            );

        }

    });


    updateVisibleCount(
        visibleCount
    );


    updateEmptyFilterMessage(
        visibleCount
    );


    ensureVisibleSelectedRow();

}


/* =========================================================
   VISIBLE COUNT
========================================================= */

function updateVisibleCount(count) {

    const element =
        document.getElementById(
            "visibleCount"
        );


    if (element) {

        element.textContent = count;

    }

}


/* =========================================================
   EMPTY FILTER MESSAGE
========================================================= */

function updateEmptyFilterMessage(count) {

    const tbody =
        document.getElementById(
            "requestTableBody"
        );


    if (!tbody) {
        return;
    }


    const existing =
        tbody.querySelector(
            ".dr-empty-row"
        );


    if (existing) {

        existing.remove();

    }


    if (count > 0) {
        return;
    }


    const row =
        document.createElement(
            "tr"
        );


    row.className =
        "dr-empty-row";


    row.innerHTML = `
        <td colspan="8">
            <i class="fa-regular fa-folder-open"></i>
            &nbsp;
            No document requests match the selected filters.
        </td>
    `;


    tbody.appendChild(row);

}


/* =========================================================
   SELECT FIRST VISIBLE ROW
========================================================= */

function ensureVisibleSelectedRow() {

    const selected =
        document.querySelector(
            ".dr-request-row.selected"
        );


    if (
        selected &&
        selected.style.display !== "none"
    ) {
        return;
    }


    const rows =
        document.querySelectorAll(
            ".dr-request-row"
        );


    for (const row of rows) {

        if (row.style.display !== "none") {

            selectRequestRow(row);

            return;

        }

    }

}


/* =========================================================
   DATE FILTERS
========================================================= */

function initializeDateFilters() {

    const buttons =
        document.querySelectorAll(
            ".dr-date-btn"
        );


    buttons.forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                buttons.forEach(
                    function (item) {

                        item.classList.remove(
                            "active"
                        );

                    }
                );


                button.classList.add(
                    "active"
                );


                /*
                 * The current page uses sample records.
                 * When connected to Django, this can submit
                 * the selected range as a GET parameter.
                 */
                const range =
                    button.dataset.dateFilter;


                console.log(
                    "Selected date filter:",
                    range
                );

            }
        );

    });

}


/* =========================================================
   REFRESH QUEUE
========================================================= */

function initializeRefreshButton() {

    const button =
        document.getElementById(
            "refreshQueueBtn"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        function () {

            button.disabled = true;


            const originalHTML =
                button.innerHTML;


            button.innerHTML = `
                <i class="fa-solid fa-arrows-rotate fa-spin"></i>
                Refreshing...
            `;


            window.setTimeout(
                function () {

                    button.disabled = false;

                    button.innerHTML =
                        originalHTML;


                    resetRefreshCountdown();


                    showDocumentToast(
                        "Queue refreshed",
                        "The document request queue has been refreshed."
                    );

                },
                900
            );

        }
    );

}


/* =========================================================
   AUTO REFRESH COUNTDOWN
========================================================= */

let documentRefreshSeconds = 24;


function initializeAutoRefreshCountdown() {

    window.setInterval(
        function () {

            documentRefreshSeconds--;


            if (
                documentRefreshSeconds <= 0
            ) {

                documentRefreshSeconds = 24;

            }


            updateRefreshCountdown();

        },
        1000
    );

}


/* =========================================================
   UPDATE COUNTDOWN
========================================================= */

function updateRefreshCountdown() {

    const element =
        document.getElementById(
            "refreshCountdown"
        );


    if (!element) {
        return;
    }


    element.textContent =
        documentRefreshSeconds + "s";

}


/* =========================================================
   RESET COUNTDOWN
========================================================= */

function resetRefreshCountdown() {

    documentRefreshSeconds = 24;

    updateRefreshCountdown();

}


/* =========================================================
   DOCUMENT ACTIONS
========================================================= */

function initializeDocumentActions() {

    const signButton =
        document.getElementById(
            "signDocumentBtn"
        );


    const printButton =
        document.getElementById(
            "printSealBtn"
        );


    const notifyButton =
        document.getElementById(
            "notifySmsBtn"
        );


    const exportButton =
        document.getElementById(
            "exportReportBtn"
        );


    const moreFiltersButton =
        document.getElementById(
            "moreFiltersBtn"
        );


    if (signButton) {

        signButton.addEventListener(
            "click",
            function () {

                const request =
                    getCurrentRequestNumber();


                showDocumentToast(
                    "Document signed",
                    request +
                    " has been marked for cryptographic signing."
                );

            }
        );

    }


    if (printButton) {

        printButton.addEventListener(
            "click",
            function () {

                const request =
                    getCurrentRequestNumber();


                showDocumentToast(
                    "Print prepared",
                    request +
                    " is ready for printing and sealing."
                );

            }
        );

    }


    if (notifyButton) {

        notifyButton.addEventListener(
            "click",
            function () {

                const name =
                    getCurrentResidentName();


                showDocumentToast(
                    "SMS notification",
                    "Notification prepared for " +
                    name +
                    "."
                );

            }
        );

    }


    if (exportButton) {

        exportButton.addEventListener(
            "click",
            function () {

                showDocumentToast(
                    "DILG report",
                    "Report export has been prepared."
                );

            }
        );

    }


    if (moreFiltersButton) {

        moreFiltersButton.addEventListener(
            "click",
            function () {

                showDocumentToast(
                    "Filters",
                    "Additional filters can be connected here."
                );

            }
        );

    }

}


/* =========================================================
   CURRENT REQUEST
========================================================= */

function getCurrentRequestNumber() {

    const element =
        document.getElementById(
            "detailRequest"
        );


    if (!element) {
        return "Selected document";
    }


    return element.textContent.trim();

}


/* =========================================================
   CURRENT RESIDENT
========================================================= */

function getCurrentResidentName() {

    const element =
        document.getElementById(
            "detailName"
        );


    if (!element) {
        return "the resident";
    }


    return element.textContent.trim();

}


/* =========================================================
   PAGINATION
========================================================= */

function initializePagination() {

    const buttons =
        document.querySelectorAll(
            ".dr-pagination button"
        );


    buttons.forEach(function (button) {

        button.addEventListener(
            "click",
            function () {

                const value =
                    button.textContent.trim();


                if (
                    value !== "1" &&
                    value !== "2" &&
                    value !== "3"
                ) {
                    return;
                }


                buttons.forEach(
                    function (item) {

                        if (
                            ["1", "2", "3"].includes(
                                item.textContent.trim()
                            )
                        ) {

                            item.classList.remove(
                                "active"
                            );

                        }

                    }
                );


                button.classList.add(
                    "active"
                );

            }
        );

    });

}


/* =========================================================
   TOAST
========================================================= */

let documentToastTimer = null;


function showDocumentToast(
    title,
    message
) {

    const toast =
        document.getElementById(
            "documentToast"
        );


    const titleElement =
        document.getElementById(
            "toastTitle"
        );


    const messageElement =
        document.getElementById(
            "toastMessage"
        );


    if (
        !toast ||
        !titleElement ||
        !messageElement
    ) {
        return;
    }


    titleElement.textContent =
        title;


    messageElement.textContent =
        message;


    toast.classList.add(
        "show"
    );


    if (documentToastTimer) {

        window.clearTimeout(
            documentToastTimer
        );

    }


    documentToastTimer =
        window.setTimeout(
            function () {

                toast.classList.remove(
                    "show"
                );

            },
            3500
        );

}