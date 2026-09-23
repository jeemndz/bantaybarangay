/* =========================================================
   BANTAYBARANGAY
   REQUEST DOCUMENT
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeDocumentSelection();
        initializeDeliverySelection();
        initializePaymentSelection();
        initializeFileUpload();
        initializeCatalog();
        initializeDraft();
        initializeReset();
        initializeFormValidation();

        updateSelections();
        updateFees();

    }
);


/* =========================================================
   DOCUMENT SELECTION
========================================================= */

function initializeDocumentSelection() {

    const documentRadios =
        document.querySelectorAll(
            'input[name="document_type"]'
        );


    documentRadios.forEach(
        function (radio) {

            radio.addEventListener(
                "change",
                function () {

                    updateDocumentCards();

                    updateCatalogCards();

                    updateFormTitle();

                    updateFees();

                }
            );

        }
    );

}


/* =========================================================
   DOCUMENT CARDS
========================================================= */

function updateDocumentCards() {

    const options =
        document.querySelectorAll(
            ".document-option"
        );


    options.forEach(
        function (option) {

            const radio =
                option.querySelector(
                    'input[name="document_type"]'
                );


            if (!radio) {
                return;
            }


            option.classList.toggle(
                "selected",
                radio.checked
            );

        }
    );

}


/* =========================================================
   FORM TITLE
========================================================= */

function updateFormTitle() {

    const selected =
        document.querySelector(
            'input[name="document_type"]:checked'
        );


    const title =
        document.getElementById(
            "requestFormTitle"
        );


    if (!title) {
        return;
    }


    if (!selected) {

        title.textContent =
            "Request Barangay Document";

        return;

    }


    const documentName =
        selected.dataset.name;


    if (documentName) {

        title.textContent =
            documentName + " Request";

    }

}


/* =========================================================
   CATALOG SELECTION
========================================================= */

function initializeCatalog() {

    const cards =
        document.querySelectorAll(
            ".catalog-card"
        );


    cards.forEach(
        function (card) {

            card.addEventListener(
                "click",
                function () {

                    const documentId =
                        card.dataset.documentId;


                    if (!documentId) {
                        return;
                    }


                    const radio =
                        document.querySelector(
                            'input[name="document_type"][value="' +
                            cssEscape(documentId) +
                            '"]'
                        );


                    if (!radio) {
                        return;
                    }


                    radio.checked = true;


                    updateDocumentCards();

                    updateCatalogCards();

                    updateFormTitle();

                    updateFees();


                    const form =
                        document.querySelector(
                            ".request-form-card"
                        );


                    if (form) {

                        form.scrollIntoView({
                            behavior: "smooth",
                            block: "start"
                        });

                    }

                }
            );

        }
    );

}


function updateCatalogCards() {

    const selected =
        document.querySelector(
            'input[name="document_type"]:checked'
        );


    document
        .querySelectorAll(
            ".catalog-card"
        )
        .forEach(
            function (card) {

                if (!selected) {

                    card.classList.remove(
                        "active"
                    );

                    return;

                }


                card.classList.toggle(
                    "active",
                    String(
                        card.dataset.documentId
                    ) === String(
                        selected.value
                    )
                );

            }
        );

}


/* =========================================================
   DELIVERY SELECTION
========================================================= */

function initializeDeliverySelection() {

    const radios =
        document.querySelectorAll(
            'input[name="delivery_method"]'
        );


    radios.forEach(
        function (radio) {

            radio.addEventListener(
                "change",
                function () {

                    updateDeliveryCards();

                    updateFees();

                }
            );

        }
    );

}


function updateDeliveryCards() {

    document
        .querySelectorAll(
            ".delivery-option"
        )
        .forEach(
            function (option) {

                const radio =
                    option.querySelector(
                        'input[name="delivery_method"]'
                    );


                if (!radio) {
                    return;
                }


                option.classList.toggle(
                    "selected",
                    radio.checked
                );

            }
        );

}


/* =========================================================
   PAYMENT SELECTION
========================================================= */

function initializePaymentSelection() {

    const radios =
        document.querySelectorAll(
            'input[name="payment_method"]'
        );


    radios.forEach(
        function (radio) {

            radio.addEventListener(
                "change",
                function () {

                    updatePaymentCards();

                }
            );

        }
    );

}


function updatePaymentCards() {

    document
        .querySelectorAll(
            ".payment-option"
        )
        .forEach(
            function (option) {

                const radio =
                    option.querySelector(
                        'input[name="payment_method"]'
                    );


                if (!radio) {
                    return;
                }


                option.classList.toggle(
                    "selected",
                    radio.checked
                );

            }
        );

}


/* =========================================================
   UPDATE ALL SELECTIONS
========================================================= */

function updateSelections() {

    updateDocumentCards();

    updateCatalogCards();

    updateDeliveryCards();

    updatePaymentCards();

    updateFormTitle();

}


/* =========================================================
   FEE CALCULATION
========================================================= */

function updateFees() {

    const documentRadio =
        document.querySelector(
            'input[name="document_type"]:checked'
        );


    const deliveryRadio =
        document.querySelector(
            'input[name="delivery_method"]:checked'
        );


    let documentFee = 0;

    let deliveryFee = 0;


    if (documentRadio) {

        documentFee =
            parseMoney(
                documentRadio.dataset.price
            );

    }


    if (deliveryRadio) {

        deliveryFee =
            parseMoney(
                deliveryRadio.dataset.deliveryFee
            );

    }


    const total =
        documentFee +
        deliveryFee;


    updateMoneyElement(
        "documentFee",
        documentFee
    );


    updateMoneyElement(
        "deliveryFee",
        deliveryFee
    );


    updateMoneyElement(
        "totalFee",
        total
    );

}


function parseMoney(value) {

    const parsed =
        parseFloat(value);


    if (
        Number.isNaN(parsed)
    ) {

        return 0;

    }


    return parsed;

}


function updateMoneyElement(
    id,
    amount
) {

    const element =
        document.getElementById(id);


    if (!element) {
        return;
    }


    element.textContent =
        formatCurrency(amount);

}


function formatCurrency(amount) {

    return (
        "₱" +
        Number(amount).toFixed(2)
    );

}


/* =========================================================
   FILE UPLOAD
========================================================= */

function initializeFileUpload() {

    const input =
        document.getElementById(
            "documentAttachments"
        );


    const uploadArea =
        document.getElementById(
            "uploadArea"
        );


    if (
        !input ||
        !uploadArea
    ) {

        return;

    }


    input.addEventListener(
        "change",
        function () {

            displaySelectedFiles(
                input.files
            );

        }
    );


    uploadArea.addEventListener(
        "dragover",
        function (event) {

            event.preventDefault();

            uploadArea.classList.add(
                "dragging"
            );

        }
    );


    uploadArea.addEventListener(
        "dragleave",
        function () {

            uploadArea.classList.remove(
                "dragging"
            );

        }
    );


    uploadArea.addEventListener(
        "drop",
        function () {

            uploadArea.classList.remove(
                "dragging"
            );

        }
    );

}


/* =========================================================
   DISPLAY FILES
========================================================= */

function displaySelectedFiles(files) {

    const list =
        document.getElementById(
            "fileList"
        );


    if (!list) {
        return;
    }


    list.innerHTML = "";


    if (
        !files ||
        files.length === 0
    ) {

        return;

    }


    Array
        .from(files)
        .forEach(
            function (file) {

                const item =
                    document.createElement(
                        "div"
                    );


                item.className =
                    "file-item";


                const name =
                    document.createElement(
                        "span"
                    );


                name.className =
                    "file-item-name";


                name.textContent =
                    file.name;


                const size =
                    document.createElement(
                        "span"
                    );


                size.textContent =
                    formatFileSize(
                        file.size
                    );


                item.appendChild(
                    name
                );


                item.appendChild(
                    size
                );


                list.appendChild(
                    item
                );

            }
        );

}


/* =========================================================
   FILE SIZE
========================================================= */

function formatFileSize(bytes) {

    if (
        bytes === 0
    ) {

        return "0 B";

    }


    if (
        bytes < 1024
    ) {

        return (
            bytes +
            " B"
        );

    }


    if (
        bytes <
        1024 * 1024
    ) {

        return (
            bytes / 1024
        ).toFixed(1) +
        " KB";

    }


    return (
        bytes /
        (
            1024 *
            1024
        )
    ).toFixed(1) +
    " MB";

}


/* =========================================================
   SAVE DRAFT
========================================================= */

function initializeDraft() {

    const button =
        document.getElementById(
            "saveDraftButton"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        function () {

            const draft = {

                document_type:
                    getSelectedValue(
                        "document_type"
                    ),

                purpose:
                    getFieldValue(
                        "purpose"
                    ),

                institution:
                    getFieldValue(
                        "institution"
                    ),

                request_notes:
                    getFieldValue(
                        "request_notes"
                    ),

                delivery_method:
                    getSelectedValue(
                        "delivery_method"
                    ),

                payment_method:
                    getSelectedValue(
                        "payment_method"
                    )

            };


            try {

                localStorage.setItem(
                    "bantayBarangayDocumentDraft",
                    JSON.stringify(
                        draft
                    )
                );


                showToast(
                    "Draft Saved",
                    "Your current request details were saved on this browser."
                );

            }

            catch (error) {

                showToast(
                    "Unable to Save Draft",
                    "Your browser could not save the draft."
                );

            }

        }
    );

}


/* =========================================================
   RESET
========================================================= */

function initializeReset() {

    const button =
        document.getElementById(
            "resetDocumentButton"
        );


    const form =
        document.getElementById(
            "documentRequestForm"
        );


    if (
        !button ||
        !form
    ) {

        return;

    }


    button.addEventListener(
        "click",
        function () {

            window.setTimeout(
                function () {

                    updateSelections();

                    updateFees();


                    const fileList =
                        document.getElementById(
                            "fileList"
                        );


                    if (fileList) {

                        fileList.innerHTML =
                            "";

                    }

                },
                0
            );

        }
    );

}


/* =========================================================
   VALIDATION
========================================================= */

function initializeFormValidation() {

    const form =
        document.getElementById(
            "documentRequestForm"
        );


    if (!form) {
        return;
    }


    form.addEventListener(
        "submit",
        function (event) {

            const documentType =
                getSelectedValue(
                    "document_type"
                );


            const purpose =
                getFieldValue(
                    "purpose"
                );


            const deliveryMethod =
                getSelectedValue(
                    "delivery_method"
                );


            if (!documentType) {

                event.preventDefault();


                showToast(
                    "Document Required",
                    "Please select a document."
                );


                scrollToSection(
                    ".document-select-grid"
                );


                return;

            }


            if (!purpose) {

                event.preventDefault();


                showToast(
                    "Purpose Required",
                    "Please enter the purpose of the document request."
                );


                const field =
                    document.getElementById(
                        "purpose"
                    );


                if (field) {

                    field.focus();

                }


                return;

            }


            const deliveryOptions =
                document.querySelectorAll(
                    'input[name="delivery_method"]'
                );


            if (
                deliveryOptions.length > 0 &&
                !deliveryMethod
            ) {

                event.preventDefault();


                showToast(
                    "Release Method Required",
                    "Please select a document release method."
                );


                return;

            }


            const paymentOptions =
                document.querySelectorAll(
                    'input[name="payment_method"]'
                );


            const paymentMethod =
                getSelectedValue(
                    "payment_method"
                );


            if (
                paymentOptions.length > 0 &&
                !paymentMethod
            ) {

                event.preventDefault();


                showToast(
                    "Payment Method Required",
                    "Please select a payment method."
                );

            }

        }
    );

}


/* =========================================================
   GET SELECTED VALUE
========================================================= */

function getSelectedValue(name) {

    const selected =
        document.querySelector(
            'input[name="' +
            name +
            '"]:checked'
        );


    if (!selected) {

        return "";

    }


    return selected.value;

}


/* =========================================================
   GET FIELD VALUE
========================================================= */

function getFieldValue(id) {

    const field =
        document.getElementById(id);


    if (!field) {

        return "";

    }


    return String(
        field.value || ""
    ).trim();

}


/* =========================================================
   SCROLL
========================================================= */

function scrollToSection(selector) {

    const element =
        document.querySelector(
            selector
        );


    if (!element) {
        return;
    }


    element.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });

}


/* =========================================================
   CSS ESCAPE
========================================================= */

function cssEscape(value) {

    if (
        window.CSS &&
        typeof window.CSS.escape ===
        "function"
    ) {

        return window.CSS.escape(
            String(value)
        );

    }


    return String(value)
        .replace(
            /["\\]/g,
            "\\$&"
        );

}


/* =========================================================
   TOAST
========================================================= */

let requestToastTimer = null;


function showToast(
    title,
    message
) {

    const toast =
        document.getElementById(
            "requestToast"
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


    if (requestToastTimer) {

        clearTimeout(
            requestToastTimer
        );

    }


    requestToastTimer =
        setTimeout(
            function () {

                toast.classList.remove(
                    "show"
                );

            },
            3500
        );

}