/* =========================================================
   BANTAYBARANGAY
   COMPLAINT MANAGEMENT
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeComplaintMessages();
        initializeReviewFileUpload();

    }
);


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

            if (message.parentNode) {

                message.remove();

            }

        },

        200
    );

}


/* =========================================================
   REVIEW FILE UPLOAD
========================================================= */

let reviewSelectedFiles = [];


/* =========================================================
   UPLOAD SETTINGS
========================================================= */

const REVIEW_MAX_FILES = 5;

const REVIEW_MAX_FILE_SIZE =
    10 * 1024 * 1024;


/* =========================================================
   ALLOWED FILE EXTENSIONS
========================================================= */

const REVIEW_ALLOWED_EXTENSIONS = [

    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",

    ".mp4",
    ".webm",
    ".mov",

    ".mp3",
    ".wav",
    ".ogg",
    ".m4a",
    ".aac",

    ".pdf",

    ".doc",
    ".docx"

];


/* =========================================================
   INITIALIZE REVIEW FILE UPLOAD
========================================================= */

function initializeReviewFileUpload() {

    const input =
        document.getElementById(
            "reviewEvidenceFiles"
        );

    const area =
        document.getElementById(
            "reviewUploadArea"
        );

    const browse =
        document.getElementById(
            "reviewBrowseFilesButton"
        );

    const clear =
        document.getElementById(
            "reviewClearFilesButton"
        );

    const form =
        document.getElementById(
            "complaintReviewForm"
        );


    if (!input || !area) {

        return;

    }


    /* =====================================================
       CLICK UPLOAD AREA
    ===================================================== */

    area.addEventListener(
        "click",
        function (event) {

            /*
             * Do not trigger the input again when the
             * Browse Files button itself was clicked.
             */

            if (
                event.target.closest(
                    ".review-upload-browse"
                )
            ) {

                return;

            }


            /*
             * Ignore clicks coming from the actual
             * hidden file input.
             */

            if (
                event.target === input
            ) {

                return;

            }


            input.click();

        }
    );


    /* =====================================================
       KEYBOARD ACCESS
    ===================================================== */

    area.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Enter"
                ||
                event.key === " "
            ) {

                event.preventDefault();

                input.click();

            }

        }
    );


    /* =====================================================
       BROWSE FILES BUTTON
    ===================================================== */

    if (browse) {

        browse.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                input.click();

            }
        );

    }


    /* =====================================================
       FILE INPUT CHANGE
    ===================================================== */

    input.addEventListener(
        "change",
        function () {

            const files =
                Array.from(
                    input.files || []
                );


            addReviewFiles(
                files
            );

        }
    );


    /* =====================================================
       DRAG ENTER
    ===================================================== */

    area.addEventListener(
        "dragenter",
        function (event) {

            event.preventDefault();
            event.stopPropagation();

            area.classList.add(
                "is-dragging"
            );

        }
    );


    /* =====================================================
       DRAG OVER
    ===================================================== */

    area.addEventListener(
        "dragover",
        function (event) {

            event.preventDefault();
            event.stopPropagation();

            area.classList.add(
                "is-dragging"
            );

        }
    );


    /* =====================================================
       DRAG LEAVE
    ===================================================== */

    area.addEventListener(
        "dragleave",
        function (event) {

            event.preventDefault();
            event.stopPropagation();


            /*
             * Prevent the drag style from disappearing
             * when moving between children inside the
             * upload area.
             */

            if (
                event.relatedTarget
                &&
                area.contains(
                    event.relatedTarget
                )
            ) {

                return;

            }


            area.classList.remove(
                "is-dragging"
            );

        }
    );


    /* =====================================================
       DROP FILES
    ===================================================== */

    area.addEventListener(
        "drop",
        function (event) {

            event.preventDefault();
            event.stopPropagation();


            area.classList.remove(
                "is-dragging"
            );


            const files =
                Array.from(
                    event.dataTransfer
                        ? event.dataTransfer.files
                        : []
                );


            if (
                files.length === 0
            ) {

                return;

            }


            addReviewFiles(
                files
            );

        }
    );


    /* =====================================================
       CLEAR ALL FILES
    ===================================================== */

    if (clear) {

        clear.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();


                clearReviewSelectedFiles();

            }
        );

    }


    /* =====================================================
       FORM SUBMISSION VALIDATION
    ===================================================== */

    if (form) {

        form.addEventListener(
            "submit",
            function (event) {

                const validationResult =
                    validateAllReviewFiles();


                if (
                    validationResult !== true
                ) {

                    event.preventDefault();


                    showReviewUploadError(
                        validationResult
                    );


                    const uploadArea =
                        document.getElementById(
                            "reviewUploadArea"
                        );


                    if (uploadArea) {

                        uploadArea.scrollIntoView({
                            behavior: "smooth",
                            block: "center"
                        });

                    }

                }

            }
        );

    }


    /* =====================================================
       INITIAL RENDER
    ===================================================== */

    renderReviewSelectedFiles();

}


/* =========================================================
   ADD REVIEW FILES
========================================================= */

function addReviewFiles(files) {

    clearReviewUploadError();


    if (
        !Array.isArray(files)
        ||
        files.length === 0
    ) {

        return;

    }


    let errorMessages = [];


    files.forEach(
        function (file) {

            /*
             * Maximum file count
             */

            if (
                reviewSelectedFiles.length
                >=
                REVIEW_MAX_FILES
            ) {

                const message =
                    "You can upload a maximum of "
                    +
                    REVIEW_MAX_FILES
                    +
                    " files at a time.";


                if (
                    !errorMessages.includes(
                        message
                    )
                ) {

                    errorMessages.push(
                        message
                    );

                }


                return;

            }


            /*
             * Validate file
             */

            const validation =
                validateReviewFile(
                    file
                );


            if (
                validation !== true
            ) {

                errorMessages.push(
                    validation
                );

                return;

            }


            /*
             * Prevent duplicates
             */

            if (
                isDuplicateReviewFile(
                    file
                )
            ) {

                errorMessages.push(
                    file.name
                    +
                    " is already selected."
                );

                return;

            }


            /*
             * Add valid file
             */

            reviewSelectedFiles.push(
                file
            );

        }
    );


    syncReviewFileInput();

    renderReviewSelectedFiles();


    if (
        errorMessages.length > 0
    ) {

        showReviewUploadError(
            errorMessages.join(
                " "
            )
        );

    }

}


/* =========================================================
   VALIDATE SINGLE FILE
========================================================= */

function validateReviewFile(file) {

    if (!file) {

        return "Invalid file selected.";

    }


    /* =====================================================
       FILE SIZE
    ===================================================== */

    if (
        file.size >
        REVIEW_MAX_FILE_SIZE
    ) {

        return (
            file.name
            +
            " exceeds the 10MB file size limit."
        );

    }


    /* =====================================================
       EMPTY FILE
    ===================================================== */

    if (
        file.size <= 0
    ) {

        return (
            file.name
            +
            " is empty and cannot be uploaded."
        );

    }


    /* =====================================================
       FILE EXTENSION
    ===================================================== */

    const extension =
        getReviewFileExtension(
            file.name
        );


    if (
        !REVIEW_ALLOWED_EXTENSIONS.includes(
            extension
        )
    ) {

        return (
            file.name
            +
            " has an unsupported file type."
        );

    }


    return true;

}


/* =========================================================
   VALIDATE ALL SELECTED FILES
========================================================= */

function validateAllReviewFiles() {

    if (
        reviewSelectedFiles.length >
        REVIEW_MAX_FILES
    ) {

        return (
            "You can upload a maximum of "
            +
            REVIEW_MAX_FILES
            +
            " files at a time."
        );

    }


    for (
        let index = 0;
        index < reviewSelectedFiles.length;
        index++
    ) {

        const validation =
            validateReviewFile(
                reviewSelectedFiles[index]
            );


        if (
            validation !== true
        ) {

            return validation;

        }

    }


    return true;

}


/* =========================================================
   CHECK DUPLICATE FILE
========================================================= */

function isDuplicateReviewFile(file) {

    return reviewSelectedFiles.some(
        function (existing) {

            return (
                existing.name === file.name
                &&
                existing.size === file.size
                &&
                existing.lastModified
                ===
                file.lastModified
            );

        }
    );

}


/* =========================================================
   GET FILE EXTENSION
========================================================= */

function getReviewFileExtension(
    fileName
) {

    const name =
        String(
            fileName || ""
        ).toLowerCase();


    const index =
        name.lastIndexOf(
            "."
        );


    if (
        index === -1
    ) {

        return "";

    }


    return name.substring(
        index
    );

}


/* =========================================================
   SYNC SELECTED FILES WITH INPUT
========================================================= */

function syncReviewFileInput() {

    const input =
        document.getElementById(
            "reviewEvidenceFiles"
        );


    if (!input) {

        return;

    }


    /*
     * DataTransfer allows us to rebuild the
     * FileList after removing individual files.
     */

    if (
        typeof DataTransfer ===
        "undefined"
    ) {

        return;

    }


    const transfer =
        new DataTransfer();


    reviewSelectedFiles.forEach(
        function (file) {

            transfer.items.add(
                file
            );

        }
    );


    input.files =
        transfer.files;

}


/* =========================================================
   RENDER SELECTED FILES
========================================================= */

function renderReviewSelectedFiles() {

    const container =
        document.getElementById(
            "reviewSelectedFiles"
        );

    const list =
        document.getElementById(
            "reviewSelectedFilesList"
        );

    const count =
        document.getElementById(
            "reviewUploadCount"
        );


    if (
        !container
        ||
        !list
        ||
        !count
    ) {

        return;

    }


    /* =====================================================
       CLEAR CURRENT LIST
    ===================================================== */

    list.innerHTML =
        "";


    /* =====================================================
       UPDATE FILE COUNT
    ===================================================== */

    count.textContent =
        reviewSelectedFiles.length
        +
        (
            reviewSelectedFiles.length === 1
                ? " file selected"
                : " files selected"
        );


    /* =====================================================
       EMPTY STATE
    ===================================================== */

    if (
        reviewSelectedFiles.length === 0
    ) {

        container.hidden =
            true;

        return;

    }


    container.hidden =
        false;


    /* =====================================================
       CREATE FILE ROWS
    ===================================================== */

    reviewSelectedFiles.forEach(
        function (
            file,
            index
        ) {

            const item =
                createReviewSelectedFileItem(
                    file,
                    index
                );


            list.appendChild(
                item
            );

        }
    );

}


/* =========================================================
   CREATE SELECTED FILE ITEM
========================================================= */

function createReviewSelectedFileItem(
    file,
    index
) {

    const item =
        document.createElement(
            "div"
        );


    item.className =
        "review-selected-file";


    /* =====================================================
       FILE ICON
    ===================================================== */

    const icon =
        document.createElement(
            "div"
        );


    icon.className =
        "review-selected-file-icon";


    icon.textContent =
        getReviewUploadFileLabel(
            file
        );


    /* =====================================================
       FILE INFORMATION
    ===================================================== */

    const info =
        document.createElement(
            "div"
        );


    info.className =
        "review-selected-file-info";


    const name =
        document.createElement(
            "strong"
        );


    name.textContent =
        file.name;


    name.title =
        file.name;


    const details =
        document.createElement(
            "span"
        );


    details.textContent =
        formatReviewFileSize(
            file.size
        )
        +
        " • "
        +
        getReviewUploadFileType(
            file
        );


    info.appendChild(
        name
    );


    info.appendChild(
        details
    );


    /* =====================================================
       REMOVE BUTTON
    ===================================================== */

    const remove =
        document.createElement(
            "button"
        );


    remove.type =
        "button";


    remove.className =
        "review-selected-file-remove";


    remove.setAttribute(
        "aria-label",
        "Remove "
        +
        file.name
    );


    remove.setAttribute(
        "title",
        "Remove file"
    );


    remove.textContent =
        "×";


    remove.addEventListener(
        "click",
        function (event) {

            event.preventDefault();
            event.stopPropagation();


            removeReviewSelectedFile(
                index
            );

        }
    );


    /* =====================================================
       APPEND ELEMENTS
    ===================================================== */

    item.appendChild(
        icon
    );


    item.appendChild(
        info
    );


    item.appendChild(
        remove
    );


    return item;

}


/* =========================================================
   REMOVE SELECTED FILE
========================================================= */

function removeReviewSelectedFile(
    index
) {

    if (
        index < 0
        ||
        index >=
            reviewSelectedFiles.length
    ) {

        return;

    }


    reviewSelectedFiles.splice(
        index,
        1
    );


    clearReviewUploadError();

    syncReviewFileInput();

    renderReviewSelectedFiles();

}


/* =========================================================
   CLEAR ALL SELECTED FILES
========================================================= */

function clearReviewSelectedFiles() {

    reviewSelectedFiles =
        [];


    const input =
        document.getElementById(
            "reviewEvidenceFiles"
        );


    if (input) {

        input.value =
            "";

    }


    clearReviewUploadError();

    syncReviewFileInput();

    renderReviewSelectedFiles();

}


/* =========================================================
   RESET REVIEW FILE UPLOAD
========================================================= */

function resetReviewFileUpload() {

    reviewSelectedFiles =
        [];


    const input =
        document.getElementById(
            "reviewEvidenceFiles"
        );

    const area =
        document.getElementById(
            "reviewUploadArea"
        );


    if (input) {

        input.value =
            "";

    }


    if (area) {

        area.classList.remove(
            "is-dragging"
        );

    }


    clearReviewUploadError();

    renderReviewSelectedFiles();

}


/* =========================================================
   GET FILE LABEL
========================================================= */

function getReviewUploadFileLabel(
    file
) {

    const type =
        String(
            file.type || ""
        ).toLowerCase();


    const name =
        String(
            file.name || ""
        ).toLowerCase();


    /* IMAGE */

    if (
        type.startsWith(
            "image/"
        )
        ||
        /\.(jpg|jpeg|png|gif|webp)$/i.test(
            name
        )
    ) {

        return "IMG";

    }


    /* VIDEO */

    if (
        type.startsWith(
            "video/"
        )
        ||
        /\.(mp4|webm|mov)$/i.test(
            name
        )
    ) {

        return "VID";

    }


    /* AUDIO */

    if (
        type.startsWith(
            "audio/"
        )
        ||
        /\.(mp3|wav|ogg|m4a|aac)$/i.test(
            name
        )
    ) {

        return "AUD";

    }


    /* PDF */

    if (
        type.includes(
            "pdf"
        )
        ||
        name.endsWith(
            ".pdf"
        )
    ) {

        return "PDF";

    }


    /* WORD DOCUMENT */

    if (
        name.endsWith(
            ".doc"
        )
        ||
        name.endsWith(
            ".docx"
        )
    ) {

        return "DOC";

    }


    return "FILE";

}


/* =========================================================
   GET FRIENDLY FILE TYPE
========================================================= */

function getReviewUploadFileType(
    file
) {

    const label =
        getReviewUploadFileLabel(
            file
        );


    switch (label) {

        case "IMG":

            return "Image";


        case "VID":

            return "Video";


        case "AUD":

            return "Audio";


        case "PDF":

            return "PDF";


        case "DOC":

            return "Document";


        default:

            return "File";

    }

}


/* =========================================================
   FORMAT FILE SIZE
========================================================= */

function formatReviewFileSize(
    bytes
) {

    const size =
        Number(
            bytes || 0
        );


    if (
        !Number.isFinite(
            size
        )
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

                Math.log(
                    size
                )
                /
                Math.log(
                    1024
                )

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
   SHOW UPLOAD ERROR
========================================================= */

function showReviewUploadError(
    message
) {

    const error =
        document.getElementById(
            "reviewUploadError"
        );


    if (!error) {

        return;

    }


    error.textContent =
        message || "Unable to add the selected file.";


    error.hidden =
        false;

}


/* =========================================================
   CLEAR UPLOAD ERROR
========================================================= */

function clearReviewUploadError() {

    const error =
        document.getElementById(
            "reviewUploadError"
        );


    if (!error) {

        return;

    }


    error.textContent =
        "";


    error.hidden =
        true;

}


/* =========================================================
   RESET FILES WHEN COMPLAINT REVIEW CLOSES
========================================================= */

/*
 * Your complaint review modal is controlled by
 * complaint_review.js.
 *
 * This event listener watches the buttons that close
 * the complaint review and clears files that have not
 * been submitted.
 */

document.addEventListener(
    "click",
    function (event) {

        const closeButton =
            event.target.closest(
                "[data-close-review]"
            );


        if (!closeButton) {

            return;

        }


        resetReviewFileUpload();

    }
);


/* =========================================================
   OPTIONAL GLOBAL FUNCTIONS
========================================================= */

/*
 * These are exposed so complaint_review.js can reset the
 * uploader directly when needed.
 */

window.resetReviewFileUpload =
    resetReviewFileUpload;


window.clearReviewSelectedFiles =
    clearReviewSelectedFiles;