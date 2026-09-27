/* =========================================================
   BANTAYBARANGAY
   HEARING SCHEDULE
========================================================= */


/* =========================================================
   STATE
========================================================= */

let hearingCalendarDate =
    new Date();


/* =========================================================
   READY
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeMessages();

        initializeScheduleModal();

        initializeCalendar();

        initializeHearingSessions();

        initializeFilters();

        initializeConfirmForms();

        initializePostponeForms();

    }
);


/* =========================================================
   MESSAGES
========================================================= */

function initializeMessages() {

    document
        .querySelectorAll(
            "[data-close-message]"
        )
        .forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const message =
                            button.closest(
                                "[data-hearing-message]"
                            );

                        if (message) {

                            message.remove();

                        }

                    }
                );

            }
        );

}


/* =========================================================
   SCHEDULE MODAL
========================================================= */

function initializeScheduleModal() {

    const modal =
        document.getElementById(
            "scheduleHearingModal"
        );

    const openButton =
        document.getElementById(
            "openScheduleModalButton"
        );


    if (
        openButton
        &&
        modal
    ) {

        openButton.addEventListener(
            "click",
            function () {

                modal.classList.add(
                    "open"
                );

                modal.setAttribute(
                    "aria-hidden",
                    "false"
                );

                document.body.style.overflow =
                    "hidden";

            }
        );

    }


    document
        .querySelectorAll(
            "[data-close-hearing-modal]"
        )
        .forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    closeScheduleModal
                );

            }
        );

}


/* =========================================================
   CLOSE SCHEDULE MODAL
========================================================= */

function closeScheduleModal() {

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
   CALENDAR
========================================================= */

function initializeCalendar() {

    const page =
        document.querySelector(
            ".hearing-page"
        );

    if (page) {

        const today =
            page.dataset.today;

        if (today) {

            hearingCalendarDate =
                parseLocalDate(
                    today
                );

        }

    }


    const previous =
        document.getElementById(
            "previousHearingMonth"
        );

    const next =
        document.getElementById(
            "nextHearingMonth"
        );

    const todayButton =
        document.getElementById(
            "calendarTodayButton"
        );


    if (previous) {

        previous.addEventListener(
            "click",
            function () {

                hearingCalendarDate
                    .setMonth(
                        hearingCalendarDate
                            .getMonth()
                        -
                        1
                    );

                renderCalendar();

            }
        );

    }


    if (next) {

        next.addEventListener(
            "click",
            function () {

                hearingCalendarDate
                    .setMonth(
                        hearingCalendarDate
                            .getMonth()
                        +
                        1
                    );

                renderCalendar();

            }
        );

    }


    if (todayButton) {

        todayButton.addEventListener(
            "click",
            function () {

                const page =
                    document.querySelector(
                        ".hearing-page"
                    );

                hearingCalendarDate =
                    page
                    &&
                    page.dataset.today

                        ? parseLocalDate(
                            page.dataset.today
                        )

                        : new Date();


                renderCalendar();

            }
        );

    }


    renderCalendar();

}


/* =========================================================
   CALENDAR EVENTS
========================================================= */

function getCalendarEvents() {

    return Array.from(
        document.querySelectorAll(
            "[data-hearing-event]"
        )
    )
    .map(
        function (element) {

            return {

                id:
                    element.dataset.id,

                date:
                    element.dataset.date,

                time:
                    element.dataset.time,

                caseNumber:
                    element.dataset.case,

                status:
                    element.dataset.status,

                chamber:
                    element.dataset.chamber

            };

        }
    );

}


/* =========================================================
   RENDER MONTH
========================================================= */

function renderCalendar() {

    const grid =
        document.getElementById(
            "hearingCalendarGrid"
        );

    const label =
        document.getElementById(
            "currentHearingMonth"
        );

    if (!grid) {

        return;

    }


    const year =
        hearingCalendarDate
            .getFullYear();

    const month =
        hearingCalendarDate
            .getMonth();


    if (label) {

        label.textContent =
            new Intl.DateTimeFormat(
                "en-US",
                {
                    month:
                        "long",

                    year:
                        "numeric"
                }
            )
            .format(
                hearingCalendarDate
            );

    }


    grid.innerHTML =
        "";


    const firstDay =
        new Date(
            year,
            month,
            1
        );

    const startDay =
        firstDay.getDay();

    const daysInMonth =
        new Date(
            year,
            month + 1,
            0
        )
        .getDate();


    const previousMonthDays =
        new Date(
            year,
            month,
            0
        )
        .getDate();


    const totalCells =
        42;


    const events =
        getCalendarEvents();


    for (
        let index = 0;
        index < totalCells;
        index++
    ) {

        let cellDate;

        let outsideMonth =
            false;


        if (index < startDay) {

            const day =
                previousMonthDays
                -
                startDay
                +
                index
                +
                1;

            cellDate =
                new Date(
                    year,
                    month - 1,
                    day
                );

            outsideMonth =
                true;

        }

        else if (
            index
            >=
            startDay + daysInMonth
        ) {

            const day =
                index
                -
                (
                    startDay
                    +
                    daysInMonth
                )
                +
                1;

            cellDate =
                new Date(
                    year,
                    month + 1,
                    day
                );

            outsideMonth =
                true;

        }

        else {

            const day =
                index
                -
                startDay
                +
                1;

            cellDate =
                new Date(
                    year,
                    month,
                    day
                );

        }


        grid.appendChild(
            createCalendarDay(
                cellDate,
                events,
                outsideMonth
            )
        );

    }

}


/* =========================================================
   CREATE CALENDAR DAY
========================================================= */

function createCalendarDay(
    date,
    events,
    outsideMonth
) {

    const cell =
        document.createElement(
            "div"
        );

    cell.className =
        "hearing-calendar-day";


    if (outsideMonth) {

        cell.classList.add(
            "outside-month"
        );

    }


    const dateKey =
        formatDateKey(
            date
        );


    const page =
        document.querySelector(
            ".hearing-page"
        );


    if (
        page
        &&
        page.dataset.today
        ===
        dateKey
    ) {

        cell.classList.add(
            "today"
        );

    }


    const number =
        document.createElement(
            "div"
        );

    number.className =
        "hearing-calendar-day-number";

    number.textContent =
        date.getDate();


    cell.appendChild(
        number
    );


    const dayEvents =
        events.filter(
            function (event) {

                return (
                    event.date
                    ===
                    dateKey
                );

            }
        );


    dayEvents.forEach(
        function (event) {

            const button =
                document.createElement(
                    "button"
                );

            button.type =
                "button";

            button.className =
                "hearing-calendar-event";


            button.classList.add(
                "status-"
                +
                slugify(
                    event.status
                )
            );


            const time =
                document.createElement(
                    "span"
                );

            time.className =
                "calendar-event-time";

            time.textContent =
                formatTime(
                    event.time
                );


            const title =
                document.createElement(
                    "strong"
                );

            title.textContent =
                event.caseNumber;


            const chamber =
                document.createElement(
                    "small"
                );

            chamber.textContent =
                event.chamber
                +
                " • "
                +
                event.status;


            button.appendChild(
                time
            );

            button.appendChild(
                title
            );

            button.appendChild(
                chamber
            );


            button.addEventListener(
                "click",
                function () {

                    openHearingSession(
                        event.id
                    );

                }
            );


            cell.appendChild(
                button
            );

        }
    );


    return cell;

}


/* =========================================================
   HEARING SESSION MODALS
========================================================= */

function initializeHearingSessions() {

    document
        .querySelectorAll(
            "[data-open-session]"
        )
        .forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        openHearingSession(
                            button.dataset
                                .openSession
                        );

                    }
                );

            }
        );


    document
        .querySelectorAll(
            "[data-close-session]"
        )
        .forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        closeHearingSession(
                            button
                        );

                    }
                );

            }
        );


    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key
                ===
                "Escape"
            ) {

                closeAllHearingSessions();

                closeScheduleModal();

            }

        }
    );

}


/* =========================================================
   OPEN SESSION
========================================================= */

function openHearingSession(
    hearingId
) {

    const modal =
        document.getElementById(
            "hearingSession"
            +
            hearingId
        );

    if (!modal) {

        return;

    }


    closeAllHearingSessions();


    modal.classList.add(
        "open"
    );

    modal.setAttribute(
        "aria-hidden",
        "false"
    );

    document.body.style.overflow =
        "hidden";

}


/* =========================================================
   CLOSE SESSION
========================================================= */

function closeHearingSession(
    element
) {

    const modal =
        element.closest(
            ".hearing-session-modal"
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
   CLOSE ALL
========================================================= */

function closeAllHearingSessions() {

    document
        .querySelectorAll(
            ".hearing-session-modal.open"
        )
        .forEach(
            function (modal) {

                modal.classList.remove(
                    "open"
                );

                modal.setAttribute(
                    "aria-hidden",
                    "true"
                );

            }
        );

    document.body.style.overflow =
        "";

}


/* =========================================================
   POSTPONE
========================================================= */

function initializePostponeForms() {

    document
        .querySelectorAll(
            "[data-show-postpone]"
        )
        .forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const form =
                            document.getElementById(
                                "postponeForm"
                                +
                                button.dataset
                                    .showPostpone
                            );

                        if (!form) {

                            return;

                        }

                        form.hidden =
                            !form.hidden;

                    }
                );

            }
        );

}


/* =========================================================
   FILTERS
========================================================= */

function initializeFilters() {

    const search =
        document.getElementById(
            "hearingSearchInput"
        );

    const status =
        document.getElementById(
            "hearingStatusFilter"
        );

    const reset =
        document.getElementById(
            "resetHearingFilters"
        );


    if (search) {

        search.addEventListener(
            "input",
            filterHearingRows
        );

    }


    if (status) {

        status.addEventListener(
            "change",
            filterHearingRows
        );

    }


    if (reset) {

        reset.addEventListener(
            "click",
            function () {

                if (search) {

                    search.value =
                        "";

                }

                if (status) {

                    status.value =
                        "all";

                }

                filterHearingRows();

            }
        );

    }

}


/* =========================================================
   FILTER ROWS
========================================================= */

function filterHearingRows() {

    const search =
        document.getElementById(
            "hearingSearchInput"
        );

    const status =
        document.getElementById(
            "hearingStatusFilter"
        );


    const searchValue =
        search
            ? search.value
                .trim()
                .toLowerCase()
            : "";


    const statusValue =
        status
            ? status.value
            : "all";


    document
        .querySelectorAll(
            "#hearingTableBody tr[data-hearing-id]"
        )
        .forEach(
            function (row) {

                const matchesSearch =
                    !searchValue
                    ||
                    row.textContent
                        .toLowerCase()
                        .includes(
                            searchValue
                        );


                const matchesStatus =
                    statusValue
                    ===
                    "all"
                    ||
                    row.dataset.status
                    ===
                    statusValue;


                row.hidden =
                    !(
                        matchesSearch
                        &&
                        matchesStatus
                    );

            }
        );

}


/* =========================================================
   CONFIRM FORMS
========================================================= */

function initializeConfirmForms() {

    document
        .querySelectorAll(
            "form[data-confirm]"
        )
        .forEach(
            function (form) {

                form.addEventListener(
                    "submit",
                    function (event) {

                        const message =
                            form.dataset.confirm;

                        if (
                            message
                            &&
                            !window.confirm(
                                message
                            )
                        ) {

                            event.preventDefault();

                        }

                    }
                );

            }
        );

}


/* =========================================================
   DATE HELPERS
========================================================= */

function parseLocalDate(
    value
) {

    const parts =
        String(
            value
        )
        .split("-")
        .map(Number);


    return new Date(
        parts[0],
        parts[1] - 1,
        parts[2]
    );

}


function formatDateKey(
    date
) {

    const year =
        date.getFullYear();

    const month =
        String(
            date.getMonth() + 1
        )
        .padStart(
            2,
            "0"
        );

    const day =
        String(
            date.getDate()
        )
        .padStart(
            2,
            "0"
        );


    return (
        year
        +
        "-"
        +
        month
        +
        "-"
        +
        day
    );

}


function formatTime(
    value
) {

    if (!value) {

        return "";

    }

    const parts =
        value.split(":");

    let hour =
        Number(
            parts[0]
        );

    const minute =
        parts[1]
        ||
        "00";

    const suffix =
        hour >= 12
            ? "PM"
            : "AM";


    hour =
        hour % 12
        ||
        12;


    return (
        hour
        +
        ":"
        +
        minute
        +
        " "
        +
        suffix
    );

}


function slugify(
    value
) {

    return String(
        value
        ||
        ""
    )
    .toLowerCase()
    .trim()
    .replace(
        /[^a-z0-9]+/g,
        "-"
    )
    .replace(
        /^-|-$/g,
        ""
    );

}


/* =========================================================
   GLOBAL
========================================================= */

window.openHearingSession =
    openHearingSession;