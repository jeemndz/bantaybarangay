/* =========================================================
   BANTAYBARANGAY
   AUDIT LOGS JAVASCRIPT
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    initializeAuditLogs();

});


/* =========================================================
   INITIALIZE
========================================================= */

function initializeAuditLogs() {

    const rows =
        Array.from(
            document.querySelectorAll(".audit-row")
        );

    initializeModuleBadges();

    initializeRowSelection(rows);

    initializeFilters(rows);

    initializeRefresh();

    initializeExport(rows);


    /*
     * Automatically display the first activity
     * when audit records exist.
     */
    if (rows.length > 0) {

        selectAuditRow(rows[0]);

    }

}


/* =========================================================
   ROW SELECTION
========================================================= */

function initializeRowSelection(rows) {

    rows.forEach(function (row) {

        row.addEventListener(
            "click",
            function () {

                selectAuditRow(row);

            }
        );


        const button =
            row.querySelector(".audit-row-button");


        if (button) {

            button.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    event.stopPropagation();

                    selectAuditRow(row);

                }
            );

        }

    });

}


/* =========================================================
   SELECT AUDIT ROW
========================================================= */

function selectAuditRow(row) {

    if (!row) {
        return;
    }


    document
        .querySelectorAll(".audit-row")
        .forEach(function (item) {

            item.classList.remove("active");

        });


    row.classList.add("active");


    const data = {

        id:
            row.dataset.id || "—",

        userId:
            row.dataset.userId || "—",

        user:
            row.dataset.user || "Unknown User",

        module:
            row.dataset.module || "System",

        action:
            row.dataset.action || "Activity",

        description:
            row.dataset.description ||
            "No description available.",

        ip:
            row.dataset.ip || "Not available",

        date:
            row.dataset.date || ""

    };


    updateDetailsPanel(data);

}


/* =========================================================
   UPDATE DETAILS PANEL
========================================================= */

function updateDetailsPanel(data) {

    const emptyState =
        document.getElementById("detailsEmpty");

    const content =
        document.getElementById("detailsContent");


    if (emptyState) {

        emptyState.hidden = true;

    }


    if (content) {

        content.hidden = false;

    }


    setText(
        "detailsId",
        data.id
    );

    setText(
        "detailsUser",
        data.user
    );

    setText(
        "detailsUserId",
        "User ID: " + data.userId
    );

    setText(
        "detailsModule",
        data.module
    );

    setText(
        "detailsAction",
        data.action
    );

    setText(
        "detailsDescription",
        data.description
    );

    setText(
        "detailsIp",
        data.ip
    );


    /* =====================================================
       USER INITIAL
    ====================================================== */

    const avatar =
        document.getElementById("detailsAvatar");


    if (avatar) {

        const name =
            String(data.user || "")
                .trim();

        avatar.textContent =
            name.length > 0
                ? name.charAt(0).toUpperCase()
                : "U";

    }


    /* =====================================================
       DATE
    ====================================================== */

    if (data.date) {

        const parsedDate =
            new Date(data.date);


        if (!Number.isNaN(parsedDate.getTime())) {

            setText(
                "detailsDate",
                parsedDate.toLocaleDateString(
                    undefined,
                    {
                        year: "numeric",
                        month: "long",
                        day: "numeric"
                    }
                )
            );


            setText(
                "detailsTime",
                parsedDate.toLocaleTimeString(
                    undefined,
                    {
                        hour: "2-digit",
                        minute: "2-digit",
                        second: "2-digit"
                    }
                )
            );

            return;

        }

    }


    setText(
        "detailsDate",
        "Not available"
    );

    setText(
        "detailsTime",
        ""
    );

}


/* =========================================================
   SAFE TEXT UPDATE
========================================================= */

function setText(id, value) {

    const element =
        document.getElementById(id);


    if (!element) {
        return;
    }


    element.textContent =
        value ?? "";

}


/* =========================================================
   FILTERS
========================================================= */

function initializeFilters(rows) {

    const searchInput =
        document.getElementById("auditSearch");

    const moduleFilter =
        document.getElementById("moduleFilter");

    const dateFilter =
        document.getElementById("dateFilter");

    const clearButton =
        document.getElementById("clearFiltersBtn");


    function applyFilters() {

        const search =
            searchInput
                ? searchInput.value
                    .trim()
                    .toLowerCase()
                : "";


        const module =
            moduleFilter
                ? moduleFilter.value
                    .trim()
                    .toLowerCase()
                : "";


        const dateRange =
            dateFilter
                ? dateFilter.value
                : "all";


        let visibleCount = 0;


        rows.forEach(function (row) {

            const rowText =
                [
                    row.dataset.user,
                    row.dataset.userId,
                    row.dataset.module,
                    row.dataset.action,
                    row.dataset.description,
                    row.dataset.ip,
                    row.dataset.id
                ]
                .join(" ")
                .toLowerCase();


            const rowModule =
                String(
                    row.dataset.module || ""
                )
                .trim()
                .toLowerCase();


            const matchesSearch =
                !search ||
                rowText.includes(search);


            const matchesModule =
                !module ||
                rowModule === module;


            const matchesDate =
                matchesDateFilter(
                    row.dataset.date,
                    dateRange
                );


            const visible =
                matchesSearch &&
                matchesModule &&
                matchesDate;


            row.style.display =
                visible
                    ? ""
                    : "none";


            if (visible) {

                visibleCount++;

            }

        });


        updateVisibleCount(
            visibleCount,
            rows.length
        );


        updateFilterEmptyState(
            visibleCount,
            rows.length
        );


        ensureSelectedRowIsVisible(rows);

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            applyFilters
        );

    }


    if (moduleFilter) {

        moduleFilter.addEventListener(
            "change",
            applyFilters
        );

    }


    if (dateFilter) {

        dateFilter.addEventListener(
            "change",
            applyFilters
        );

    }


    if (clearButton) {

        clearButton.addEventListener(
            "click",
            function () {

                if (searchInput) {

                    searchInput.value = "";

                }


                if (moduleFilter) {

                    moduleFilter.value = "";

                }


                if (dateFilter) {

                    dateFilter.value = "all";

                }


                applyFilters();


                if (searchInput) {

                    searchInput.focus();

                }

            }
        );

    }

}


/* =========================================================
   DATE FILTER
========================================================= */

function matchesDateFilter(dateValue, filter) {

    if (
        !filter ||
        filter === "all"
    ) {

        return true;

    }


    if (!dateValue) {

        return false;

    }


    const rowDate =
        new Date(dateValue);


    if (
        Number.isNaN(
            rowDate.getTime()
        )
    ) {

        return false;

    }


    const now =
        new Date();


    if (filter === "today") {

        return (
            rowDate.getFullYear() ===
                now.getFullYear() &&

            rowDate.getMonth() ===
                now.getMonth() &&

            rowDate.getDate() ===
                now.getDate()
        );

    }


    const millisecondsPerDay =
        1000 * 60 * 60 * 24;


    const difference =
        now.getTime() -
        rowDate.getTime();


    const days =
        difference /
        millisecondsPerDay;


    if (filter === "week") {

        return (
            days >= 0 &&
            days <= 7
        );

    }


    if (filter === "month") {

        return (
            days >= 0 &&
            days <= 30
        );

    }


    return true;

}


/* =========================================================
   FILTER EMPTY STATE
========================================================= */

function updateFilterEmptyState(
    visibleCount,
    totalCount
) {

    const emptyState =
        document.getElementById(
            "filterEmptyState"
        );


    if (!emptyState) {
        return;
    }


    /*
     * Do not show the filter empty state if
     * there were no database records to begin with.
     */
    if (totalCount === 0) {

        emptyState.hidden = true;

        return;

    }


    emptyState.hidden =
        visibleCount !== 0;

}


/* =========================================================
   VISIBLE COUNT
========================================================= */

function updateVisibleCount(
    visibleCount,
    totalCount
) {

    const counter =
        document.getElementById(
            "visibleLogCount"
        );


    if (!counter) {
        return;
    }


    if (visibleCount === totalCount) {

        counter.textContent =
            totalCount +
            (
                totalCount === 1
                    ? " activity"
                    : " activities"
            );

        return;

    }


    counter.textContent =
        "Showing " +
        visibleCount +
        " of " +
        totalCount;

}


/* =========================================================
   ENSURE SELECTED ROW IS VISIBLE
========================================================= */

function ensureSelectedRowIsVisible(rows) {

    const activeRow =
        document.querySelector(
            ".audit-row.active"
        );


    if (
        activeRow &&
        activeRow.style.display !== "none"
    ) {

        return;

    }


    const firstVisible =
        rows.find(
            function (row) {

                return (
                    row.style.display !== "none"
                );

            }
        );


    if (firstVisible) {

        selectAuditRow(firstVisible);

    } else {

        clearDetailsPanel();

    }

}


/* =========================================================
   CLEAR DETAILS
========================================================= */

function clearDetailsPanel() {

    document
        .querySelectorAll(".audit-row")
        .forEach(function (row) {

            row.classList.remove("active");

        });


    const emptyState =
        document.getElementById(
            "detailsEmpty"
        );

    const content =
        document.getElementById(
            "detailsContent"
        );


    if (emptyState) {

        emptyState.hidden = false;

    }


    if (content) {

        content.hidden = true;

    }

}


/* =========================================================
   MODULE BADGES
========================================================= */

function initializeModuleBadges() {

    document
        .querySelectorAll(
            "[data-module-badge]"
        )
        .forEach(
            function (badge) {

                const module =
                    badge.textContent
                        .trim()
                        .toLowerCase();


                const normalized =
                    module
                        .replace(
                            /[^a-z0-9]+/g,
                            "-"
                        )
                        .replace(
                            /^-|-$/g,
                            ""
                        );


                if (normalized) {

                    badge.classList.add(
                        "module-" +
                        normalized
                    );

                }

            }
        );

}


/* =========================================================
   REFRESH
========================================================= */

function initializeRefresh() {

    const refreshButton =
        document.getElementById(
            "refreshLogsBtn"
        );

    const refreshIcon =
        document.getElementById(
            "refreshIcon"
        );


    if (!refreshButton) {
        return;
    }


    refreshButton.addEventListener(
        "click",
        function () {

            refreshButton.disabled = true;


            if (refreshIcon) {

                refreshIcon.classList.add(
                    "is-spinning"
                );

            }


            /*
             * Small delay allows the refresh animation
             * to be visible before the browser reloads.
             */
            window.setTimeout(
                function () {

                    window.location.reload();

                },
                350
            );

        }
    );

}


/* =========================================================
   CSV EXPORT
========================================================= */

function initializeExport(rows) {

    const exportButton =
        document.getElementById(
            "exportLogsBtn"
        );


    if (!exportButton) {
        return;
    }


    exportButton.addEventListener(
        "click",
        function () {

            const visibleRows =
                rows.filter(
                    function (row) {

                        return (
                            row.style.display !==
                            "none"
                        );

                    }
                );


            if (visibleRows.length === 0) {

                window.alert(
                    "There are no audit logs to export."
                );

                return;

            }


            const records =
                visibleRows.map(
                    function (row) {

                        return [
                            row.dataset.id || "",
                            row.dataset.userId || "",
                            row.dataset.user || "",
                            row.dataset.module || "",
                            row.dataset.action || "",
                            row.dataset.description || "",
                            row.dataset.ip || "",
                            row.dataset.date || ""
                        ];

                    }
                );


            const headers = [
                "Audit ID",
                "User ID",
                "User",
                "Module",
                "Action",
                "Description",
                "IP Address",
                "Created At"
            ];


            const csv =
                [
                    headers,
                    ...records
                ]
                .map(
                    function (record) {

                        return record
                            .map(csvEscape)
                            .join(",");

                    }
                )
                .join("\n");


            downloadCsv(
                csv,
                createExportFilename()
            );

        }
    );

}


/* =========================================================
   CSV ESCAPE
========================================================= */

function csvEscape(value) {

    const text =
        String(
            value ?? ""
        );


    return (
        '"' +
        text.replace(
            /"/g,
            '""'
        ) +
        '"'
    );

}


/* =========================================================
   DOWNLOAD CSV
========================================================= */

function downloadCsv(csv, filename) {

    const blob =
        new Blob(
            [
                "\uFEFF",
                csv
            ],
            {
                type:
                    "text/csv;charset=utf-8;"
            }
        );


    const url =
        URL.createObjectURL(blob);


    const link =
        document.createElement("a");


    link.href = url;

    link.download = filename;

    link.style.display = "none";


    document.body.appendChild(link);

    link.click();

    link.remove();


    URL.revokeObjectURL(url);

}


/* =========================================================
   EXPORT FILENAME
========================================================= */

function createExportFilename() {

    const date =
        new Date();


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
        "bantaybarangay-audit-logs-" +
        year +
        "-" +
        month +
        "-" +
        day +
        ".csv"
    );

}