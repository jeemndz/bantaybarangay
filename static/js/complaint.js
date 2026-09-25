/* =========================================================
   BANTAYBARANGAY
   COMPLAINT MANAGEMENT
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeComplaintReview();
        initializeComplaintMessages();
        initializeEvidencePreview();

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
       CLICKABLE COMPLAINT ROWS
    ===================================================== */

    document
        .querySelectorAll(
            ".complaint-row"
        )
        .forEach(function (row) {

            row.addEventListener(
                "click",
                function (event) {

                    /*
                     * Do not trigger the row when the user
                     * clicked another interactive control.
                     */

                    if (
                        event.target.closest(
                            "a, button, input, select, textarea"
                        )
                    ) {
                        return;
                    }


                    openComplaintReview(
                        row
                    );

                }
            );


            /* =============================================
               KEYBOARD ACCESSIBILITY
            ============================================== */

            row.addEventListener(
                "keydown",
                function (event) {

                    if (
                        event.key === "Enter"
                        ||
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
       CLOSE REVIEW BUTTONS
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
                event.key !== "Escape"
            ) {
                return;
            }


            const evidencePreview =
                document.getElementById(
                    "evidencePreviewModal"
                );


            /*
             * Close the evidence preview first.
             */

            if (
                evidencePreview
                &&
                evidencePreview.classList.contains(
                    "active"
                )
            ) {

                closeEvidencePreview();

                return;

            }


            /*
             * Otherwise close complaint review.
             */

            if (
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


    if (
        !modal
        ||
        !form
        ||
        !row
    ) {
        return;
    }


    const complaintId =
        row.dataset.complaintId || "";


    /* =====================================================
       COMPLAINT REFERENCE
    ===================================================== */

    setText(
        "reviewReference",

        row.dataset.reference
        ||
        (
            "#CP-"
            +
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


    const respondentSection =
        document.getElementById(
            "reviewRespondentSection"
        );


    const hasRespondent =
        Boolean(
            cleanValue(
                row.dataset.respondentName
            )
        )
        ||
        Boolean(
            cleanValue(
                row.dataset.respondentAddress
            )
        )
        ||
        Boolean(
            cleanValue(
                row.dataset.respondentRelationship
            )
        )
        ||
        Boolean(
            cleanValue(
                row.dataset.respondentContact
            )
        );


    if (respondentSection) {

        if (
            row.dataset.reportType ===
                "Community Issue"
            &&
            !hasRespondent
        ) {

            respondentSection
                .classList
                .add(
                    "hidden"
                );

        } else {

            respondentSection
                .classList
                .remove(
                    "hidden"
                );

        }

    }


    /* =====================================================
       REVIEW FORM
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
            row.dataset.priority
            ||
            "N/A";

    }


    if (status) {

        status.value =
            row.dataset.status
            ||
            "Submitted";

    }


    if (resolution) {

        resolution.value =
            row.dataset.resolution
            ||
            "";

    }


    /* =====================================================
       RESET SAVE BUTTON
    ===================================================== */

    const saveButton =
        document.getElementById(
            "reviewSaveButton"
        );


    if (saveButton) {

        saveButton.disabled =
            false;


        const label =
            saveButton.querySelector(
                "span"
            );


        if (label) {

            label.textContent =
                "Save Changes";

        }

    }


    /* =====================================================
       UPDATE FORM URL
    ===================================================== */

    const urlTemplate =
        form.dataset.updateUrlTemplate;


    if (
        urlTemplate
        &&
        complaintId
    ) {

        form.action =
            replaceUrlId(
                urlTemplate,
                complaintId
            );

    }


    /* =====================================================
       SHOW COMPLAINT MODAL
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
       LOAD COMPLAINT EVIDENCE
    ===================================================== */

    loadComplaintEvidence(
        complaintId
    );

}


/* =========================================================
   LOAD COMPLAINT EVIDENCE
========================================================= */

async function loadComplaintEvidence(
    complaintId
) {

    const page =
        document.querySelector(
            ".complaint-page"
        );


    const grid =
        document.getElementById(
            "reviewEvidenceGrid"
        );


    const loading =
        document.getElementById(
            "reviewEvidenceLoading"
        );


    const empty =
        document.getElementById(
            "reviewEvidenceEmpty"
        );


    const count =
        document.getElementById(
            "reviewEvidenceCount"
        );


    if (
        !page
        ||
        !grid
        ||
        !loading
        ||
        !empty
        ||
        !count
    ) {

        return;

    }


    /* =====================================================
       RESET EVIDENCE UI
    ===================================================== */

    grid.innerHTML =
        "";


    grid.hidden =
        true;


    empty.hidden =
        true;


    loading.hidden =
        false;


    count.textContent =
        "Loading...";


    /*
     * Reset the empty-state message in case the
     * previous request failed.
     */

    const emptyMessage =
        empty.querySelector(
            "span"
        );


    if (emptyMessage) {

        emptyMessage.textContent =
            "This complaint does not currently have any uploaded evidence.";

    }


    /* =====================================================
       URL
    ===================================================== */

    const template =
        page.dataset.evidenceUrlTemplate;


    if (
        !template
        ||
        !complaintId
    ) {

        showEvidenceError(
            "Unable to load evidence."
        );

        return;

    }


    const url =
        replaceUrlId(
            template,
            complaintId
        );


    /* =====================================================
       FETCH
    ===================================================== */

    try {

        const response =
            await fetch(
                url,
                {
                    method:
                        "GET",

                    headers: {
                        "X-Requested-With":
                            "XMLHttpRequest"
                    },

                    credentials:
                        "same-origin"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Evidence request returned "
                +
                response.status
            );

        }


        const data =
            await response.json();


        loading.hidden =
            true;


        const evidence =
            Array.isArray(
                data.evidence
            )
                ? data.evidence
                : [];


        /* =================================================
           COUNT
        ================================================= */

        count.textContent =
            evidence.length
            +
            (
                evidence.length === 1
                    ? " file"
                    : " files"
            );


        /* =================================================
           EMPTY
        ================================================= */

        if (
            evidence.length === 0
        ) {

            empty.hidden =
                false;

            return;

        }


        /* =================================================
           CREATE CARDS
        ================================================= */

        evidence.forEach(
            function (item) {

                const card =
                    createEvidenceCard(
                        item
                    );


                grid.appendChild(
                    card
                );

            }
        );


        grid.hidden =
            false;

    } catch (error) {

        console.error(
            "Evidence loading error:",
            error
        );


        loading.hidden =
            true;


        count.textContent =
            "Unavailable";


        showEvidenceError(
            "Evidence could not be loaded. Please try again."
        );

    }

}


/* =========================================================
   CREATE EVIDENCE CARD
========================================================= */

function createEvidenceCard(item) {

    const button =
        document.createElement(
            "button"
        );


    button.type =
        "button";


    button.className =
        "review-evidence-item";


    /* =====================================================
       FILE KIND
    ===================================================== */

    const kind =
        determineEvidenceKind(
            item.file_type,
            item.file_name
        );


    button.dataset.kind =
        kind;


    /* =====================================================
       PREVIEW
    ===================================================== */

    const preview =
        document.createElement(
            "div"
        );


    preview.className =
        "review-evidence-thumbnail";


    /* =====================================================
       IMAGE
    ===================================================== */

    if (
        kind === "image"
        &&
        item.file_path
    ) {

        const image =
            document.createElement(
                "img"
            );


        image.src =
            item.file_path;


        image.alt =
            item.file_name
            ||
            "Complaint evidence";


        image.loading =
            "lazy";


        image.addEventListener(
            "error",
            function () {

                preview.innerHTML =
                    "";


                preview.appendChild(
                    createEvidenceIcon(
                        "image"
                    )
                );

            }
        );


        preview.appendChild(
            image
        );

    }

    /* =====================================================
       OTHER FILE TYPES
    ===================================================== */

    else {

        preview.appendChild(
            createEvidenceIcon(
                kind
            )
        );

    }


    /* =====================================================
       VIDEO PLAY INDICATOR
    ===================================================== */

    if (
        kind === "video"
    ) {

        const play =
            document.createElement(
                "span"
            );


        play.className =
            "review-evidence-play";


        play.textContent =
            "▶";


        preview.appendChild(
            play
        );

    }


    /* =====================================================
       HASH / VERIFIED
    ===================================================== */

    if (
        cleanValue(
            item.file_hash
        )
    ) {

        const verified =
            document.createElement(
                "span"
            );


        verified.className =
            "review-evidence-verified";


        verified.textContent =
            "Verified";


        preview.appendChild(
            verified
        );

    }


    /* =====================================================
       INFORMATION
    ===================================================== */

    const info =
        document.createElement(
            "div"
        );


    info.className =
        "review-evidence-info";


    const name =
        document.createElement(
            "strong"
        );


    name.textContent =
        item.file_name
        ||
        "Evidence file";


    name.title =
        item.file_name
        ||
        "Evidence file";


    const meta =
        document.createElement(
            "div"
        );


    meta.className =
        "review-evidence-meta";


    const size =
        document.createElement(
            "span"
        );


    size.textContent =
        formatFileSize(
            item.file_size
        );


    const type =
        document.createElement(
            "span"
        );


    type.textContent =
        getFriendlyFileType(
            item.file_type,
            item.file_name
        );


    meta.appendChild(
        size
    );


    meta.appendChild(
        type
    );


    info.appendChild(
        name
    );


    info.appendChild(
        meta
    );


    button.appendChild(
        preview
    );


    button.appendChild(
        info
    );


    /* =====================================================
       OPEN PREVIEW
    ===================================================== */

    button.addEventListener(
        "click",
        function (event) {

            event.preventDefault();
            event.stopPropagation();


            openEvidencePreview(
                item,
                kind
            );

        }
    );


    return button;

}


/* =========================================================
   DETERMINE EVIDENCE KIND
========================================================= */

function determineEvidenceKind(
    fileType,
    fileName
) {

    const type =
        String(
            fileType || ""
        ).toLowerCase();


    const name =
        String(
            fileName || ""
        ).toLowerCase();


    /* =====================================================
       IMAGE
    ===================================================== */

    if (
        type.startsWith(
            "image/"
        )
        ||
        /\.(jpg|jpeg|png|gif|webp|bmp)$/i
            .test(name)
    ) {

        return "image";

    }


    /* =====================================================
       VIDEO
    ===================================================== */

    if (
        type.startsWith(
            "video/"
        )
        ||
        /\.(mp4|webm|mov|m4v|ogv)$/i
            .test(name)
    ) {

        return "video";

    }


    /* =====================================================
       AUDIO
    ===================================================== */

    if (
        type.startsWith(
            "audio/"
        )
        ||
        /\.(mp3|wav|ogg|m4a|aac|flac)$/i
            .test(name)
    ) {

        return "audio";

    }


    /* =====================================================
       PDF
    ===================================================== */

    if (
        type.includes(
            "pdf"
        )
        ||
        /\.pdf$/i.test(
            name
        )
    ) {

        return "pdf";

    }


    return "document";

}


/* =========================================================
   CREATE EVIDENCE ICON
========================================================= */

function createEvidenceIcon(type) {

    const wrapper =
        document.createElement(
            "div"
        );


    wrapper.className =
        "review-evidence-file-icon "
        +
        "review-evidence-file-"
        +
        type;


    const labels = {

        image:
            "IMG",

        video:
            "VIDEO",

        audio:
            "AUDIO",

        pdf:
            "PDF",

        document:
            "FILE"

    };


    wrapper.textContent =
        labels[type]
        ||
        "FILE";


    return wrapper;

}


/* =========================================================
   INITIALIZE EVIDENCE PREVIEW
========================================================= */

function initializeEvidencePreview() {

    document
        .querySelectorAll(
            "[data-close-evidence-preview]"
        )
        .forEach(function (element) {

            element.addEventListener(
                "click",
                function () {

                    closeEvidencePreview();

                }
            );

        });

}


/* =========================================================
   OPEN EVIDENCE PREVIEW
========================================================= */

function openEvidencePreview(
    item,
    kind
) {

    const modal =
        document.getElementById(
            "evidencePreviewModal"
        );


    const content =
        document.getElementById(
            "evidencePreviewContent"
        );


    const title =
        document.getElementById(
            "evidencePreviewTitle"
        );


    const type =
        document.getElementById(
            "evidencePreviewType"
        );


    const size =
        document.getElementById(
            "evidencePreviewSize"
        );


    const date =
        document.getElementById(
            "evidencePreviewDate"
        );


    const original =
        document.getElementById(
            "evidenceOpenOriginal"
        );


    if (
        !modal
        ||
        !content
    ) {

        return;

    }


    /* =====================================================
       RESET
    ===================================================== */

    content.innerHTML =
        "";


    /* =====================================================
       INFORMATION
    ===================================================== */

    if (title) {

        title.textContent =
            item.file_name
            ||
            "Evidence";

    }


    if (type) {

        type.textContent =
            getFriendlyFileType(
                item.file_type,
                item.file_name
            );

    }


    if (size) {

        size.textContent =
            formatFileSize(
                item.file_size
            );

    }


    if (date) {

        date.textContent =
            item.uploaded_at
            ||
            "";

    }


    /* =====================================================
       OPEN ORIGINAL LINK
    ===================================================== */

    if (original) {

        if (
            cleanValue(
                item.file_path
            )
        ) {

            original.href =
                item.file_path;


            original.style.display =
                "inline-flex";

        } else {

            original.removeAttribute(
                "href"
            );


            original.style.display =
                "none";

        }

    }


    /* =====================================================
       IMAGE
    ===================================================== */

    if (
        kind === "image"
        &&
        item.file_path
    ) {

        const image =
            document.createElement(
                "img"
            );


        image.src =
            item.file_path;


        image.alt =
            item.file_name
            ||
            "Complaint evidence";


        image.className =
            "evidence-preview-image";


        content.appendChild(
            image
        );

    }

    /* =====================================================
       VIDEO
    ===================================================== */

    else if (
        kind === "video"
        &&
        item.file_path
    ) {

        const video =
            document.createElement(
                "video"
            );


        video.src =
            item.file_path;


        video.controls =
            true;


        video.preload =
            "metadata";


        video.playsInline =
            true;


        video.className =
            "evidence-preview-video";


        content.appendChild(
            video
        );

    }

    /* =====================================================
       AUDIO
    ===================================================== */

    else if (
        kind === "audio"
        &&
        item.file_path
    ) {

        const wrapper =
            document.createElement(
                "div"
            );


        wrapper.className =
            "evidence-preview-audio-wrapper";


        const audio =
            document.createElement(
                "audio"
            );


        audio.src =
            item.file_path;


        audio.controls =
            true;


        audio.preload =
            "metadata";


        wrapper.appendChild(
            audio
        );


        content.appendChild(
            wrapper
        );

    }

    /* =====================================================
       PDF
    ===================================================== */

    else if (
        kind === "pdf"
        &&
        item.file_path
    ) {

        const frame =
            document.createElement(
                "iframe"
            );


        frame.src =
            item.file_path;


        frame.className =
            "evidence-preview-pdf";


        frame.title =
            item.file_name
            ||
            "PDF evidence";


        content.appendChild(
            frame
        );

    }

    /* =====================================================
       DOCUMENT / NO PREVIEW
    ===================================================== */

    else {

        createDocumentFallback(
            content,
            kind
        );

    }


    /* =====================================================
       SHOW
    ===================================================== */

    modal.classList.add(
        "active"
    );


    modal.setAttribute(
        "aria-hidden",
        "false"
    );

}


/* =========================================================
   DOCUMENT FALLBACK
========================================================= */

function createDocumentFallback(
    content,
    kind
) {

    const documentPreview =
        document.createElement(
            "div"
        );


    documentPreview.className =
        "evidence-preview-document";


    const icon =
        document.createElement(
            "div"
        );


    icon.className =
        "evidence-preview-document-icon";


    icon.textContent =
        kind === "pdf"
            ? "PDF"
            : "FILE";


    const message =
        document.createElement(
            "p"
        );


    message.textContent =
        (
            "Preview is not available for this file type. "
            +
            "Use Open Original to view or download the file."
        );


    documentPreview.appendChild(
        icon
    );


    documentPreview.appendChild(
        message
    );


    content.appendChild(
        documentPreview
    );

}


/* =========================================================
   CLOSE EVIDENCE PREVIEW
========================================================= */

function closeEvidencePreview() {

    const modal =
        document.getElementById(
            "evidencePreviewModal"
        );


    const content =
        document.getElementById(
            "evidencePreviewContent"
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


    /*
     * Clearing the content stops currently playing
     * video or audio when the preview closes.
     */

    if (content) {

        content.innerHTML =
            "";

    }

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


    /* =====================================================
       CLOSE EVIDENCE PREVIEW FIRST
    ===================================================== */

    closeEvidencePreview();


    /* =====================================================
       CLOSE REVIEW
    ===================================================== */

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


    /* =====================================================
       RESET EVIDENCE AREA
    ===================================================== */

    const grid =
        document.getElementById(
            "reviewEvidenceGrid"
        );


    const loading =
        document.getElementById(
            "reviewEvidenceLoading"
        );


    const empty =
        document.getElementById(
            "reviewEvidenceEmpty"
        );


    const count =
        document.getElementById(
            "reviewEvidenceCount"
        );


    if (grid) {

        grid.innerHTML =
            "";

        grid.hidden =
            true;

    }


    if (loading) {

        loading.hidden =
            true;

    }


    if (empty) {

        empty.hidden =
            true;

    }


    if (count) {

        count.textContent =
            "0 files";

    }

}


/* =========================================================
   FRIENDLY FILE TYPE
========================================================= */

function getFriendlyFileType(
    fileType,
    fileName
) {

    const kind =
        determineEvidenceKind(
            fileType,
            fileName
        );


    const labels = {

        image:
            "Image",

        video:
            "Video",

        audio:
            "Audio",

        pdf:
            "PDF",

        document:
            "Document"

    };


    return (
        labels[kind]
        ||
        "Document"
    );

}


/* =========================================================
   FORMAT FILE SIZE
========================================================= */

function formatFileSize(bytes) {

    const size =
        Number(
            bytes || 0
        );


    if (
        !Number.isFinite(size)
        ||
        size <= 0
    ) {

        return "0 B";

    }


    const units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB"
    ];


    const index =
        Math.min(
            Math.floor(
                Math.log(size)
                /
                Math.log(1024)
            ),

            units.length - 1
        );


    const value =
        size
        /
        Math.pow(
            1024,
            index
        );


    const formatted =
        index === 0
            ? value.toFixed(0)
            : value.toFixed(1);


    return (
        formatted
        +
        " "
        +
        units[index]
    );

}


/* =========================================================
   SHOW EVIDENCE ERROR
========================================================= */

function showEvidenceError(message) {

    const loading =
        document.getElementById(
            "reviewEvidenceLoading"
        );


    const empty =
        document.getElementById(
            "reviewEvidenceEmpty"
        );


    const grid =
        document.getElementById(
            "reviewEvidenceGrid"
        );


    const count =
        document.getElementById(
            "reviewEvidenceCount"
        );


    if (loading) {

        loading.hidden =
            true;

    }


    if (grid) {

        grid.hidden =
            true;

    }


    if (count) {

        count.textContent =
            "Unavailable";

    }


    if (empty) {

        empty.hidden =
            false;


        const text =
            empty.querySelector(
                "span"
            );


        if (text) {

            text.textContent =
                message;

        }

    }

}


/* =========================================================
   REPLACE URL ID

   Example:

   /evidence/complaint/0/
          ↓
   /evidence/complaint/15/
========================================================= */

function replaceUrlId(
    template,
    id
) {

    if (
        !template
        ||
        !id
    ) {

        return template;

    }


    /*
     * Django's URL generated with ID 0 normally
     * contains /0/. Replace that placeholder.
     */

    if (
        template.includes(
            "/0/"
        )
    ) {

        return template.replace(
            "/0/",
            "/"
            +
            encodeURIComponent(id)
            +
            "/"
        );

    }


    /*
     * Fallback in case the URL does not contain
     * the expected /0/ pattern.
     */

    return template.replace(
        /0(?=\/?$)/,
        encodeURIComponent(id)
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
        cleanValue(value)
        ||
        "—";

}


/* =========================================================
   CLEAN VALUE
========================================================= */

function cleanValue(value) {

    if (
        value === undefined
        ||
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


window.openEvidencePreview =
    openEvidencePreview;


window.closeEvidencePreview =
    closeEvidencePreview;