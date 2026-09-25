/* =========================================================
   BANTAYBARANGAY
   COMPLAINT MANAGEMENT
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeComplaintReview();
        initializeComplaintMessages();

    }
);


/* =========================================================
   INITIALIZE COMPLAINT REVIEW
========================================================= */

function initializeComplaintReview() {

    const modal =
        document.getElementById(
            "complaintReviewModal"
        );

    const form =
        document.getElementById(
            "complaintReviewForm"
        );


    if (!modal || !form) {

        console.warn(
            "Complaint review modal or form was not found."
        );

        return;

    }


    /* =====================================================
       TABLE ROWS
    ===================================================== */

    const rows =
        document.querySelectorAll(
            ".complaint-row"
        );


    rows.forEach(function (row) {

        row.addEventListener(
            "click",
            function (event) {

                /*
                 * Prevent duplicate behavior if the user
                 * clicks an interactive element.
                 */

                if (
                    event.target.closest(
                        "a, input, select, textarea"
                    )
                ) {
                    return;
                }


                openComplaintReview(
                    row
                );

            }
        );


        /* =================================================
           KEYBOARD ACCESSIBILITY
        ================================================= */

        row.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Enter" ||
                    event.key === " "
                ) {

                    event.preventDefault();

                    openComplaintReview(
                        row
                    );

                }

            }
        );

    });


    /* =====================================================
       ACTION BUTTONS
    ===================================================== */

    document
        .querySelectorAll(
            ".action-btn"
        )
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    event.stopPropagation();


                    const row =
                        button.closest(
                            ".complaint-row"
                        );


                    if (row) {

                        openComplaintReview(
                            row
                        );

                    }

                }
            );

        });


    /* =====================================================
       CLOSE BUTTONS
    ===================================================== */

    document
        .querySelectorAll(
            "[data-close-review]"
        )
        .forEach(function (element) {

            element.addEventListener(
                "click",
                function () {

                    closeComplaintReview();

                }
            );

        });


    /* =====================================================
       ESCAPE KEY
    ===================================================== */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                modal.classList.contains(
                    "active"
                )
            ) {

                closeComplaintReview();

            }

        }
    );


    /* =====================================================
       FORM SUBMISSION
    ===================================================== */

    form.addEventListener(
        "submit",
        function () {

            const button =
                document.getElementById(
                    "reviewSaveButton"
                );


            if (!button) {
                return;
            }


            button.disabled = true;


            const label =
                button.querySelector(
                    "span"
                );


            if (label) {

                label.textContent =
                    "Saving...";

            }

        }
    );

}


/* =========================================================
   OPEN COMPLAINT REVIEW
========================================================= */

function openComplaintReview(row) {

    const modal =
        document.getElementById(
            "complaintReviewModal"
        );

    const form =
        document.getElementById(
            "complaintReviewForm"
        );


    if (!modal || !form || !row) {
        return;
    }


    /* =====================================================
       COMPLAINT ID
    ===================================================== */

    const complaintId =
        row.dataset.complaintId || "";


    setText(
        "reviewReference",
        row.dataset.reference ||
        (
            "#CP-" +
            String(
                complaintId
            ).padStart(
                4,
                "0"
            )
        )
    );


    /* =====================================================
       COMPLAINT INFORMATION
    ===================================================== */

    setText(
        "reviewComplainant",
        row.dataset.complainant
    );


    setText(
        "reviewReportType",
        row.dataset.reportType
    );


    setText(
        "reviewCategory",
        row.dataset.category
    );


    setText(
        "reviewIncidentDate",
        row.dataset.incidentDate
    );


    setText(
        "reviewIncidentTime",
        row.dataset.incidentTime
    );


    setText(
        "reviewLocation",
        row.dataset.location
    );


    setText(
        "reviewSubject",
        row.dataset.subject
    );


    setText(
        "reviewDescription",
        row.dataset.description
    );


    /* =====================================================
       RESPONDENT INFORMATION
    ===================================================== */

    setText(
        "reviewRespondentName",
        row.dataset.respondentName
    );


    setText(
        "reviewRespondentRelationship",
        row.dataset.respondentRelationship
    );


    setText(
        "reviewRespondentContact",
        row.dataset.respondentContact
    );


    setText(
        "reviewRespondentAddress",
        row.dataset.respondentAddress
    );


    /* =====================================================
       RESPONDENT SECTION VISIBILITY
    ===================================================== */

    const respondentSection =
        document.getElementById(
            "reviewRespondentSection"
        );


    const hasRespondent =
        Boolean(
            cleanValue(
                row.dataset.respondentName
            )
        ) ||
        Boolean(
            cleanValue(
                row.dataset.respondentAddress
            )
        ) ||
        Boolean(
            cleanValue(
                row.dataset.respondentRelationship
            )
        ) ||
        Boolean(
            cleanValue(
                row.dataset.respondentContact
            )
        );


    if (respondentSection) {

        if (
            row.dataset.reportType ===
                "Community Issue" &&
            !hasRespondent
        ) {

            respondentSection.classList.add(
                "hidden"
            );

        } else {

            respondentSection.classList.remove(
                "hidden"
            );

        }

    }


    /* =====================================================
       FORM VALUES
    ===================================================== */

    const priority =
        document.getElementById(
            "reviewPriority"
        );


    const status =
        document.getElementById(
            "reviewStatus"
        );


    const resolution =
        document.getElementById(
            "reviewResolution"
        );


    if (priority) {

        priority.value =
            row.dataset.priority ||
            "N/A";

    }


    if (status) {

        status.value =
            row.dataset.status ||
            "Submitted";

    }


    if (resolution) {

        resolution.value =
            row.dataset.resolution ||
            "";

    }


    /* =====================================================
       BUILD DJANGO UPDATE URL
    ===================================================== */

    const urlTemplate =
        form.dataset.updateUrlTemplate;


    if (urlTemplate && complaintId) {

        /*
         * Template example:
         *
         * /complaints/0/update/
         *
         * Replace the placeholder ID with the
         * selected complaint ID.
         */

        form.action =
            urlTemplate.replace(
                /\/0\/(?=[^/]*\/?$)/,
                "/" +
                encodeURIComponent(
                    complaintId
                ) +
                "/"
            );


        /*
         * Fallback in case the project's URL has
         * additional path components.
         */

        if (
            form.action.includes(
                "/0/"
            )
        ) {

            form.action =
                urlTemplate.replace(
                    "/0/",
                    "/" +
                    encodeURIComponent(
                        complaintId
                    ) +
                    "/"
                );

        }

    }


    /* =====================================================
       SHOW MODAL
    ===================================================== */

    modal.classList.add(
        "active"
    );


    modal.setAttribute(
        "aria-hidden",
        "false"
    );


    document.body.classList.add(
        "complaint-review-open"
    );


    /* =====================================================
       FOCUS FIRST FIELD
    ===================================================== */

    window.setTimeout(
        function () {

            if (priority) {
                priority.focus();
            }

        },
        180
    );

}


/* =========================================================
   CLOSE COMPLAINT REVIEW
========================================================= */

function closeComplaintReview() {

    const modal =
        document.getElementById(
            "complaintReviewModal"
        );


    if (!modal) {
        return;
    }


    modal.classList.remove(
        "active"
    );


    modal.setAttribute(
        "aria-hidden",
        "true"
    );


    document.body.classList.remove(
        "complaint-review-open"
    );

}


/* =========================================================
   SET TEXT
========================================================= */

function setText(
    elementId,
    value
) {

    const element =
        document.getElementById(
            elementId
        );


    if (!element) {
        return;
    }


    element.textContent =
        cleanValue(value) ||
        "—";

}


/* =========================================================
   CLEAN VALUE
========================================================= */

function cleanValue(value) {

    if (
        value === undefined ||
        value === null
    ) {

        return "";

    }


    return String(
        value
    ).trim();

}


/* =========================================================
   DJANGO MESSAGES
========================================================= */

function initializeComplaintMessages() {

    document
        .querySelectorAll(
            ".complaint-message"
        )
        .forEach(function (message) {

            const closeButton =
                message.querySelector(
                    ".complaint-message-close"
                );


            if (closeButton) {

                closeButton.addEventListener(
                    "click",
                    function () {

                        hideComplaintMessage(
                            message
                        );

                    }
                );

            }


            window.setTimeout(
                function () {

                    hideComplaintMessage(
                        message
                    );

                },
                5000
            );

        });

}


/* =========================================================
   HIDE MESSAGE
========================================================= */

function hideComplaintMessage(message) {

    if (!message) {
        return;
    }


    message.classList.add(
        "is-hiding"
    );


    window.setTimeout(
        function () {

            message.remove();

        },
        200
    );

}


/* =========================================================
   GLOBAL FUNCTIONS
========================================================= */

window.openComplaintReview =
    openComplaintReview;


window.closeComplaintReview =
    closeComplaintReview;