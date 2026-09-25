/* =========================================================
   BANTAYBARANGAY
   MY COMPLAINTS
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const searchInput =
        document.getElementById("complaintSearch");

    const categoryFilter =
        document.getElementById("categoryFilter");

    const statusTabs =
        document.querySelectorAll(".status-tab");

    const complaintCards =
        document.querySelectorAll(".complaint-card");

    const filterEmpty =
        document.getElementById("filterEmpty");


    let currentStatus = "all";


    /* =====================================================
       NORMALIZE TEXT
    ====================================================== */

    function normalize(value) {

        return String(value || "")
            .trim()
            .toLowerCase();

    }


    /* =====================================================
       STATUS MATCHING
    ====================================================== */

    function statusMatches(status, filter) {

        status = normalize(status);


        if (filter === "all") {
            return true;
        }


        if (filter === "progress") {

            return (
                status.includes("progress") ||
                status.includes("investigation") ||
                status.includes("pending") ||
                status.includes("submitted") ||
                status.includes("review")
            );

        }


        if (filter === "mediation") {

            return (
                status.includes("mediation") ||
                status.includes("conciliation") ||
                status.includes("hearing") ||
                status.includes("lupon")
            );

        }


        if (filter === "resolved") {

            return (
                status.includes("resolved") ||
                status.includes("closed") ||
                status.includes("archived") ||
                status.includes("completed")
            );

        }


        return true;

    }


    /* =====================================================
       APPLY FILTERS
    ====================================================== */

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


        complaintCards.forEach(function (card) {

            const cardSearch =
                normalize(card.dataset.search);

            const cardStatus =
                normalize(card.dataset.status);

            const cardCategory =
                normalize(card.dataset.category);


            const matchesSearch =
                !searchValue ||
                cardSearch.includes(searchValue);


            const matchesCategory =
                selectedCategory === "all" ||
                cardCategory === selectedCategory;


            const matchesStatus =
                statusMatches(
                    cardStatus,
                    currentStatus
                );


            const shouldShow =
                matchesSearch &&
                matchesCategory &&
                matchesStatus;


            card.hidden = !shouldShow;


            if (shouldShow) {
                visibleCount++;
            }

        });


        /* ===============================================
           FILTER EMPTY STATE
        ================================================ */

        if (filterEmpty) {

            if (
                complaintCards.length > 0 &&
                visibleCount === 0
            ) {

                filterEmpty.hidden = false;

            } else {

                filterEmpty.hidden = true;

            }

        }

    }


    /* =====================================================
       SEARCH
    ====================================================== */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            applyFilters
        );

    }


    /* =====================================================
       CATEGORY FILTER
    ====================================================== */

    if (categoryFilter) {

        categoryFilter.addEventListener(
            "change",
            applyFilters
        );

    }


    /* =====================================================
       STATUS TABS
    ====================================================== */

    statusTabs.forEach(function (tab) {

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


                tab.classList.add("active");


                currentStatus =
                    tab.dataset.filter || "all";


                applyFilters();

            }
        );

    });


    /* =====================================================
       INITIAL FILTER
    ====================================================== */

    applyFilters();

});