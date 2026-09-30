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

    const rows = Array.from(
        document.querySelectorAll(".audit-row")
    );

    initializeModuleBadges();

    initializeRowSelection(rows);

    initializeFilterForm();

    initializeRefresh();

    initializeExport(rows);

    /*
     * Automatically select the first audit record
     * on the current page.
     */
    if (rows.length > 0) {

        selectAuditRow(rows[0]);

    } else {

        clearDetailsPanel();

    }

}


/* =========================================================
   FILTER FORM
========================================================= */

function initializeFilterForm() {

    const form =
        document.getElementById("auditFilterForm");

    const moduleFilter =
        document.getElementById("moduleFilter");

    const actionFilter =
        document.getElementById("actionFilter");

    const dateFilter =
        document.getElementById("dateFilter");

    if (!form) {
        return;
    }


    /*
     * Select filters submit automatically.
     *
     * Search remains manual through the Filter button
     * so typing does not reload the page continuously.
     */

    if (moduleFilter) {

        moduleFilter.addEventListener(
            "change",
            function () {

                form.submit();

            }
        );

    }


    if (actionFilter) {

        actionFilter.addEventListener(
            "change",
            function () {

                form.submit();

            }
        );

    }


    if (dateFilter) {

        dateFilter.addEventListener(
            "change",
            function () {

                form.submit();

            }
        );

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
            row.dataset.userId || "",

        user:
            row.dataset.user || "System",

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


    if (data.userId) {

        setText(
            "detailsUserId",
            "User ID: " + data.userId
        );

    } else {

        setText(
            "detailsUserId",
            "System activity"
        );

    }


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
                : "S";

    }


    /* =====================================================
       DATE / TIME
    ====================================================== */

    updateDetailsDate(
        data.date
    );

}


/* =========================================================
   DETAILS DATE
========================================================= */

function updateDetailsDate(dateValue) {

    if (!dateValue) {

        setText(
            "detailsDate",
            "Not available"
        );

        setText(
            "detailsTime",
            ""
        );

        return;

    }


    const parsedDate =
        new Date(dateValue);


    if (
        Number.isNaN(
            parsedDate.getTime()
        )
    ) {

        setText(
            "detailsDate",
            "Not available"
        );

        setText(
            "detailsTime",
            ""
        );

        return;

    }


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
        .forEach(function (badge) {

            const moduleName =
                badge.textContent
                    .trim()
                    .toLowerCase();


            const normalized =
                moduleName
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

        });

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


            window.setTimeout(
                function () {

                    window.location.reload();

                },
                300
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

            /*
             * This exports the records currently displayed
             * on the current paginated page.
             */

            if (rows.length === 0) {

                window.alert(
                    "There are no audit logs to export."
                );

                return;

            }


            const records =
                rows.map(function (row) {

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

                });


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
                .map(function (record) {

                    return record
                        .map(csvEscape)
                        .join(",");

                })
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