/* =========================================================
   BANTAYBARANGAY
   EVIDENCE MANAGEMENT
========================================================= */

document.addEventListener("DOMContentLoaded", function () {


    /* =====================================================
       ELEMENTS
    ====================================================== */

    const evidenceGrid =
        document.getElementById("evidenceGrid");

    const categoryCards =
        Array.from(
            document.querySelectorAll(
                ".evidence-category-card"
            )
        );

    const showAllButton =
        document.getElementById("showAllCategories");

    const searchInput =
        document.getElementById("evidenceSearch");

    const clearSearchButton =
        document.getElementById("clearEvidenceSearch");

    const sortSelect =
        document.getElementById("sortEvidence");

    const gridViewButton =
        document.getElementById("gridViewButton");

    const listViewButton =
        document.getElementById("listViewButton");

    const detailsPanel =
        document.getElementById("evidenceDetailsPanel");

    const closeDetailsButton =
        document.getElementById("closeEvidenceDetails");

    const emptyState =
        document.getElementById("evidenceEmptyState");

    const databaseEmptyState =
        document.getElementById("databaseEmptyState");

    const dropZone =
        document.getElementById("dropZone");

    const browseButton =
        document.getElementById("browseFiles");

    const fileInput =
        document.getElementById("fileInput");


    /* =====================================================
       CURRENT CATEGORY
    ====================================================== */

    let currentCategory = "all";


    /* =====================================================
       GET EVIDENCE CARDS
    ====================================================== */

    function getEvidenceCards() {

        if (!evidenceGrid) {
            return [];
        }

        return Array.from(
            evidenceGrid.querySelectorAll(
                ".evidence-file-card"
            )
        );
    }


    /* =====================================================
       NORMALIZE CATEGORY
    ====================================================== */

    function normalizeCategory(value) {

        const type =
            String(value || "")
                .toLowerCase()
                .trim();


        if (
            type.includes("image") ||
            type.includes("photo") ||
            type.includes("jpg") ||
            type.includes("jpeg") ||
            type.includes("png") ||
            type.includes("gif") ||
            type.includes("webp")
        ) {
            return "photos";
        }


        if (
            type.includes("video") ||
            type.includes("mp4") ||
            type.includes("webm") ||
            type.includes("mov") ||
            type.includes("avi")
        ) {
            return "videos";
        }


        if (
            type.includes("audio") ||
            type.includes("mp3") ||
            type.includes("wav") ||
            type.includes("m4a") ||
            type.includes("ogg")
        ) {
            return "audio";
        }


        if (
            type.includes("complaint")
        ) {
            return "complaints";
        }


        if (
            type.includes("incident")
        ) {
            return "incidents";
        }


        return "documents";
    }


    /* =====================================================
       UPDATE CATEGORY COUNTS
    ====================================================== */

    function updateCategoryCounts() {

        const counts = {
            photos: 0,
            videos: 0,
            audio: 0,
            documents: 0
        };


        getEvidenceCards().forEach(function (card) {

            const category =
                normalizeCategory(
                    card.dataset.category
                );

            if (
                Object.prototype.hasOwnProperty.call(
                    counts,
                    category
                )
            ) {
                counts[category]++;
            }

        });


        const photoCount =
            document.getElementById("photoCount");

        const videoCount =
            document.getElementById("videoCount");

        const audioCount =
            document.getElementById("audioCount");

        const documentCount =
            document.getElementById("documentCount");


        if (photoCount) {
            photoCount.textContent =
                counts.photos;
        }

        if (videoCount) {
            videoCount.textContent =
                counts.videos;
        }

        if (audioCount) {
            audioCount.textContent =
                counts.audio;
        }

        if (documentCount) {
            documentCount.textContent =
                counts.documents;
        }
    }


    /* =====================================================
       CATEGORY FILTER
    ====================================================== */

    categoryCards.forEach(function (categoryCard) {

        categoryCard.addEventListener(
            "click",
            function () {

                const clickedCategory =
                    this.dataset.category || "all";


                /*
                 * Clicking the active category again
                 * resets the filter.
                 */

                if (
                    this.classList.contains("active")
                ) {

                    currentCategory = "all";

                    categoryCards.forEach(
                        function (card) {

                            card.classList.remove(
                                "active"
                            );

                        }
                    );

                } else {

                    categoryCards.forEach(
                        function (card) {

                            card.classList.remove(
                                "active"
                            );

                        }
                    );


                    this.classList.add("active");

                    currentCategory =
                        clickedCategory;
                }


                filterEvidence();

            }
        );

    });


    /* =====================================================
       SEE ALL
    ====================================================== */

    if (showAllButton) {

        showAllButton.addEventListener(
            "click",
            function () {

                currentCategory = "all";


                categoryCards.forEach(
                    function (card) {

                        card.classList.remove(
                            "active"
                        );

                    }
                );


                filterEvidence();

            }
        );

    }


    /* =====================================================
       SEARCH
    ====================================================== */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            function () {

                if (clearSearchButton) {

                    clearSearchButton.hidden =
                        this.value.trim() === "";

                }

                filterEvidence();

            }
        );

    }


    /* =====================================================
       CLEAR SEARCH
    ====================================================== */

    if (clearSearchButton) {

        clearSearchButton.addEventListener(
            "click",
            function () {

                if (!searchInput) {
                    return;
                }


                searchInput.value = "";

                clearSearchButton.hidden = true;

                filterEvidence();

                searchInput.focus();

            }
        );

    }


    /* =====================================================
       FILTER EVIDENCE
    ====================================================== */

    function filterEvidence() {

        const cards =
            getEvidenceCards();


        const query =
            searchInput
                ? searchInput.value
                    .trim()
                    .toLowerCase()
                : "";


        let visibleCount = 0;


        cards.forEach(function (card) {

            const fileName =
                String(
                    card.dataset.name || ""
                ).toLowerCase();


            const category =
                normalizeCategory(
                    card.dataset.category
                );


            /*
             * Search can also match the
             * category/type.
             */

            const searchableText =
                fileName + " " + category;


            const searchMatches =
                query === "" ||
                searchableText.includes(query);


            /*
             * Complaints and incidents are
             * special logical categories.
             *
             * If your backend later supplies
             * those exact file_type values,
             * they will automatically work.
             */

            const categoryMatches =
                currentCategory === "all" ||
                category === currentCategory;


            const visible =
                searchMatches &&
                categoryMatches;


            card.style.display =
                visible ? "" : "none";


            if (visible) {
                visibleCount++;
            }

        });


        /*
         * Show filter-empty state only when
         * database actually contains cards.
         */

        if (emptyState) {

            emptyState.hidden =
                cards.length === 0 ||
                visibleCount > 0;

        }


        /*
         * Database empty state is only for
         * truly empty repositories.
         */

        if (databaseEmptyState) {

            databaseEmptyState.style.display =
                cards.length === 0
                    ? ""
                    : "none";

        }

    }


    /* =====================================================
       GRID VIEW
    ====================================================== */

    if (gridViewButton && evidenceGrid) {

        gridViewButton.addEventListener(
            "click",
            function () {

                evidenceGrid.classList.remove(
                    "list-view"
                );

                gridViewButton.classList.add(
                    "active"
                );


                if (listViewButton) {

                    listViewButton.classList.remove(
                        "active"
                    );

                }

            }
        );

    }


    /* =====================================================
       LIST VIEW
    ====================================================== */

    if (listViewButton && evidenceGrid) {

        listViewButton.addEventListener(
            "click",
            function () {

                evidenceGrid.classList.add(
                    "list-view"
                );

                listViewButton.classList.add(
                    "active"
                );


                if (gridViewButton) {

                    gridViewButton.classList.remove(
                        "active"
                    );

                }

            }
        );

    }


    /* =====================================================
       EVIDENCE CARD CLICK
    ====================================================== */

    function bindEvidenceCards() {

        getEvidenceCards().forEach(
            function (card) {

                /*
                 * Avoid duplicate listeners.
                 */

                if (
                    card.dataset.clickBound === "true"
                ) {
                    return;
                }


                card.dataset.clickBound = "true";


                card.addEventListener(
                    "click",
                    function () {

                        getEvidenceCards().forEach(
                            function (item) {

                                item.classList.remove(
                                    "selected"
                                );

                            }
                        );


                        this.classList.add(
                            "selected"
                        );


                        updateDetailsFromCard(
                            this
                        );


                        if (detailsPanel) {

                            detailsPanel.classList.remove(
                                "closed"
                            );

                        }

                    }
                );

            }
        );

    }


    /* =====================================================
       DETAILS FROM CARD
    ====================================================== */

    function updateDetailsFromCard(card) {

        const detailName =
            document.getElementById(
                "detailName"
            );

        const detailModified =
            document.getElementById(
                "detailModified"
            );

        const detailType =
            document.getElementById(
                "detailType"
            );

        const detailSize =
            document.getElementById(
                "detailSize"
            );

        const detailHash =
            document.getElementById(
                "detailHash"
            );

        const detailImage =
            document.getElementById(
                "detailImage"
            );

        const detailPreviewFallback =
            document.getElementById(
                "detailPreviewFallback"
            );


        const name =
            card.dataset.name ||
            "Unnamed Evidence";

        const date =
            card.dataset.date || "—";

        const size =
            card.dataset.size || "—";

        const category =
            normalizeCategory(
                card.dataset.category
            );


        if (detailName) {
            detailName.textContent = name;
        }


        if (detailModified) {

            detailModified.textContent =
                date !== "—"
                    ? "Uploaded " + date
                    : "Upload date unavailable";

        }


        if (detailType) {

            detailType.textContent =
                capitalize(category);

        }


        if (detailSize) {

            detailSize.textContent =
                formatStoredSize(size);

        }


        /*
         * If the card has an image preview,
         * display it in the details panel.
         */

        const previewImage =
            card.querySelector(
                ".evidence-file-preview img"
            );


        if (
            previewImage &&
            detailImage &&
            detailPreviewFallback
        ) {

            detailImage.src =
                previewImage.src;

            detailImage.hidden = false;

            detailPreviewFallback.style.display =
                "none";

        } else {

            if (detailImage) {

                detailImage.hidden = true;

                detailImage.removeAttribute(
                    "src"
                );

            }


            if (detailPreviewFallback) {

                detailPreviewFallback.style.display =
                    "flex";

            }

        }


        /*
         * The current HTML doesn't expose
         * file_hash as a data attribute.
         * Preserve the existing message
         * rather than inventing a hash.
         */

        if (
            detailHash &&
            !detailHash.dataset.loaded
        ) {

            detailHash.textContent =
                "Hash information available after verification.";

        }

    }


    /* =====================================================
       CLOSE DETAILS
    ====================================================== */

    if (closeDetailsButton) {

        closeDetailsButton.addEventListener(
            "click",
            function () {

                if (detailsPanel) {

                    detailsPanel.classList.add(
                        "closed"
                    );

                }


                getEvidenceCards().forEach(
                    function (card) {

                        card.classList.remove(
                            "selected"
                        );

                    }
                );

            }
        );

    }


    /* =====================================================
       SORT
    ====================================================== */

    if (sortSelect) {

        sortSelect.addEventListener(
            "change",
            function () {

                sortEvidence(
                    this.value
                );

            }
        );

    }


    function sortEvidence(sortType) {

        if (!evidenceGrid) {
            return;
        }


        const cards =
            getEvidenceCards();


        cards.sort(function (a, b) {

            if (sortType === "newest") {

                return (
                    parseDate(b.dataset.date) -
                    parseDate(a.dataset.date)
                );

            }


            if (sortType === "oldest") {

                return (
                    parseDate(a.dataset.date) -
                    parseDate(b.dataset.date)
                );

            }


            if (sortType === "name") {

                return String(
                    a.dataset.name || ""
                ).localeCompare(
                    String(
                        b.dataset.name || ""
                    )
                );

            }


            if (sortType === "size") {

                return (
                    parseFloat(
                        b.dataset.size || 0
                    ) -
                    parseFloat(
                        a.dataset.size || 0
                    )
                );

            }


            return 0;

        });


        cards.forEach(function (card) {

            evidenceGrid.appendChild(card);

        });

    }


    /* =====================================================
       DROP ZONE
    ====================================================== */

    if (
        browseButton &&
        fileInput
    ) {

        browseButton.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();

                fileInput.click();

            }
        );

    }


    if (
        dropZone &&
        fileInput
    ) {

        dropZone.addEventListener(
            "click",
            function (event) {

                if (
                    browseButton &&
                    (
                        event.target === browseButton ||
                        browseButton.contains(
                            event.target
                        )
                    )
                ) {
                    return;
                }


                fileInput.click();

            }
        );


        dropZone.addEventListener(
            "dragenter",
            function (event) {

                event.preventDefault();

                this.classList.add(
                    "drag-active"
                );

            }
        );


        dropZone.addEventListener(
            "dragover",
            function (event) {

                event.preventDefault();

                this.classList.add(
                    "drag-active"
                );

            }
        );


        dropZone.addEventListener(
            "dragleave",
            function (event) {

                event.preventDefault();

                this.classList.remove(
                    "drag-active"
                );

            }
        );


        dropZone.addEventListener(
            "drop",
            function (event) {

                event.preventDefault();

                this.classList.remove(
                    "drag-active"
                );


                const files =
                    event.dataTransfer.files;


                if (!files.length) {
                    return;
                }


                /*
                 * Your Django upload form only
                 * accepts one file at a time.
                 */

                const file =
                    files[0];


                const maxSize =
                    500 * 1024 * 1024;


                if (file.size > maxSize) {

                    alert(
                        file.name +
                        " exceeds the maximum 500MB file size."
                    );

                    return;
                }


                /*
                 * Put the dropped file into
                 * the real file input so the
                 * Django form can upload it.
                 */

                try {

                    const transfer =
                        new DataTransfer();

                    transfer.items.add(file);

                    fileInput.files =
                        transfer.files;

                } catch (error) {

                    console.warn(
                        "Unable to assign dropped file:",
                        error
                    );

                }

            }
        );

    }


    /* =====================================================
       RESIDENT SEARCH
    ====================================================== */

    const residentSearchInput =
        document.getElementById(
            "residentSearchInput"
        );

    const residentIdInput =
        document.getElementById(
            "residentIdInput"
        );

    const residentSearchResults =
        document.getElementById(
            "residentSearchResults"
        );

    const complaintSelect =
        document.getElementById(
            "complaintSelect"
        );

    const evidenceUploadForm =
        document.getElementById(
            "evidenceUploadForm"
        );


    const residents = [];


    document
        .querySelectorAll(".resident-data")
        .forEach(function (element) {

            residents.push({

                id:
                    element.dataset.id,

                firstName:
                    element.dataset.firstName || "",

                middleName:
                    element.dataset.middleName || "",

                lastName:
                    element.dataset.lastName || "",

                suffix:
                    element.dataset.suffix || ""

            });

        });


    /* =====================================================
       RESIDENT INPUT
    ====================================================== */

    if (
        residentSearchInput &&
        residentIdInput &&
        residentSearchResults &&
        complaintSelect
    ) {

        residentSearchInput.addEventListener(
            "input",
            function () {

                const search =
                    this.value
                        .trim()
                        .toLowerCase();


                /*
                 * Editing the text invalidates
                 * the previously selected ID.
                 */

                residentIdInput.value = "";


                complaintSelect.innerHTML =
                    '<option value="">' +
                    'Select Complaint' +
                    '</option>';


                complaintSelect.disabled = true;


                if (!search) {

                    residentSearchResults.innerHTML =
                        "";

                    residentSearchResults.classList.add(
                        "hidden"
                    );

                    return;
                }


                const filteredResidents =
                    residents.filter(
                        function (resident) {

                            const fullName =
                                getResidentFullName(
                                    resident
                                )
                                .toLowerCase();


                            return fullName.includes(
                                search
                            );

                        }
                    );


                residentSearchResults.innerHTML =
                    "";


                if (
                    filteredResidents.length === 0
                ) {

                    const noResult =
                        document.createElement(
                            "div"
                        );


                    noResult.className =
                        "resident-search-empty";


                    noResult.textContent =
                        "No residents found";


                    residentSearchResults.appendChild(
                        noResult
                    );


                    residentSearchResults.classList.remove(
                        "hidden"
                    );

                    return;
                }


                filteredResidents
                    .slice(0, 10)
                    .forEach(
                        function (resident) {

                            const fullName =
                                getResidentFullName(
                                    resident
                                );


                            const result =
                                document.createElement(
                                    "button"
                                );


                            result.type =
                                "button";


                            result.className =
                                "resident-search-item";


                            result.textContent =
                                fullName;


                            result.addEventListener(
                                "click",
                                function () {

                                    selectResident(
                                        resident,
                                        fullName
                                    );

                                }
                            );


                            residentSearchResults
                                .appendChild(
                                    result
                                );

                        }
                    );


                residentSearchResults.classList.remove(
                    "hidden"
                );

            }
        );


        /* =================================================
           SELECT RESIDENT
        ================================================= */

        function selectResident(
            resident,
            fullName
        ) {

            residentSearchInput.value =
                fullName;

            residentIdInput.value =
                resident.id;


            residentSearchResults.innerHTML =
                "";

            residentSearchResults.classList.add(
                "hidden"
            );


            loadResidentComplaints(
                resident.id
            );

        }


        /* =================================================
           LOAD COMPLAINTS
        ================================================= */

        function loadResidentComplaints(
            residentId
        ) {

            complaintSelect.innerHTML =
                '<option value="">' +
                'Loading complaints...' +
                '</option>';


            complaintSelect.disabled = true;


            const url =
                "/evidence/resident/" +
                encodeURIComponent(
                    residentId
                ) +
                "/complaints/";


            fetch(url, {
                method: "GET",
                headers: {
                    "X-Requested-With":
                        "XMLHttpRequest"
                }
            })

                .then(function (response) {

                    if (!response.ok) {

                        throw new Error(
                            "Failed to load complaints."
                        );

                    }

                    return response.json();

                })

                .then(function (data) {

                    complaintSelect.innerHTML =
                        '<option value="">' +
                        'Select Complaint' +
                        '</option>';


                    if (
                        !Array.isArray(
                            data.complaints
                        ) ||
                        data.complaints.length === 0
                    ) {

                        complaintSelect.innerHTML =
                            '<option value="">' +
                            'No complaints found' +
                            '</option>';


                        complaintSelect.disabled =
                            true;

                        return;
                    }


                    data.complaints.forEach(
                        function (complaint) {

                            const option =
                                document.createElement(
                                    "option"
                                );


                            option.value =
                                complaint.complaint_id;


                            option.textContent =
                                "#" +
                                complaint.complaint_id +
                                " - " +
                                (
                                    complaint.subject ||
                                    "Complaint"
                                ) +
                                (
                                    complaint.status
                                        ? " (" +
                                          complaint.status +
                                          ")"
                                        : ""
                                );


                            complaintSelect.appendChild(
                                option
                            );

                        }
                    );


                    complaintSelect.disabled =
                        false;

                })

                .catch(function (error) {

                    console.error(
                        "Complaint loading error:",
                        error
                    );


                    complaintSelect.innerHTML =
                        '<option value="">' +
                        'Unable to load complaints' +
                        '</option>';


                    complaintSelect.disabled =
                        true;

                });

        }


        /* =================================================
           CLOSE RESIDENT RESULTS
        ================================================= */

        document.addEventListener(
            "click",
            function (event) {

                if (
                    !residentSearchInput.contains(
                        event.target
                    ) &&
                    !residentSearchResults.contains(
                        event.target
                    )
                ) {

                    residentSearchResults.classList.add(
                        "hidden"
                    );

                }

            }
        );

    }


    /* =====================================================
       UPLOAD FORM VALIDATION
    ====================================================== */

    if (evidenceUploadForm) {

        evidenceUploadForm.addEventListener(
            "submit",
            function (event) {

                if (
                    residentIdInput &&
                    !residentIdInput.value
                ) {

                    event.preventDefault();

                    alert(
                        "Please select a resident from the search results."
                    );

                    residentSearchInput.focus();

                    return;
                }


                if (
                    complaintSelect &&
                    !complaintSelect.value
                ) {

                    event.preventDefault();

                    alert(
                        "Please select a complaint."
                    );

                    complaintSelect.focus();

                    return;
                }


                if (
                    fileInput &&
                    !fileInput.files.length
                ) {

                    event.preventDefault();

                    alert(
                        "Please select an evidence file."
                    );

                    return;
                }

            }
        );

    }


    /* =====================================================
       HELPERS
    ====================================================== */

    function getResidentFullName(
        resident
    ) {

        return [
            resident.firstName,
            resident.middleName,
            resident.lastName,
            resident.suffix
        ]
            .filter(Boolean)
            .join(" ");

    }


    function capitalize(value) {

        if (!value) {
            return "—";
        }


        return (
            value.charAt(0).toUpperCase() +
            value.slice(1)
        );

    }


    function parseDate(value) {

        const date =
            new Date(value || 0);


        if (
            Number.isNaN(
                date.getTime()
            )
        ) {
            return 0;
        }


        return date.getTime();

    }


    function formatStoredSize(value) {

        const numeric =
            Number(value);


        if (
            !Number.isFinite(numeric) ||
            numeric <= 0
        ) {

            return value || "—";

        }


        /*
         * If Django stores raw bytes,
         * convert to readable size.
         */

        if (numeric >= 1024) {

            return formatFileSize(
                numeric
            );

        }


        return value;

    }


    function formatFileSize(bytes) {

        const numericBytes =
            Number(bytes);


        if (
            !Number.isFinite(
                numericBytes
            ) ||
            numericBytes <= 0
        ) {

            return "0 Bytes";

        }


        const units = [
            "Bytes",
            "KB",
            "MB",
            "GB"
        ];


        const index =
            Math.min(
                Math.floor(
                    Math.log(numericBytes) /
                    Math.log(1024)
                ),
                units.length - 1
            );


        const value =
            numericBytes /
            Math.pow(
                1024,
                index
            );


        return (
            value.toFixed(
                index === 0 ? 0 : 1
            ) +
            " " +
            units[index]
        );

    }


    /* =====================================================
       INITIALIZE
    ====================================================== */

    updateCategoryCounts();

    bindEvidenceCards();

    filterEvidence();


    if (sortSelect) {

        sortEvidence(
            sortSelect.value
        );

    }

});