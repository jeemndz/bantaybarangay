/* =========================================================
   BANTAYBARANGAY
   DOCUMENT REQUEST MANAGEMENT
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

    initializeRequestModal();

    initializeStatusForm();

    initializeSearch();

    initializeDjangoMessages();

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

        /* -------------------------------------------------
           ROW CLICK
        ------------------------------------------------- */

        row.addEventListener(
            "click",
            function (event) {

                /*
                 * Do not trigger the row when clicking
                 * buttons, links, inputs, selects, or forms.
                 */

                if (
                    event.target.closest(
                        "button, a, input, select, textarea, form"
                    )
                ) {
                    return;
                }

                selectRequestRow(
                    row
                );

            }
        );


        /* -------------------------------------------------
           VIEW BUTTON
        ------------------------------------------------- */

        const viewButton =
            row.querySelector(
                ".dr-view-btn"
            );

        if (viewButton) {

            viewButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    event.stopPropagation();

                    selectRequestRow(
                        row
                    );

                    openRequestModalFromRow(
                        row
                    );

                }
            );

        }

    });

}


/* =========================================================
   SELECT REQUEST ROW
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

}


/* =========================================================
   INITIALIZE MODAL
========================================================= */

function initializeRequestModal() {

    const modal =
        document.getElementById(
            "requestModal"
        );

    if (!modal) {
        return;
    }


    /* -------------------------------------------------
       OVERLAY
    ------------------------------------------------- */

    const overlay =
        modal.querySelector(
            ".dr-modal-overlay"
        );

    if (overlay) {

        overlay.addEventListener(
            "click",
            function () {

                closeRequestModal();

            }
        );

    }


    /* -------------------------------------------------
       CLOSE BUTTON
    ------------------------------------------------- */

    const closeButton =
        modal.querySelector(
            ".dr-modal-close"
        );

    if (closeButton) {

        closeButton.addEventListener(
            "click",
            function () {

                closeRequestModal();

            }
        );

    }


    /* -------------------------------------------------
       ESCAPE KEY
    ------------------------------------------------- */

    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                modal.classList.contains(
                    "show"
                )
            ) {

                closeRequestModal();

            }

        }
    );

}


/* =========================================================
   OPEN REQUEST MODAL
========================================================= */

function openRequestModalFromRow(row) {

    if (!row) {
        return;
    }

    const modal =
        document.getElementById(
            "requestModal"
        );

    if (!modal) {
        return;
    }


    /* =====================================================
       REQUEST INFORMATION
    ===================================================== */

    const requestId =
        getDatasetValue(
            row,
            "requestId"
        );

    const reference =
        getDatasetValue(
            row,
            "reference"
        );

    const residentName =
        getDatasetValue(
            row,
            "resident"
        );

    const residentId =
        getDatasetValue(
            row,
            "residentId"
        );

    const address =
        getDatasetValue(
            row,
            "address"
        );

    const email =
        getDatasetValue(
            row,
            "email"
        );

    const contact =
        getDatasetValue(
            row,
            "contact"
        );

    const documentName =
        getDatasetValue(
            row,
            "document"
        );

    const purpose =
        getDatasetValue(
            row,
            "purpose"
        );

    const institution =
        getDatasetValue(
            row,
            "institution"
        );

    const notes =
        getDatasetValue(
            row,
            "notes"
        );

    const delivery =
        getDatasetValue(
            row,
            "delivery"
        );

    const payment =
        getDatasetValue(
            row,
            "payment"
        );

    const status =
        getDatasetValue(
            row,
            "status"
        );

    const submitted =
        getDatasetValue(
            row,
            "submitted"
        );


    /* =====================================================
       POPULATE MODAL
    ===================================================== */

    setText(
        "modalReference",
        reference
    );

    setText(
        "modalResident",
        residentName
    );

    setText(
        "modalResidentId",
        residentId
    );

    setText(
        "modalEmail",
        email
    );

    setText(
        "modalContact",
        contact
    );

    setText(
        "modalAddress",
        address
    );

    setText(
        "modalDocument",
        documentName
    );

    setText(
        "modalPurpose",
        purpose
    );

    setText(
        "modalInstitution",
        institution
    );

    setText(
        "modalNotes",
        notes
    );

    setText(
        "modalDelivery",
        delivery
    );

    setText(
        "modalPayment",
        payment
    );

    setText(
        "modalSubmitted",
        submitted
    );


    /* =====================================================
       STATUS SELECT
    ===================================================== */

    const statusSelect =
        document.getElementById(
            "modalStatus"
        );

    if (statusSelect) {

        const optionExists =
            Array.from(
                statusSelect.options
            )
            .some(function (option) {

                return (
                    option.value ===
                    status
                );

            });

        if (optionExists) {

            statusSelect.value =
                status;

        }

    }


    /* =====================================================
       UPDATE STATUS FORM
    ===================================================== */

    const statusForm =
        document.getElementById(
            "statusUpdateForm"
        );

    if (statusForm) {

        /*
         * The template should provide the base URL
         * through data-update-url.
         *
         * Example:
         *
         * data-update-url="/document-requests/0/status/"
         */

        const baseUrl =
            statusForm.dataset.updateUrl;

        if (baseUrl) {

            statusForm.action =
                buildStatusUpdateUrl(
                    baseUrl,
                    requestId
                );

        }

    }


    /* =====================================================
       STORE CURRENT REQUEST
    ===================================================== */

    modal.dataset.requestId =
        requestId;

    modal.dataset.reference =
        reference;


    /* =====================================================
       SHOW MODAL
    ===================================================== */

    modal.classList.add(
        "show"
    );

    modal.setAttribute(
        "aria-hidden",
        "false"
    );

    document.body.classList.add(
        "dr-modal-open"
    );


    /* =====================================================
       FOCUS STATUS
    ===================================================== */

    window.setTimeout(
        function () {

            if (statusSelect) {

                statusSelect.focus();

            }

        },
        100
    );

}


/* =========================================================
   GLOBAL OPEN REQUEST MODAL
========================================================= */

/*
 * This keeps compatibility if the HTML still contains:
 *
 * onclick="openRequestModal(this)"
 */

function openRequestModal(button) {

    if (!button) {
        return;
    }

    const row =
        button.closest(
            ".dr-request-row"
        );

    if (!row) {
        return;
    }

    selectRequestRow(
        row
    );

    openRequestModalFromRow(
        row
    );

}


/* =========================================================
   CLOSE REQUEST MODAL
========================================================= */

function closeRequestModal() {

    const modal =
        document.getElementById(
            "requestModal"
        );

    if (!modal) {
        return;
    }

    modal.classList.remove(
        "show"
    );

    modal.setAttribute(
        "aria-hidden",
        "true"
    );

    document.body.classList.remove(
        "dr-modal-open"
    );

}


/* =========================================================
   GET DATASET VALUE
========================================================= */

function getDatasetValue(
    element,
    key
) {

    if (
        !element ||
        !element.dataset
    ) {
        return "";
    }

    const value =
        element.dataset[key];

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
   SET TEXT
========================================================= */

function setText(
    id,
    value
) {

    const element =
        document.getElementById(
            id
        );

    if (!element) {
        return;
    }

    const cleanValue =
        value === undefined ||
        value === null
            ? ""
            : String(value).trim();

    element.textContent =
        cleanValue || "—";

}


/* =========================================================
   BUILD STATUS UPDATE URL
========================================================= */

function buildStatusUpdateUrl(
    baseUrl,
    requestId
) {

    if (
        !baseUrl ||
        !requestId
    ) {
        return baseUrl || "";
    }

    /*
     * Expected Django generated URL:
     *
     * /document-requests/0/status/
     *
     * Replace only the /0/ segment.
     */

    return baseUrl.replace(
        /\/0\/status\/?$/,
        "/" +
        encodeURIComponent(
            requestId
        ) +
        "/status/"
    );

}


/* =========================================================
   STATUS FORM
========================================================= */

function initializeStatusForm() {

    const form =
        document.getElementById(
            "statusUpdateForm"
        );

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        function (event) {

            const statusSelect =
                document.getElementById(
                    "modalStatus"
                );

            if (
                !statusSelect ||
                !statusSelect.value
            ) {

                event.preventDefault();

                showDocumentToast(
                    "Status required",
                    "Please select a request status."
                );

                return;
            }


            /* -------------------------------------------------
               DISABLE SUBMIT BUTTON
            ------------------------------------------------- */

            const submitButton =
                form.querySelector(
                    'button[type="submit"]'
                );

            if (!submitButton) {
                return;
            }

            if (
                submitButton.dataset.submitting ===
                "true"
            ) {

                event.preventDefault();

                return;
            }

            submitButton.dataset.submitting =
                "true";

            submitButton.disabled =
                true;

            submitButton.dataset.originalHtml =
                submitButton.innerHTML;

            submitButton.innerHTML = `
                <i class="fa-solid fa-spinner fa-spin"></i>
                Updating...
            `;

        }
    );

}


/* =========================================================
   SEARCH
========================================================= */

function initializeSearch() {

    /*
     * The Django view handles filtering using GET.
     *
     * This JavaScript simply allows Enter inside the
     * search field to submit the existing filter form.
     */

    const searchInput =
        document.querySelector(
            '.dr-search input[name="search"]'
        );

    if (!searchInput) {
        return;
    }

    searchInput.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key !== "Enter"
            ) {
                return;
            }

            const form =
                searchInput.closest(
                    "form"
                );

            if (!form) {
                return;
            }

            event.preventDefault();

            form.submit();

        }
    );

}


/* =========================================================
   DJANGO MESSAGES
========================================================= */

function initializeDjangoMessages() {

    const messages =
        document.querySelectorAll(
            ".dr-message"
        );

    messages.forEach(
        function (message) {

            window.setTimeout(
                function () {

                    hideDjangoMessage(
                        message
                    );

                },
                5000
            );

        }
    );

}


/* =========================================================
   HIDE DJANGO MESSAGE
========================================================= */

function hideDjangoMessage(
    message
) {

    if (!message) {
        return;
    }

    message.style.transition =
        "opacity 0.25s ease, " +
        "transform 0.25s ease";

    message.style.opacity =
        "0";

    message.style.transform =
        "translateY(-5px)";

    window.setTimeout(
        function () {

            message.remove();

        },
        260
    );

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

    /*
     * The updated template may not contain the old
     * documentToast component.
     *
     * In that case, create one dynamically.
     */

    if (!toast) {

        createDocumentToast(
            title,
            message
        );

        return;

    }

    const titleElement =
        document.getElementById(
            "toastTitle"
        );

    const messageElement =
        document.getElementById(
            "toastMessage"
        );

    if (titleElement) {

        titleElement.textContent =
            title || "";

    }

    if (messageElement) {

        messageElement.textContent =
            message || "";

    }

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


/* =========================================================
   CREATE TOAST
========================================================= */

function createDocumentToast(
    title,
    message
) {

    let toast =
        document.getElementById(
            "dynamicDocumentToast"
        );

    if (!toast) {

        toast =
            document.createElement(
                "div"
            );

        toast.id =
            "dynamicDocumentToast";

        toast.className =
            "dr-dynamic-toast";

        toast.setAttribute(
            "role",
            "status"
        );

        toast.setAttribute(
            "aria-live",
            "polite"
        );

        toast.innerHTML = `
            <div class="dr-dynamic-toast-icon">
                <i class="fa-solid fa-circle-info"></i>
            </div>

            <div class="dr-dynamic-toast-content">
                <strong
                    id="dynamicToastTitle"
                ></strong>

                <span
                    id="dynamicToastMessage"
                ></span>
            </div>
        `;

        document.body.appendChild(
            toast
        );

    }

    const titleElement =
        document.getElementById(
            "dynamicToastTitle"
        );

    const messageElement =
        document.getElementById(
            "dynamicToastMessage"
        );

    if (titleElement) {

        titleElement.textContent =
            title || "";

    }

    if (messageElement) {

        messageElement.textContent =
            message || "";

    }

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


/* =========================================================
   REFRESH REQUESTS
========================================================= */

function refreshDocumentRequests() {

    window.location.reload();

}


/* =========================================================
   RESET FILTERS
========================================================= */

function resetDocumentRequestFilters() {

    const form =
        document.querySelector(
            ".dr-filter-form"
        );

    if (!form) {
        return;
    }

    const search =
        form.querySelector(
            '[name="search"]'
        );

    const documentType =
        form.querySelector(
            '[name="document_type"]'
        );

    const status =
        form.querySelector(
            '[name="status"]'
        );

    if (search) {
        search.value = "";
    }

    if (documentType) {
        documentType.value = "";
    }

    if (status) {
        status.value = "";
    }

    form.submit();

}