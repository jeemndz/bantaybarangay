/* =========================================================
   BANTAYBARANGAY
   COMPLAINT REVIEW MODAL
========================================================= */


/* =========================================================
   STATE
========================================================= */

let activeComplaintRow = null;


/* =========================================================
   DOCUMENT READY
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeComplaintReview();
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
       CLOSE REVIEW
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

            if (event.key !== "Escape") {

                return;

            }


            const evidencePreview =
                document.getElementById(
                    "evidencePreviewModal"
                );


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
        function (event) {

            /*
             * There must be an active complaint row.
             */

            if (!activeComplaintRow) {

                event.preventDefault();

                return;

            }


            /*
             * Determine whether this account has permission
             * to edit the complaint.
             */

            const canEdit =
                activeComplaintRow
                    .dataset
                    .canEdit === "true";


            /*
             * The backend also performs this ownership
             * validation. This JavaScript check is only
             * for the user interface.
             */

            if (!canEdit) {

                event.preventDefault();

                return;

            }


            const assignedOfficial =
                cleanReviewValue(
                    activeComplaintRow
                        .dataset
                        .assignedOfficial
                );


            const currentStatus =
                cleanReviewValue(
                    activeComplaintRow
                        .dataset
                        .status
                );


            const selectedStatus =
                document.getElementById(
                    "reviewStatus"
                );


            /*
             * A newly submitted and unassigned complaint
             * cannot skip directly to another workflow
             * status.
             *
             * It must first become Under Review.
             */

            if (
                !assignedOfficial
                &&
                currentStatus === "Submitted"
                &&
                selectedStatus
                &&
                selectedStatus.value !== "Submitted"
                &&
                selectedStatus.value !== "Under Review"
            ) {

                event.preventDefault();


                window.alert(
                    "A newly submitted complaint must first be changed to Under Review."
                );


                return;

            }


            /* =================================================
               SAVING STATE
            ================================================= */

            const button =
                document.getElementById(
                    "reviewSaveButton"
                );


            if (!button) {

                return;

            }


            button.disabled =
                true;


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


    /* =====================================================
       SAVE ACTIVE COMPLAINT
    ===================================================== */

    activeComplaintRow =
        row;


    const complaintId =
        row.dataset.complaintId
        ||
        "";


    /* =====================================================
       COMPLAINT REFERENCE
    ===================================================== */

    setReviewText(
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

    setReviewText(
        "reviewComplainant",
        row.dataset.complainant
    );


    setReviewText(
        "reviewReportType",
        row.dataset.reportType
    );


    setReviewText(
        "reviewCategory",
        row.dataset.category
    );


    setReviewText(
        "reviewIncidentDate",
        row.dataset.incidentDate
    );


    setReviewText(
        "reviewIncidentTime",
        row.dataset.incidentTime
    );


    setReviewText(
        "reviewLocation",
        row.dataset.location
    );


    setReviewText(
        "reviewSubject",
        row.dataset.subject
    );


    setReviewText(
        "reviewDescription",
        row.dataset.description
    );


    /* =====================================================
       RESPONDENT INFORMATION
    ===================================================== */

    setReviewText(
        "reviewRespondentName",
        row.dataset.respondentName
    );


    setReviewText(
        "reviewRespondentRelationship",
        row.dataset.respondentRelationship
    );


    setReviewText(
        "reviewRespondentContact",
        row.dataset.respondentContact
    );


    setReviewText(
        "reviewRespondentAddress",
        row.dataset.respondentAddress
    );


    const respondentSection =
        document.getElementById(
            "reviewRespondentSection"
        );


    const hasRespondent =
        Boolean(
            cleanReviewValue(
                row.dataset.respondentName
            )
        )
        ||
        Boolean(
            cleanReviewValue(
                row.dataset.respondentAddress
            )
        )
        ||
        Boolean(
            cleanReviewValue(
                row.dataset.respondentRelationship
            )
        )
        ||
        Boolean(
            cleanReviewValue(
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

        }
        else {

            respondentSection
                .classList
                .remove(
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
       ASSIGNED HANDLER
    ===================================================== */

    updateAssignedHandlerDisplay(
        row
    );


    /* =====================================================
       EDIT PERMISSIONS
    ===================================================== */

    updateComplaintEditPermissions(
        row
    );


    /* =====================================================
       RESET SAVE BUTTON
    ===================================================== */

    const saveButton =
        document.getElementById(
            "reviewSaveButton"
        );


    const canEdit =
        row.dataset.canEdit === "true";


    if (saveButton) {

        saveButton.disabled =
            !canEdit;


        saveButton.hidden =
            !canEdit;


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
       UPDATE FORM ACTION
    ===================================================== */

    const urlTemplate =
        form.dataset.updateUrlTemplate;


    if (
        urlTemplate
        &&
        complaintId
    ) {

        form.action =
            replaceReviewUrlId(
                urlTemplate,
                complaintId
            );

    }


    /* =====================================================
       OPEN MODAL
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
       LOAD EVIDENCE
    ===================================================== */

    loadComplaintEvidence(
        complaintId
    );

}


/* =========================================================
   ASSIGNED HANDLER DISPLAY
========================================================= */

function updateAssignedHandlerDisplay(row) {

    const assignedOfficial =
        cleanReviewValue(
            row.dataset.assignedOfficial
        );


    const assignedUsername =
        cleanReviewValue(
            row.dataset.assignedUsername
        );


    const assignedRole =
        cleanReviewValue(
            row.dataset.assignedRole
        );


    const currentUser =
        getComplaintCurrentUser();


    const name =
        document.getElementById(
            "assignedOfficialName"
        );


    const role =
        document.getElementById(
            "assignedOfficialRole"
        );


    const avatar =
        document.getElementById(
            "assignedOfficialAvatar"
        );


    const badge =
        document.getElementById(
            "assignedOfficialBadge"
        );


    const badgeText =
        document.getElementById(
            "assignedOfficialBadgeText"
        );


    const helper =
        document.getElementById(
            "assignedOfficialHelper"
        );


    /* =====================================================
       UNASSIGNED
    ===================================================== */

    if (!assignedOfficial) {

        if (name) {

            name.textContent =
                "Unassigned";

        }


        if (role) {

            role.textContent =
                "No handler assigned";

        }


        if (avatar) {

            avatar.textContent =
                "?";

        }


        if (badgeText) {

            badgeText.textContent =
                "Unassigned";

        }


        if (badge) {

            badge.classList.remove(
                "assigned-to-you"
            );


            badge.classList.remove(
                "assigned-to-other"
            );


            badge.classList.add(
                "unassigned"
            );

        }


        if (helper) {

            helper.textContent =
                "Change the status from Submitted to Under Review to assign this complaint to your account.";

        }


        return;

    }


    /* =====================================================
       ASSIGNED USER
    ===================================================== */

    if (name) {

        name.textContent =
            assignedUsername
            ||
            "Assigned User";

    }


    if (role) {

        role.textContent =
            formatComplaintRole(
                assignedRole
            );

    }


    if (avatar) {

        avatar.textContent =
            (
                assignedUsername
                ||
                "U"
            )
            .charAt(0)
            .toUpperCase();

    }


    /* =====================================================
       ASSIGNED TO CURRENT USER
    ===================================================== */

    if (
        currentUser.id
        &&
        String(
            currentUser.id
        )
        ===
        String(
            assignedOfficial
        )
    ) {

        if (badgeText) {

            badgeText.textContent =
                "Assigned to You";

        }


        if (badge) {

            badge.classList.remove(
                "unassigned"
            );


            badge.classList.remove(
                "assigned-to-other"
            );


            badge.classList.add(
                "assigned-to-you"
            );

        }


        if (helper) {

            helper.textContent =
                "You are responsible for handling and updating this complaint.";

        }


        return;

    }


    /* =====================================================
       ASSIGNED TO ANOTHER USER
    ===================================================== */

    if (badgeText) {

        badgeText.textContent =
            "Assigned Handler";

    }


    if (badge) {

        badge.classList.remove(
            "unassigned"
        );


        badge.classList.remove(
            "assigned-to-you"
        );


        badge.classList.add(
            "assigned-to-other"
        );

    }


    if (helper) {

        helper.textContent =
            "This complaint is being handled by another Admin or Barangay Official. You have view-only access.";

    }

}


/* =========================================================
   COMPLAINT EDIT PERMISSIONS
========================================================= */

function updateComplaintEditPermissions(row) {

    const canEdit =
        row.dataset.canEdit === "true";


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


    const evidenceInput =
        document.getElementById(
            "reviewEvidenceFiles"
        );


    const browseButton =
        document.getElementById(
            "reviewBrowseFilesButton"
        );


    const clearButton =
        document.getElementById(
            "reviewClearFilesButton"
        );


    const uploadArea =
        document.getElementById(
            "reviewUploadArea"
        );


    const uploadSection =
        document.getElementById(
            "reviewUploadSection"
        );


    const saveButton =
        document.getElementById(
            "reviewSaveButton"
        );


    const lockedNotice =
        document.getElementById(
            "complaintLockedNotice"
        );


    /* =====================================================
       PRIORITY
    ===================================================== */

    if (priority) {

        priority.disabled =
            !canEdit;

    }


    /* =====================================================
       STATUS
    ===================================================== */

    if (status) {

        status.disabled =
            !canEdit;

    }


    /* =====================================================
       RESOLUTION
    ===================================================== */

    if (resolution) {

        resolution.disabled =
            !canEdit;

    }


    /* =====================================================
       FILE INPUT
    ===================================================== */

    if (evidenceInput) {

        evidenceInput.disabled =
            !canEdit;

    }


    /* =====================================================
       BROWSE BUTTON
    ===================================================== */

    if (browseButton) {

        browseButton.disabled =
            !canEdit;

    }


    /* =====================================================
       CLEAR BUTTON
    ===================================================== */

    if (clearButton) {

        clearButton.disabled =
            !canEdit;

    }


    /* =====================================================
       UPLOAD AREA
    ===================================================== */

    if (uploadArea) {

        if (canEdit) {

            uploadArea.classList.remove(
                "review-upload-disabled"
            );


            uploadArea.removeAttribute(
                "aria-disabled"
            );


            uploadArea.setAttribute(
                "tabindex",
                "0"
            );

        }
        else {

            uploadArea.classList.add(
                "review-upload-disabled"
            );


            uploadArea.setAttribute(
                "aria-disabled",
                "true"
            );


            uploadArea.setAttribute(
                "tabindex",
                "-1"
            );

        }

    }


    /* =====================================================
       UPLOAD SECTION
    ===================================================== */

    if (uploadSection) {

        if (canEdit) {

            uploadSection.classList.remove(
                "review-section-readonly"
            );

        }
        else {

            uploadSection.classList.add(
                "review-section-readonly"
            );

        }

    }


    /* =====================================================
       SAVE BUTTON
    ===================================================== */

    if (saveButton) {

        saveButton.disabled =
            !canEdit;


        saveButton.hidden =
            !canEdit;

    }


    /* =====================================================
       LOCK NOTICE
    ===================================================== */

    if (lockedNotice) {

        lockedNotice.hidden =
            canEdit;

    }

}


/* =========================================================
   GET CURRENT LOGGED-IN USER
========================================================= */

function getComplaintCurrentUser() {

    const element =
        document.getElementById(
            "complaintCurrentUser"
        );


    if (!element) {

        return {

            id: "",
            username: "",
            role: ""

        };

    }


    return {

        id:
            cleanReviewValue(
                element.dataset.userId
            ),

        username:
            cleanReviewValue(
                element.dataset.username
            ),

        role:
            cleanReviewValue(
                element.dataset.role
            )

    };

}


/* =========================================================
   FORMAT COMPLAINT USER ROLE
========================================================= */

function formatComplaintRole(role) {

    if (role === "admin") {

        return "Administrator";

    }


    if (role === "official") {

        return "Barangay Official";

    }


    return (
        role
        ||
        "Assigned User"
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


    const emptyMessage =
        empty.querySelector(
            "span"
        );


    if (emptyMessage) {

        emptyMessage.textContent =
            "This complaint does not currently have any uploaded evidence.";

    }


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
        replaceReviewUrlId(
            template,
            complaintId
        );


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


        count.textContent =
            evidence.length
            +
            (
                evidence.length === 1
                    ? " file"
                    : " files"
            );


        if (
            evidence.length === 0
        ) {

            empty.hidden =
                false;


            return;

        }


        evidence.forEach(
            function (item) {

                grid.appendChild(
                    createEvidenceCard(
                        item
                    )
                );

            }
        );


        grid.hidden =
            false;

    }
    catch (error) {

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
        "div"
    );

button.className =
    "review-evidence-item";

button.setAttribute(
    "role",
    "button"
);

button.setAttribute(
    "tabindex",
    "0"
);


    const kind =
        determineEvidenceKind(
            item.file_type,
            item.file_name
        );


    button.dataset.kind =
        kind;


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

    if (kind === "video") {

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
       VERIFIED
    ===================================================== */

    /* =====================================================
   BLOCKCHAIN / INTEGRITY STATUS
===================================================== */

const blockchainStatus =
    cleanReviewValue(
        item.blockchain_status
    );

const integrityStatus =
    cleanReviewValue(
        item.integrity_status
    );

const statusBadge =
    document.createElement(
        "span"
    );

statusBadge.className =
    "review-evidence-verified";


if (integrityStatus === "Verified") {

    statusBadge.textContent =
        "Verified";

}
else if (integrityStatus === "Failed") {

    statusBadge.textContent =
        "Integrity Failed";

}
else if (blockchainStatus === "Registered") {

    statusBadge.textContent =
        "Registered";

}
else if (blockchainStatus === "Failed") {

    statusBadge.textContent =
        "Registration Failed";

}
else {

    statusBadge.textContent =
        "Pending Registration";

}


preview.appendChild(
    statusBadge
);


    /* =====================================================
       FILE INFORMATION
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
   BLOCKCHAIN ACTION
===================================================== */

const blockchainAction =
    document.createElement(
        "button"
    );

blockchainAction.type =
    "button";

blockchainAction.className =
    "review-evidence-blockchain-action";


if (integrityStatus === "Verified") {

    blockchainAction.textContent =
        "Verified";

    blockchainAction.disabled =
        true;

}
else if (blockchainStatus === "Registered") {

    blockchainAction.textContent =
        "Verify Integrity";

    blockchainAction.addEventListener(
        "click",
        function (event) {

            event.preventDefault();
            event.stopPropagation();

            verifyEvidenceOnBlockchain(
                item.evidence_id
            );

        }
    );

}
else {

    blockchainAction.textContent =
        blockchainStatus === "Failed"
            ? "Retry Registration"
            : "Register on Blockchain";

    blockchainAction.addEventListener(
        "click",
        function (event) {

            event.preventDefault();
            event.stopPropagation();

            registerEvidenceOnBlockchain(
                item.evidence_id
            );

        }
    );

}


info.appendChild(
    blockchainAction
);




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
   REGISTER EVIDENCE ON BLOCKCHAIN
========================================================= */

async function registerEvidenceOnBlockchain(evidenceId) {

    if (!evidenceId) {
        return;
    }

    const url =
        "/evidence/"
        + encodeURIComponent(evidenceId)
        + "/blockchain/register/";

    try {

        const response = await fetch(
            url,
            {
                method: "POST",

                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getReviewCsrfToken()
                },

                credentials: "same-origin"
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message
                || data.error
                || "Blockchain registration failed."
            );

        }

        window.alert(
            data.message
            || "Evidence successfully registered on Hyperledger Fabric."
        );

        if (activeComplaintRow) {

            loadComplaintEvidence(
                activeComplaintRow.dataset.complaintId
            );

        }

    }
    catch (error) {

        console.error(
            "Blockchain registration error:",
            error
        );

        window.alert(
            error.message
            || "Unable to register evidence on the blockchain."
        );

    }
}


/* =========================================================
   VERIFY EVIDENCE INTEGRITY
========================================================= */

async function verifyEvidenceOnBlockchain(evidenceId) {

    if (!evidenceId) {
        return;
    }

    const url =
        "/evidence/"
        + encodeURIComponent(evidenceId)
        + "/blockchain/verify/";

    try {

        const response = await fetch(
            url,
            {
                method: "POST",

                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getReviewCsrfToken()
                },

                credentials: "same-origin"
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message
                || data.error
                || "Evidence verification failed."
            );

        }

        if (data.verified) {

            window.alert(
                "Evidence integrity verified successfully."
            );

        }
        else {

            window.alert(
                "Integrity verification failed. The current file does not match the hash registered on Hyperledger Fabric."
            );

        }

        if (activeComplaintRow) {

            loadComplaintEvidence(
                activeComplaintRow.dataset.complaintId
            );

        }

    }
    catch (error) {

        console.error(
            "Evidence verification error:",
            error
        );

        window.alert(
            error.message
            || "Unable to verify evidence integrity."
        );

    }
}


/* =========================================================
   GET CSRF TOKEN
========================================================= */

function getReviewCsrfToken() {

    const cookies =
        document.cookie
            .split(";")
            .map(function (cookie) {
                return cookie.trim();
            });

    const csrfCookie =
        cookies.find(function (cookie) {
            return cookie.startsWith("csrftoken=");
        });

    if (!csrfCookie) {
        return "";
    }

    return decodeURIComponent(
        csrfCookie.substring(
            "csrftoken=".length
        )
    );
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


    if (
        type.startsWith(
            "image/"
        )
        ||
        /\.(jpg|jpeg|png|gif|webp|bmp)$/i.test(
            name
        )
    ) {

        return "image";

    }


    if (
        type.startsWith(
            "video/"
        )
        ||
        /\.(mp4|webm|mov|m4v|ogv)$/i.test(
            name
        )
    ) {

        return "video";

    }


    if (
        type.startsWith(
            "audio/"
        )
        ||
        /\.(mp3|wav|ogg|m4a|aac|flac)$/i.test(
            name
        )
    ) {

        return "audio";

    }


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

        image: "IMG",

        video: "VIDEO",

        audio: "AUDIO",

        pdf: "PDF",

        document: "FILE"

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


    content.innerHTML =
        "";


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


    if (original) {

        if (
            cleanReviewValue(
                item.file_path
            )
        ) {

            original.href =
                item.file_path;


            original.style.display =
                "inline-flex";

        }
        else {

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
       DOCUMENT
    ===================================================== */

    else {

        createDocumentFallback(
            content,
            kind
        );

    }


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
        "Preview is not available for this file type. "
        +
        "Use Open Original to view or download the file.";


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


    closeEvidencePreview();


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
       RESET ACTIVE COMPLAINT
    ===================================================== */

    activeComplaintRow =
        null;


    /* =====================================================
       RESET EVIDENCE
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

            ? value.toFixed(
                0
            )

            : value.toFixed(
                1
            );


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
========================================================= */

function replaceReviewUrlId(
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


    if (
        template.includes(
            "/0/"
        )
    ) {

        return template.replace(

            "/0/",

            "/"
            +
            encodeURIComponent(
                id
            )
            +
            "/"

        );

    }


    return template.replace(

        /0(?=\/?$)/,

        encodeURIComponent(
            id
        )

    );

}


/* =========================================================
   SET TEXT
========================================================= */

function setReviewText(
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
        cleanReviewValue(
            value
        )
        ||
        "—";

}


/* =========================================================
   CLEAN VALUE
========================================================= */

function cleanReviewValue(value) {

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