/* =========================================================
   BANTAYBARANGAY
   MY COMPLAINTS
========================================================= */

(function () {

    "use strict";


    /* =====================================================
       PAGE INITIALIZATION
    ====================================================== */

    document.addEventListener(
        "DOMContentLoaded",
        function () {

            initializeComplaintPage();

        }
    );


    /* =====================================================
       INITIALIZE
    ====================================================== */

    function initializeComplaintPage() {

        initializeFilters();

        initializeTimeline();

        removeAccidentalLoader();

    }


    /* =====================================================
       REMOVE ACCIDENTAL FULL-SCREEN LOADER
    ====================================================== */

    function removeAccidentalLoader() {

        const selectors = [

            "#pageLoader",
            "#page-loader",

            "#loadingScreen",
            "#loading-screen",

            "#loadingOverlay",
            "#loading-overlay",

            "#preloader",

            "#globalLoader",
            "#global-loader",

            ".page-loader",
            ".loading-screen",
            ".loading-overlay",
            ".preloader",
            ".global-loader"

        ];


        selectors.forEach(
            function (selector) {

                document
                    .querySelectorAll(selector)
                    .forEach(
                        function (element) {

                            if (
                                element.closest(
                                    "#timelineModal"
                                )
                            ) {

                                return;

                            }


                            element.style.setProperty(
                                "display",
                                "none",
                                "important"
                            );


                            element.style.setProperty(
                                "visibility",
                                "hidden",
                                "important"
                            );


                            element.style.setProperty(
                                "opacity",
                                "0",
                                "important"
                            );


                            element.style.setProperty(
                                "pointer-events",
                                "none",
                                "important"
                            );

                        }
                    );

            }
        );

    }


    /* =====================================================
       FILTERS
    ====================================================== */

    function initializeFilters() {

        const searchInput =
            document.getElementById(
                "complaintSearch"
            );


        const categoryFilter =
            document.getElementById(
                "categoryFilter"
            );


        const statusTabs =
            document.querySelectorAll(
                ".status-tab"
            );


        const complaintCards =
            document.querySelectorAll(
                ".complaint-card"
            );


        const filterEmpty =
            document.getElementById(
                "filterEmpty"
            );


        const searchSpinner =
            document.getElementById(
                "searchSpinner"
            );


        let currentStatus = "all";

        let searchTimer = null;


        /* =================================================
           NORMALIZE
        ================================================== */

        function normalize(value) {

            return String(
                value || ""
            )
                .trim()
                .toLowerCase();

        }


        /* =================================================
           STATUS MATCH
        ================================================== */

        function statusMatches(
            status,
            filter
        ) {

            status =
                normalize(status);


            if (
                filter === "all"
            ) {

                return true;

            }


            if (
                filter === "progress"
            ) {

                return (
                    status.includes(
                        "progress"
                    ) ||
                    status.includes(
                        "investigation"
                    ) ||
                    status.includes(
                        "pending"
                    ) ||
                    status.includes(
                        "submitted"
                    ) ||
                    status.includes(
                        "review"
                    ) ||
                    status.includes(
                        "verification"
                    ) ||
                    status.includes(
                        "referred"
                    )
                );

            }


            if (
                filter === "mediation"
            ) {

                return (
                    status.includes(
                        "mediation"
                    ) ||
                    status.includes(
                        "conciliation"
                    ) ||
                    status.includes(
                        "hearing"
                    ) ||
                    status.includes(
                        "lupon"
                    )
                );

            }


            if (
                filter === "resolved"
            ) {

                return (
                    status.includes(
                        "resolved"
                    ) ||
                    status.includes(
                        "closed"
                    ) ||
                    status.includes(
                        "completed"
                    ) ||
                    status.includes(
                        "settled"
                    )
                );

            }


            return true;

        }


        /* =================================================
           APPLY FILTERS
        ================================================== */

        function applyFilters() {

            const searchValue =
                normalize(
                    searchInput
                        ? searchInput.value
                        : ""
                );


            const selectedCategory =
                normalize(
                    categoryFilter
                        ? categoryFilter.value
                        : "all"
                );


            let visibleCount = 0;


            complaintCards.forEach(
                function (card) {

                    const cardSearch =
                        normalize(
                            card.dataset.search
                        );


                    const cardStatus =
                        normalize(
                            card.dataset.status
                        );


                    const cardCategory =
                        normalize(
                            card.dataset.category
                        );


                    const matchesSearch =
                        !searchValue ||
                        cardSearch.includes(
                            searchValue
                        );


                    const matchesCategory =
                        selectedCategory === "all" ||
                        cardCategory ===
                            selectedCategory;


                    const matchesStatus =
                        statusMatches(
                            cardStatus,
                            currentStatus
                        );


                    const shouldShow =
                        matchesSearch &&
                        matchesCategory &&
                        matchesStatus;


                    card.hidden =
                        !shouldShow;


                    if (
                        shouldShow
                    ) {

                        visibleCount++;

                    }

                }
            );


            if (
                filterEmpty
            ) {

                filterEmpty.hidden =
                    !(
                        complaintCards.length > 0 &&
                        visibleCount === 0
                    );

            }

        }


        /* =================================================
           SEARCH
        ================================================== */

        if (
            searchInput
        ) {

            searchInput.addEventListener(
                "input",
                function () {

                    if (
                        searchSpinner
                    ) {

                        searchSpinner.classList.add(
                            "is-visible"
                        );

                    }


                    clearTimeout(
                        searchTimer
                    );


                    searchTimer =
                        setTimeout(
                            function () {

                                applyFilters();


                                if (
                                    searchSpinner
                                ) {

                                    searchSpinner.classList.remove(
                                        "is-visible"
                                    );

                                }

                            },
                            180
                        );

                }
            );

        }


        /* =================================================
           CATEGORY
        ================================================== */

        if (
            categoryFilter
        ) {

            categoryFilter.addEventListener(
                "change",
                function () {

                    applyFilters();

                }
            );

        }


        /* =================================================
           STATUS TABS
        ================================================== */

        statusTabs.forEach(
            function (tab) {

                tab.addEventListener(
                    "click",
                    function () {

                        statusTabs.forEach(
                            function (button) {

                                button.classList.remove(
                                    "active"
                                );

                            }
                        );


                        tab.classList.add(
                            "active"
                        );


                        currentStatus =
                            tab.dataset.filter ||
                            "all";


                        applyFilters();

                    }
                );

            }
        );


        /* =================================================
           INITIAL FILTER
        ================================================== */

        applyFilters();

    }


    /* =====================================================
       TIMELINE
    ====================================================== */

    function initializeTimeline() {

        const modal =
            document.getElementById(
                "timelineModal"
            );


        const overlay =
            document.getElementById(
                "timelineOverlay"
            );


        const closeButton =
            document.getElementById(
                "timelineClose"
            );


        const doneButton =
            document.getElementById(
                "timelineDone"
            );


        const timelineButtons =
            document.querySelectorAll(
                ".view-timeline-button"
            );


        if (
            !modal ||
            !timelineButtons.length
        ) {

            return;

        }


        /* =================================================
           ELEMENTS
        ================================================== */

        const title =
            document.getElementById(
                "timelineTitle"
            );


        const reference =
            document.getElementById(
                "timelineReference"
            );


        const referenceInfo =
            document.getElementById(
                "timelineReferenceInfo"
            );


        const category =
            document.getElementById(
                "timelineCategory"
            );


        const subject =
            document.getElementById(
                "timelineSubject"
            );


        const start =
            document.getElementById(
                "timelineStart"
            );


        const startPoint =
            document.getElementById(
                "timelineStartPoint"
            );


        const status =
            document.getElementById(
                "timelineStatus"
            );


        const statusPoint =
            document.getElementById(
                "timelineStatusPoint"
            );


        const footerStatus =
            document.getElementById(
                "timelineFooterStatus"
            );


        const elapsed =
            document.getElementById(
                "timelineElapsed"
            );


        const description =
            document.getElementById(
                "timelineDescription"
            );


        const progress =
            document.getElementById(
                "timelineProgress"
            );


        /* =================================================
           FORMAT DATE
        ================================================== */

        function formatDate(
            value
        ) {

            if (
                !value
            ) {

                return "Not available";

            }


            const date =
                new Date(
                    value +
                    "T00:00:00"
                );


            if (
                Number.isNaN(
                    date.getTime()
                )
            ) {

                return "Not available";

            }


            return date.toLocaleDateString(
                "en-US",
                {
                    month: "short",
                    day: "numeric",
                    year: "numeric"
                }
            );

        }


        /* =================================================
           DAYS ELAPSED
        ================================================== */

        function getElapsedDays(
            value
        ) {

            if (
                !value
            ) {

                return 0;

            }


            const startDate =
                new Date(
                    value +
                    "T00:00:00"
                );


            const today =
                new Date();


            if (
                Number.isNaN(
                    startDate.getTime()
                )
            ) {

                return 0;

            }


            startDate.setHours(
                0,
                0,
                0,
                0
            );


            today.setHours(
                0,
                0,
                0,
                0
            );


            const difference =
                today.getTime() -
                startDate.getTime();


            return Math.max(
                0,
                Math.floor(
                    difference /
                    86400000
                )
            );

        }


        /* =================================================
           STATUS DESCRIPTION
        ================================================== */

        function getStatusDescription(
            value
        ) {

            const current =
                String(
                    value || ""
                )
                    .trim()
                    .toLowerCase();


            if (
                current.includes(
                    "resolved"
                )
            ) {

                return (
                    "The complaint has been resolved."
                );

            }


            if (
                current.includes(
                    "closed"
                )
            ) {

                return (
                    "The complaint has been closed."
                );

            }


            if (
                current.includes(
                    "settled"
                )
            ) {

                return (
                    "The complaint has been settled."
                );

            }


            if (
                current.includes(
                    "hearing"
                )
            ) {

                return (
                    "The complaint is currently scheduled for or undergoing a hearing."
                );

            }


            if (
                current.includes(
                    "mediation"
                )
            ) {

                return (
                    "The complaint is currently under mediation."
                );

            }


            if (
                current.includes(
                    "conciliation"
                )
            ) {

                return (
                    "The complaint is currently under conciliation."
                );

            }


            if (
                current.includes(
                    "investigation"
                )
            ) {

                return (
                    "The complaint is currently under investigation."
                );

            }


            if (
                current.includes(
                    "verification"
                )
            ) {

                return (
                    "The complaint is currently undergoing verification."
                );

            }


            if (
                current.includes(
                    "review"
                )
            ) {

                return (
                    "The complaint is currently under review."
                );

            }


            if (
                current.includes(
                    "referred"
                )
            ) {

                return (
                    "The complaint has been referred for further action."
                );

            }


            if (
                current.includes(
                    "submitted"
                )
            ) {

                return (
                    "The complaint has been submitted and is awaiting further processing."
                );

            }


            return (
                "The complaint is currently being processed by the barangay."
            );

        }


        /* =================================================
           OPEN TIMELINE
        ================================================== */

        function openTimeline(
            button
        ) {

            const complaintReference =
                button.dataset.reference ||
                "--";


            const complaintSubject =
                button.dataset.subject ||
                "Complaint";


            const complaintCategory =
                button.dataset.category ||
                "General Complaint";


            const complaintStatus =
                button.dataset.status ||
                "Submitted";


            const complaintStartDate =
                button.dataset.startDate ||
                "";


            const formattedStartDate =
                formatDate(
                    complaintStartDate
                );


            const elapsedDays =
                getElapsedDays(
                    complaintStartDate
                );


            /* ---------------------------------------------
               HEADER
            --------------------------------------------- */

            if (
                title
            ) {

                title.textContent =
                    complaintSubject;

            }


            if (
                reference
            ) {

                reference.textContent =
                    "Reference #" +
                    complaintReference;

            }


            /* ---------------------------------------------
               INFORMATION
            --------------------------------------------- */

            if (
                referenceInfo
            ) {

                referenceInfo.textContent =
                    "#" +
                    complaintReference;

            }


            if (
                category
            ) {

                category.textContent =
                    complaintCategory;

            }


            if (
                subject
            ) {

                subject.textContent =
                    complaintSubject;

            }


            /* ---------------------------------------------
               SUMMARY
            --------------------------------------------- */

            if (
                start
            ) {

                start.textContent =
                    formattedStartDate;

            }


            if (
                status
            ) {

                status.textContent =
                    complaintStatus;

            }


            if (
                elapsed
            ) {

                elapsed.textContent =
                    formatElapsedDays(
                        elapsedDays
                    );

            }


            /* ---------------------------------------------
               CHART POINTS
            --------------------------------------------- */

            if (
                startPoint
            ) {

                startPoint.textContent =
                    formattedStartDate;

            }


            if (
                statusPoint
            ) {

                statusPoint.textContent =
                    complaintStatus;

            }


            if (
                footerStatus
            ) {

                footerStatus.textContent =
                    complaintStatus;

            }


            if (
                description
            ) {

                description.textContent =
                    getStatusDescription(
                        complaintStatus
                    );

            }


            /* ---------------------------------------------
               PROGRESS LINE
            --------------------------------------------- */

            if (
                progress
            ) {

                /*
                 * We only know two actual points:
                 *
                 * 1. complaint started
                 * 2. current status today
                 *
                 * Therefore the visual line represents
                 * the passage from filing to today.
                 */

                progress.style.transform =
                    "scaleX(0)";


                requestAnimationFrame(
                    function () {

                        requestAnimationFrame(
                            function () {

                                progress.style.transform =
                                    "scaleX(1)";

                            }
                        );

                    }
                );

            }


            /* ---------------------------------------------
               OPEN
            --------------------------------------------- */

            modal.classList.add(
                "is-open"
            );


            modal.setAttribute(
                "aria-hidden",
                "false"
            );


            document.body.classList.add(
                "timeline-open"
            );

        }


        /* =================================================
           FORMAT ELAPSED
        ================================================== */

        function formatElapsedDays(
            days
        ) {

            if (
                days === 0
            ) {

                return "Today";

            }


            if (
                days === 1
            ) {

                return "1 day";

            }


            return (
                days +
                " days"
            );

        }


        /* =================================================
           CLOSE TIMELINE
        ================================================== */

        function closeTimeline() {

            modal.classList.remove(
                "is-open"
            );


            modal.setAttribute(
                "aria-hidden",
                "true"
            );


            document.body.classList.remove(
                "timeline-open"
            );


            if (
                progress
            ) {

                progress.style.transform =
                    "scaleX(0)";

            }

        }


        /* =================================================
           BUTTONS
        ================================================== */

        timelineButtons.forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        openTimeline(
                            button
                        );

                    }
                );

            }
        );


        /* =================================================
           CLOSE BUTTON
        ================================================== */

        if (
            closeButton
        ) {

            closeButton.addEventListener(
                "click",
                closeTimeline
            );

        }


        /* =================================================
           DONE BUTTON
        ================================================== */

        if (
            doneButton
        ) {

            doneButton.addEventListener(
                "click",
                closeTimeline
            );

        }


        /* =================================================
           OVERLAY
        ================================================== */

        if (
            overlay
        ) {

            overlay.addEventListener(
                "click",
                closeTimeline
            );

        }


        /* =================================================
           ESCAPE
        ================================================== */

        document.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.key === "Escape" &&
                    modal.classList.contains(
                        "is-open"
                    )
                ) {

                    closeTimeline();

                }

            }
        );

    }


})();