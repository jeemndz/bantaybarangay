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

    const evidenceCards =
        Array.from(document.querySelectorAll(".evidence-card"));

    const categoryCards =
        document.querySelectorAll(".category-card");

    const seeAllButton =
        document.querySelector(".see-all-button");

    const searchInput =
        document.getElementById("evidenceSearch");

    const sortSelect =
        document.getElementById("sortEvidence");

    const gridViewButton =
        document.getElementById("gridViewButton");

    const listViewButton =
        document.getElementById("listViewButton");

    const detailsPanel =
        document.getElementById("detailsPanel");

    const closeDetailsButton =
        document.getElementById("closeDetails");

    const uploadButton =
        document.getElementById("uploadEvidenceButton");

    const fileInput =
        document.getElementById("fileInput");

    const browseButton =
        document.getElementById("browseFiles");

    const dropZone =
        document.getElementById("dropZone");

    const emptyState =
        document.getElementById("emptyState");


    /* =====================================================
       CURRENT FILTER
    ====================================================== */

    let currentCategory = "all";


    /* =====================================================
       FILE DATA
    ====================================================== */

    const evidenceData = {

        1: {
            name: "IMG_20240101_INCIDENT.jpg",
            modified: "Modified Jan 12, 2024 • 14:22 PM",
            type: "JPEG Image",
            resolution: "4032 × 3024",
            uploader: "Officer K. San Jose",
            image: null,
            hash:
                "f3a1e948c03d7b6fa829b05c41d7e82f3a1e948c03d7b6f8a29b05c41d7e82"
        },

        2: {
            name: "CCTV_ENTRY_WAY_B4.mp4",
            modified: "Modified Jan 11, 2024 • 09:40 AM",
            type: "MP4 Video",
            resolution: "1920 × 1080",
            uploader: "Officer M. Reyes",
            image: null,
            hash:
                "71c20e731ef427a99b8114cbbe58176db76fc97b45ae69121051e295e7d19e21"
        },

        3: {
            name: "WITNESS_STATEMENT_REF_002.pdf",
            modified: "Modified Jan 10, 2024 • 11:18 AM",
            type: "PDF Document",
            resolution: "Document",
            uploader: "Officer K. San Jose",
            image: null,
            hash:
                "8a42c876cd78346f12be92c0ac22418e5399d88f23ab6c4f128ff039110721aa"
        }

    };


    /* =====================================================
       CATEGORY FILTER
    ====================================================== */

    categoryCards.forEach(function (category) {

        category.addEventListener("click", function () {

            categoryCards.forEach(function (card) {
                card.classList.remove("active");
            });

            this.classList.add("active");

            currentCategory =
                this.dataset.category || "all";

            filterEvidence();

        });

    });


    /* =====================================================
       SEE ALL
    ====================================================== */

    if (seeAllButton) {

        seeAllButton.addEventListener("click", function () {

            currentCategory = "all";

            categoryCards.forEach(function (card) {
                card.classList.remove("active");
            });

            filterEvidence();

        });

    }


    /* =====================================================
       SEARCH
    ====================================================== */

    if (searchInput) {

        searchInput.addEventListener("input", function () {
            filterEvidence();
        });

    }


    /* =====================================================
       FILTER EVIDENCE
    ====================================================== */

 function filterEvidence() {

    const query =
        searchInput
            ? searchInput.value.trim().toLowerCase()
            : "";

    let visibleCount = 0;

    evidenceGrid.querySelectorAll(".evidence-card")
        .forEach(function (card) {

            const fileName =
                (card.dataset.name || "").toLowerCase();

            const type =
                card.dataset.type || "";

            const categoryMatches =
                currentCategory === "all" ||
                type === currentCategory;

            const searchMatches =
                fileName.includes(query);

            if (categoryMatches && searchMatches) {

                card.style.display = "";
                visibleCount++;

            } else {

                card.style.display = "none";

            }

        });

    if (emptyState) {
        emptyState.hidden = visibleCount !== 0;
    }

}

    /* =====================================================
       GRID VIEW
    ====================================================== */

    if (gridViewButton) {

        gridViewButton.addEventListener("click", function () {

            evidenceGrid.classList.remove("list-view");

            gridViewButton.classList.add("active");
            listViewButton.classList.remove("active");

        });

    }


    /* =====================================================
       LIST VIEW
    ====================================================== */

    if (listViewButton) {

        listViewButton.addEventListener("click", function () {

            evidenceGrid.classList.add("list-view");

            listViewButton.classList.add("active");
            gridViewButton.classList.remove("active");

        });

    }


    /* =====================================================
       SELECT EVIDENCE
    ====================================================== */

    evidenceCards.forEach(function (card) {

        card.addEventListener("click", function () {

            evidenceCards.forEach(function (item) {
                item.classList.remove("selected");
            });

            this.classList.add("selected");

            const id = this.dataset.id;

            updateDetails(id);

            detailsPanel.classList.remove("closed");

        });

    });


    /* =====================================================
       UPDATE DETAILS PANEL
    ====================================================== */

    function updateDetails(id) {

        const data = evidenceData[id];

        if (!data) {
            return;
        }


        const detailName =
            document.getElementById("detailName");

        const detailModified =
            document.getElementById("detailModified");

        const detailType =
            document.getElementById("detailType");

        const detailResolution =
            document.getElementById("detailResolution");

        const detailUploader =
            document.getElementById("detailUploader");

        const detailHash =
            document.getElementById("detailHash");


        if (detailName) {
            detailName.textContent = data.name;
        }

        if (detailModified) {
            detailModified.textContent = data.modified;
        }

        if (detailType) {
            detailType.textContent = data.type;
        }

        if (detailResolution) {
            detailResolution.textContent = data.resolution;
        }

        if (detailUploader) {
            detailUploader.textContent = data.uploader;
        }

        if (detailHash) {
            detailHash.textContent = data.hash;
        }

    }


    /* =====================================================
       CLOSE DETAILS PANEL
    ====================================================== */

    if (closeDetailsButton) {

        closeDetailsButton.addEventListener("click", function () {

            detailsPanel.classList.add("closed");

            evidenceCards.forEach(function (card) {
                card.classList.remove("selected");
            });

        });

    }


    /* =====================================================
       OPEN FILE PICKER
    ====================================================== */

    if (uploadButton) {

        uploadButton.addEventListener("click", function () {
            fileInput.click();
        });

    }


    if (browseButton) {

        browseButton.addEventListener("click", function (event) {

            event.stopPropagation();

            fileInput.click();

        });

    }


    if (dropZone) {

        dropZone.addEventListener("click", function (event) {

            if (event.target !== browseButton) {
                fileInput.click();
            }

        });

    }


    /* =====================================================
       FILE INPUT
    ====================================================== */

    if (fileInput) {

        fileInput.addEventListener("change", function () {

            if (!this.files.length) {
                return;
            }

            handleFiles(this.files);

            this.value = "";

        });

    }


  /* =====================================================
   DRAG AND DROP
====================================================== */

if (dropZone) {

    dropZone.addEventListener("dragenter", function (event) {

        event.preventDefault();

        dropZone.classList.add("drag-active");

    });


    dropZone.addEventListener("dragover", function (event) {

        event.preventDefault();

        dropZone.classList.add("drag-active");

    });


    dropZone.addEventListener("dragleave", function (event) {

        event.preventDefault();

        dropZone.classList.remove("drag-active");

    });


    dropZone.addEventListener("drop", function (event) {

        event.preventDefault();

        dropZone.classList.remove("drag-active");

        const files = event.dataTransfer.files;

        if (files.length) {
            handleFiles(files);
        }

    });

}


    /* =====================================================
       DRAG LEAVE
    ====================================================== */

    dropZone.addEventListener("dragleave", function (event) {

        event.preventDefault();

        dropZone.classList.remove("drag-active");

    });


    /* =====================================================
       DROP FILE
    ====================================================== */

    dropZone.addEventListener("drop", function (event) {

        event.preventDefault();

        dropZone.classList.remove("drag-active");

        const files = event.dataTransfer.files;

        if (files.length) {
            handleFiles(files);
        }

    });


    /* =====================================================
       PROCESS UPLOAD
    ====================================================== */

    function handleFiles(files) {

        const maxSize =
            500 * 1024 * 1024;

        Array.from(files).forEach(function (file) {

            if (file.size > maxSize) {

                alert(
                    file.name +
                    " exceeds the maximum 500MB file size."
                );

                return;

            }

            createEvidenceCard(file);

        });

    }


    /* =====================================================
       CREATE NEW EVIDENCE CARD
    ====================================================== */

    function createEvidenceCard(file) {

        const id =
            "upload_" + Date.now() + "_" +
            Math.floor(Math.random() * 10000);

        const category =
            determineFileCategory(file);

        const size =
            formatFileSize(file.size);

        const today =
            new Date();

        const card =
            document.createElement("article");


        card.className = "evidence-card";

        card.dataset.id = id;
        card.dataset.type = category;
        card.dataset.name = file.name;
        card.dataset.date = today
            .toISOString()
            .split("T")[0];

        card.dataset.size =
            file.size / (1024 * 1024);


        /* =============================================
           PREVIEW
        ============================================== */

        const preview =
            document.createElement("div");

        preview.className =
            "evidence-preview";


        if (
            category === "photos" &&
            file.type.startsWith("image/")
        ) {

            preview.classList.add("image-preview");

            const image =
                document.createElement("img");

            image.src =
                URL.createObjectURL(file);

            image.alt = file.name;

            preview.appendChild(image);

        } else {

            const icon =
                document.createElement("i");

            icon.className =
                getFileIcon(category) +
                " preview-icon";

            preview.appendChild(icon);

        }


        const badge =
            document.createElement("span");

        badge.className =
            "verification-badge pending";

        badge.innerHTML =
            '<i class="fa-solid fa-circle"></i> Pending Ledger';

        preview.appendChild(badge);


        /* =============================================
           INFO
        ============================================== */

        const info =
            document.createElement("div");

        info.className =
            "evidence-info";


        const name =
            document.createElement("strong");

        name.className =
            "evidence-name";

        name.textContent =
            file.name;


        const meta =
            document.createElement("div");

        meta.className =
            "evidence-meta";


        const sizeElement =
            document.createElement("span");

        sizeElement.textContent =
            size;


        const dateElement =
            document.createElement("span");

        dateElement.textContent =
            today.toLocaleDateString(
                "en-US",
                {
                    month: "short",
                    day: "numeric",
                    year: "numeric"
                }
            );


        meta.appendChild(sizeElement);
        meta.appendChild(dateElement);

        info.appendChild(name);
        info.appendChild(meta);

        card.appendChild(preview);
        card.appendChild(info);


        /* =============================================
           DETAILS DATA
        ============================================== */

        evidenceData[id] = {

            name: file.name,

            modified:
                "Uploaded " +
                today.toLocaleString(),

            type:
                file.type || "Unknown File",

            resolution:
                category === "photos"
                    ? "Processing..."
                    : "N/A",

            uploader:
                "Admin Jane",

            hash:
                "Pending blockchain verification..."

        };


        /* =============================================
           CARD CLICK
        ============================================== */

        card.addEventListener(
            "click",
            function () {

                document
                    .querySelectorAll(".evidence-card")
                    .forEach(function (item) {

                        item.classList.remove("selected");

                    });

                card.classList.add("selected");

                updateDetails(id);

                detailsPanel.classList.remove("closed");

            }
        );


        evidenceGrid.prepend(card);

        emptyState.hidden = true;

    }


    /* =====================================================
       DETERMINE FILE CATEGORY
    ====================================================== */

    function determineFileCategory(file) {

        const type =
            file.type.toLowerCase();

        if (type.startsWith("image/")) {
            return "photos";
        }

        if (type.startsWith("video/")) {
            return "videos";
        }

        if (type.startsWith("audio/")) {
            return "audio";
        }

        return "documents";

    }


    /* =====================================================
       FILE ICON
    ====================================================== */

    function getFileIcon(category) {

        switch (category) {

            case "videos":
                return "fa-solid fa-clapperboard";

            case "audio":
                return "fa-solid fa-file-audio";

            case "documents":
                return "fa-regular fa-file-lines";

            default:
                return "fa-regular fa-file";

        }

    }


    /* =====================================================
       FORMAT FILE SIZE
    ====================================================== */

    function formatFileSize(bytes) {

        if (bytes === 0) {
            return "0 Bytes";
        }

        const units = [
            "Bytes",
            "KB",
            "MB",
            "GB"
        ];

        const index =
            Math.floor(
                Math.log(bytes) /
                Math.log(1024)
            );

        const value =
            bytes /
            Math.pow(1024, index);

        return (
            value.toFixed(
                index === 0 ? 0 : 1
            ) +
            " " +
            units[index]
        );

    }


    /* =====================================================
       SORT EVIDENCE
    ====================================================== */

    if (sortSelect) {

        sortSelect.addEventListener(
            "change",
            function () {

                sortEvidence(this.value);

            }
        );

    }


    function sortEvidence(sortType) {

        const cards =
            Array.from(
                evidenceGrid.querySelectorAll(
                    ".evidence-card"
                )
            );


        cards.sort(function (a, b) {

            /* NEWEST */

            if (sortType === "newest") {

                return (
                    new Date(b.dataset.date) -
                    new Date(a.dataset.date)
                );

            }


            /* OLDEST */

            if (sortType === "oldest") {

                return (
                    new Date(a.dataset.date) -
                    new Date(b.dataset.date)
                );

            }


            /* NAME */

            if (sortType === "name") {

                return (
                    a.dataset.name || ""
                ).localeCompare(
                    b.dataset.name || ""
                );

            }


            /* SIZE */

            if (sortType === "size") {

                return (
                    parseFloat(b.dataset.size || 0) -
                    parseFloat(a.dataset.size || 0)
                );

            }


            return 0;

        });


        cards.forEach(function (card) {
            evidenceGrid.appendChild(card);
        });

    }
       /* =====================================================
       RESIDENT SEARCH
    ====================================================== */

    const residentSearchInput =
        document.getElementById("residentSearchInput");

    const residentIdInput =
        document.getElementById("residentIdInput");

    const residentSearchResults =
        document.getElementById("residentSearchResults");

    const complaintSelect =
        document.getElementById("complaintSelect");

    const evidenceUploadForm =
        document.getElementById("evidenceUploadForm");

    const residents = [];

document.querySelectorAll(".resident-data").forEach(
    function (element) {

        residents.push({
            id: element.dataset.id,
            firstName: element.dataset.firstName || "",
            middleName: element.dataset.middleName || "",
            lastName: element.dataset.lastName || "",
            suffix: element.dataset.suffix || ""
        });

    }
);


    /* =====================================================
       RESIDENT SEARCH
    ===================================================== */

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

                residentIdInput.value = "";

                complaintSelect.innerHTML =
                    '<option value="">Select Complaint</option>';

                complaintSelect.disabled = true;


                if (!search) {

                    residentSearchResults.innerHTML = "";

                    residentSearchResults.classList.add(
                        "hidden"
                    );

                    return;
                }


                /* =========================================
                   FILTER RESIDENTS
                ========================================== */

                const filteredResidents =
                    residents.filter(function (resident) {

                        const fullName =
                            [
                                resident.firstName,
                                resident.middleName,
                                resident.lastName,
                                resident.suffix
                            ]
                            .filter(Boolean)
                            .join(" ")
                            .toLowerCase();

                        return fullName.includes(search);

                    });


                /* =========================================
                   NO RESULTS
                ========================================== */

                if (filteredResidents.length === 0) {

                    residentSearchResults.innerHTML =
                        '<div class="px-3 py-2 text-sm text-slate-500">' +
                        'No residents found' +
                        '</div>';

                    residentSearchResults.classList.remove(
                        "hidden"
                    );

                    return;
                }


                /* =========================================
                   DISPLAY RESULTS
                ========================================== */

                residentSearchResults.innerHTML = "";


                filteredResidents.forEach(
                    function (resident) {

                        const fullName =
                            [
                                resident.firstName,
                                resident.middleName,
                                resident.lastName,
                                resident.suffix
                            ]
                            .filter(Boolean)
                            .join(" ");


                        const result =
                            document.createElement("button");

                        result.type = "button";

                        result.className =
                            "block w-full px-3 py-2 text-left text-sm hover:bg-slate-100";


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


                        residentSearchResults.appendChild(
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

            residentSearchResults.innerHTML = "";

            residentSearchResults.classList.add(
                "hidden"
            );


            loadResidentComplaints(
                resident.id
            );

        }


        /* =================================================
           LOAD RESIDENT COMPLAINTS
        ================================================= */

        function loadResidentComplaints(
            residentId
        ) {

            complaintSelect.innerHTML =
                '<option value="">Loading complaints...</option>';

            complaintSelect.disabled = true;


            const url =
                "/evidence/resident/" +
                residentId +
                "/complaints/";


            fetch(url)
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
                        '<option value="">Select Complaint</option>';


                    if (
                        !data.complaints ||
                        data.complaints.length === 0
                    ) {

                        complaintSelect.innerHTML =
                            '<option value="">No complaints found</option>';

                        complaintSelect.disabled = true;

                        return;
                    }


                    data.complaints.forEach(
                        function (complaint) {

                            const option =
                                document.createElement("option");

                            option.value =
                                complaint.complaint_id;

                            option.textContent =
                                "#" +
                                complaint.complaint_id +
                                " - " +
                                complaint.subject +
                                " (" +
                                complaint.status +
                                ")";


                            complaintSelect.appendChild(
                                option
                            );

                        }
                    );


                    complaintSelect.disabled = false;

                })
                .catch(function (error) {

                    console.error(
                        "Complaint loading error:",
                        error
                    );

                    complaintSelect.innerHTML =
                        '<option value="">Unable to load complaints</option>';

                    complaintSelect.disabled = true;

                });

        }


        /* =================================================
           HIDE RESULTS WHEN CLICKING OUTSIDE
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


        /* =================================================
           FORM VALIDATION
        ================================================= */

        if (evidenceUploadForm) {

            evidenceUploadForm.addEventListener(
                "submit",
                function (event) {

                    if (!residentIdInput.value) {

                        event.preventDefault();

                        alert(
                            "Please select a resident."
                        );

                        residentSearchInput.focus();

                        return;
                    }


                    if (!complaintSelect.value) {

                        event.preventDefault();

                        alert(
                            "Please select a complaint."
                        );

                        complaintSelect.focus();

                        return;
                    }

                }
            );

        }

    }

});