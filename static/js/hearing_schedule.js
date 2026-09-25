/* =========================================================
   BANTAYBARANGAY
   HEARING SCHEDULE MODULE
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeHearingCalendar();

        initializeHearingViewTabs();

        initializeHearingFilters();

        initializeHearingModal();

        initializeHearingPagination();

        initializeHearingHeaderActions();

        initializeHearingTableActions();

    }
);


/* =========================================================
   HEARING CALENDAR STATE
========================================================= */

let hearingSelectedDate =
    new Date(
        2024,
        9,
        24
    );


let hearingCurrentView =
    "today";


/* =========================================================
   INITIALIZE CALENDAR
========================================================= */

function initializeHearingCalendar() {

    const previousButton =
        document.getElementById(
            "previousHearingDate"
        );


    const nextButton =
        document.getElementById(
            "nextHearingDate"
        );


    updateHearingDateDisplay();


    if (previousButton) {

        previousButton.addEventListener(
            "click",
            function () {

                changeHearingDate(
                    -1
                );

            }
        );

    }


    if (nextButton) {

        nextButton.addEventListener(
            "click",
            function () {

                changeHearingDate(
                    1
                );

            }
        );

    }

}


/* =========================================================
   CHANGE CALENDAR DATE
========================================================= */

function changeHearingDate(direction) {

    if (
        hearingCurrentView ===
        "weekly"
    ) {

        hearingSelectedDate.setDate(
            hearingSelectedDate.getDate() +
            (7 * direction)
        );

    } else if (
        hearingCurrentView ===
        "monthly"
    ) {

        hearingSelectedDate.setMonth(
            hearingSelectedDate.getMonth() +
            direction
        );

    } else {

        hearingSelectedDate.setDate(
            hearingSelectedDate.getDate() +
            direction
        );

    }


    updateHearingDateDisplay();

}


/* =========================================================
   UPDATE CALENDAR LABEL
========================================================= */

function updateHearingDateDisplay() {

    const dateLabel =
        document.getElementById(
            "currentHearingDate"
        );


    if (!dateLabel) {
        return;
    }


    let formatter;


    if (
        hearingCurrentView ===
        "monthly"
    ) {

        formatter =
            new Intl.DateTimeFormat(
                "en-US",
                {
                    month: "long",
                    year: "numeric"
                }
            );

    } else {

        formatter =
            new Intl.DateTimeFormat(
                "en-US",
                {
                    weekday: "long",
                    month: "long",
                    day: "numeric",
                    year: "numeric"
                }
            );

    }


    dateLabel.textContent =
        formatter.format(
            hearingSelectedDate
        );

}


/* =========================================================
   VIEW TABS
========================================================= */

function initializeHearingViewTabs() {

    const tabs =
        document.querySelectorAll(
            ".hearing-view-tab"
        );


    tabs.forEach(
        function (tab) {

            tab.addEventListener(
                "click",
                function () {

                    tabs.forEach(
                        function (item) {

                            item.classList.remove(
                                "active"
                            );

                        }
                    );


                    tab.classList.add(
                        "active"
                    );


                    hearingCurrentView =
                        tab.dataset.hearingView ||
                        "today";


                    updateHearingDateDisplay();

                }
            );

        }
    );

}


/* =========================================================
   FILTER INITIALIZATION
========================================================= */

function initializeHearingFilters() {

    const searchInput =
        document.getElementById(
            "hearingSearchInput"
        );


    const statusFilter =
        document.getElementById(
            "hearingStatusFilter"
        );


    const chamberFilter =
        document.getElementById(
            "hearingChamberFilter"
        );


    const dateFilter =
        document.getElementById(
            "hearingDateFilter"
        );


    const resetButton =
        document.getElementById(
            "resetHearingFilters"
        );


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterHearingRecords
        );

    }


    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            filterHearingRecords
        );

    }


    if (chamberFilter) {

        chamberFilter.addEventListener(
            "change",
            filterHearingRecords
        );

    }


    if (dateFilter) {

        dateFilter.addEventListener(
            "change",
            filterHearingRecords
        );

    }


    if (resetButton) {

        resetButton.addEventListener(
            "click",
            resetHearingFilters
        );

    }


    updateHearingRecordCount();

}


/* =========================================================
   FILTER RECORDS
========================================================= */

function filterHearingRecords() {

    const searchInput =
        document.getElementById(
            "hearingSearchInput"
        );


    const statusFilter =
        document.getElementById(
            "hearingStatusFilter"
        );


    const chamberFilter =
        document.getElementById(
            "hearingChamberFilter"
        );


    const dateFilter =
        document.getElementById(
            "hearingDateFilter"
        );


    const rows =
        document.querySelectorAll(
            "#hearingTableBody tr"
        );


    const searchValue =
        searchInput
            ? searchInput.value
                .trim()
                .toLowerCase()
            : "";


    const selectedStatus =
        statusFilter
            ? statusFilter.value
            : "all";


    const selectedChamber =
        chamberFilter
            ? chamberFilter.value
            : "all";


    const selectedDate =
        dateFilter
            ? dateFilter.value
            : "all";


    let visibleRows =
        0;


    rows.forEach(
        function (row) {

            const searchableText =
                row.textContent
                    .replace(/\s+/g, " ")
                    .trim()
                    .toLowerCase();


            const rowStatus =
                row.dataset.status || "";


            const rowChamber =
                row.dataset.chamber || "";


            const rowDate =
                row.dataset.date || "";


            const matchesSearch =
                searchValue === "" ||
                searchableText.includes(
                    searchValue
                );


            const matchesStatus =
                selectedStatus === "all" ||
                rowStatus === selectedStatus;


            const matchesChamber =
                selectedChamber === "all" ||
                rowChamber === selectedChamber;


            const matchesDate =
                selectedDate === "all" ||
                rowDate === selectedDate;


            const shouldDisplay =
                matchesSearch &&
                matchesStatus &&
                matchesChamber &&
                matchesDate;


            row.classList.toggle(
                "hearing-filter-hidden",
                !shouldDisplay
            );


            if (shouldDisplay) {

                visibleRows++;

            }

        }
    );


    updateHearingRecordCount(
        visibleRows
    );


    updateHearingEmptyState(
        visibleRows
    );

}


/* =========================================================
   RESET FILTERS
========================================================= */

function resetHearingFilters() {

    const searchInput =
        document.getElementById(
            "hearingSearchInput"
        );


    const statusFilter =
        document.getElementById(
            "hearingStatusFilter"
        );


    const chamberFilter =
        document.getElementById(
            "hearingChamberFilter"
        );


    const dateFilter =
        document.getElementById(
            "hearingDateFilter"
        );


    if (searchInput) {

        searchInput.value =
            "";

    }


    if (statusFilter) {

        statusFilter.value =
            "all";

    }


    if (chamberFilter) {

        chamberFilter.value =
            "all";

    }


    if (dateFilter) {

        dateFilter.value =
            "all";

    }


    filterHearingRecords();

}


/* =========================================================
   RECORD COUNT
========================================================= */

function updateHearingRecordCount(
    visibleCount
) {

    const rows =
        document.querySelectorAll(
            "#hearingTableBody tr"
        );


    const visibleCountElement =
        document.getElementById(
            "visibleHearingCount"
        );


    const totalCountElement =
        document.getElementById(
            "totalHearingCount"
        );


    const totalRows =
        rows.length;


    if (
        typeof visibleCount !==
        "number"
    ) {

        visibleCount =
            Array.from(rows)
                .filter(
                    function (row) {

                        return !row.classList.contains(
                            "hearing-filter-hidden"
                        );

                    }
                )
                .length;

    }


    if (visibleCountElement) {

        visibleCountElement.textContent =
            visibleCount;

    }


    if (totalCountElement) {

        totalCountElement.textContent =
            totalRows;

    }

}


/* =========================================================
   EMPTY STATE
========================================================= */

function updateHearingEmptyState(
    visibleRows
) {

    const emptyState =
        document.getElementById(
            "hearingEmptyState"
        );


    const tableWrapper =
        document.querySelector(
            ".hearing-table-wrapper"
        );


    if (!emptyState) {
        return;
    }


    if (visibleRows === 0) {

        emptyState.classList.add(
            "visible"
        );


        if (tableWrapper) {

            tableWrapper.style.display =
                "none";

        }

    } else {

        emptyState.classList.remove(
            "visible"
        );


        if (tableWrapper) {

            tableWrapper.style.display =
                "";

        }

    }

}


/* =========================================================
   MODAL INITIALIZATION
========================================================= */

function initializeHearingModal() {

    const openButton =
        document.getElementById(
            "openScheduleModalButton"
        );


    const closeButtons =
        document.querySelectorAll(
            "[data-close-hearing-modal]"
        );


    const form =
        document.getElementById(
            "scheduleHearingForm"
        );


    if (openButton) {

        openButton.addEventListener(
            "click",
            openHearingModal
        );

    }


    closeButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                closeHearingModal
            );

        }
    );


    if (form) {

        form.addEventListener(
            "submit",
            submitHearingSchedule
        );

    }


    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key ===
                "Escape"
            ) {

                closeHearingModal();

            }

        }
    );

}


/* =========================================================
   OPEN MODAL
========================================================= */

function openHearingModal() {

    const modal =
        document.getElementById(
            "scheduleHearingModal"
        );


    if (!modal) {
        return;
    }


    modal.classList.add(
        "open"
    );


    modal.setAttribute(
        "aria-hidden",
        "false"
    );


    document.body.style.overflow =
        "hidden";


    setDefaultHearingFormDate();


    window.setTimeout(
        function () {

            const caseInput =
                document.getElementById(
                    "hearingCaseNumber"
                );


            if (caseInput) {

                caseInput.focus();

            }

        },
        100
    );

}


/* =========================================================
   CLOSE MODAL
========================================================= */

function closeHearingModal() {

    const modal =
        document.getElementById(
            "scheduleHearingModal"
        );


    if (!modal) {
        return;
    }


    modal.classList.remove(
        "open"
    );


    modal.setAttribute(
        "aria-hidden",
        "true"
    );


    document.body.style.overflow =
        "";

}


/* =========================================================
   DEFAULT FORM DATE
========================================================= */

function setDefaultHearingFormDate() {

    const dateInput =
        document.getElementById(
            "hearingDate"
        );


    if (!dateInput) {
        return;
    }


    const year =
        hearingSelectedDate
            .getFullYear();


    const month =
        String(
            hearingSelectedDate
                .getMonth() + 1
        ).padStart(
            2,
            "0"
        );


    const day =
        String(
            hearingSelectedDate
                .getDate()
        ).padStart(
            2,
            "0"
        );


    dateInput.value =
        year +
        "-" +
        month +
        "-" +
        day;

}


/* =========================================================
   FORM SUBMISSION
========================================================= */

function submitHearingSchedule(
    event
) {

    event.preventDefault();


    const form =
        event.currentTarget;


    if (!form.checkValidity()) {

        form.reportValidity();

        return;

    }


    const formData =
        new FormData(
            form
        );


    const hearingData = {

        caseNumber:
            formData.get(
                "case_number"
            ),

        hearingDate:
            formData.get(
                "hearing_date"
            ),

        hearingTime:
            formData.get(
                "hearing_time"
            ),

        chamber:
            formData.get(
                "chamber"
            ),

        stage:
            formData.get(
                "stage"
            ),

        mediator:
            formData.get(
                "mediator"
            ),

        notes:
            formData.get(
                "notes"
            )

    };


    /*
    =========================================================
    DJANGO BACKEND CONNECTION
    =========================================================

    The current form is front-end only.

    When your Django scheduling endpoint is ready,
    replace the demo section below with:

    fetch("/hearings/schedule/", {

        method: "POST",

        headers: {
            "X-CSRFToken":
                getHearingCsrfToken()
        },

        body:
            formData

    })
    .then(function (response) {

        if (!response.ok) {

            throw new Error(
                "Unable to schedule hearing."
            );

        }

        return response.json();

    })
    .then(function (data) {

        closeHearingModal();

        form.reset();

        showHearingToast(
            "Hearing Scheduled",
            "The hearing schedule was saved successfully."
        );

    })
    .catch(function (error) {

        showHearingToast(
            "Unable to Schedule",
            error.message
        );

    });

    =========================================================
    */


    console.log(
        "Hearing schedule:",
        hearingData
    );


    closeHearingModal();


    form.reset();


    showHearingToast(
        "Hearing Scheduled",
        "The hearing schedule was prepared successfully."
    );

}


/* =========================================================
   HEADER ACTIONS
========================================================= */

function initializeHearingHeaderActions() {

    const exportButton =
        document.getElementById(
            "exportCalendarButton"
        );


    const summonsButton =
        document.getElementById(
            "issueSummonsButton"
        );


    if (exportButton) {

        exportButton.addEventListener(
            "click",
            function () {

                showHearingToast(
                    "Calendar Export",
                    "Connect this action to your Django calendar export view."
                );

            }
        );

    }


    if (summonsButton) {

        summonsButton.addEventListener(
            "click",
            function () {

                showHearingToast(
                    "Issue Summons",
                    "Connect this action to your summons generation module."
                );

            }
        );

    }

}


/* =========================================================
   TABLE ACTIONS
========================================================= */

function initializeHearingTableActions() {

    const buttons =
        document.querySelectorAll(
            ".table-action-button"
        );


    buttons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    const title =
                        button.getAttribute(
                            "title"
                        ) || "Hearing action";


                    showHearingToast(
                        title,
                        "This action can now be connected to its Django view."
                    );

                }
            );

        }
    );

}


/* =========================================================
   PAGINATION
========================================================= */

function initializeHearingPagination() {

    const pageNumbers =
        document.querySelectorAll(
            ".pagination-number"
        );


    pageNumbers.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    pageNumbers.forEach(
                        function (page) {

                            page.classList.remove(
                                "active"
                            );

                        }
                    );


                    button.classList.add(
                        "active"
                    );

                }
            );

        }
    );

}


/* =========================================================
   TOAST
========================================================= */

let hearingToastTimeout =
    null;


function showHearingToast(
    title,
    message
) {

    const toast =
        document.getElementById(
            "hearingToast"
        );


    const titleElement =
        document.getElementById(
            "hearingToastTitle"
        );


    const messageElement =
        document.getElementById(
            "hearingToastMessage"
        );


    if (!toast) {
        return;
    }


    if (titleElement) {

        titleElement.textContent =
            title;

    }


    if (messageElement) {

        messageElement.textContent =
            message;

    }


    if (hearingToastTimeout) {

        window.clearTimeout(
            hearingToastTimeout
        );

    }


    toast.classList.add(
        "show"
    );


    hearingToastTimeout =
        window.setTimeout(
            function () {

                toast.classList.remove(
                    "show"
                );

            },
            3500
        );

}


/* =========================================================
   CSRF TOKEN
========================================================= */

function getHearingCsrfToken() {

    const csrfInput =
        document.querySelector(
            "input[name='csrfmiddlewaretoken']"
        );


    if (csrfInput) {

        return csrfInput.value;

    }


    const cookies =
        document.cookie
            .split(";");


    for (
        let index = 0;
        index < cookies.length;
        index++
    ) {

        const cookie =
            cookies[index]
                .trim();


        if (
            cookie.startsWith(
                "csrftoken="
            )
        ) {

            return decodeURIComponent(
                cookie.substring(
                    "csrftoken=".length
                )
            );

        }

    }


    return "";

}