document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // ELEMENTS
    // =====================================================

    const notificationToggle =
        document.getElementById("notification-toggle");

    const notificationMenu =
        document.getElementById("notification-menu");

    const profileToggle =
        document.getElementById("profile-toggle");

    const profileMenu =
        document.getElementById("profile-menu");

    const profileArrow =
        document.getElementById("profile-arrow");

    const markAllRead =
        document.getElementById("mark-all-read");

    const notificationBadge =
        document.getElementById("notification-badge");

    const notificationItems =
        document.querySelectorAll(".notification-item");

    const searchInput =
        document.getElementById("global-search");

    const searchResults =
        document.getElementById("global-search-results");

    const searchResultsContent =
        document.getElementById("search-results-content");

    const searchLoading =
        document.getElementById("search-loading");


    // =====================================================
    // SEARCH STATE
    // =====================================================

    let searchTimeout = null;


    // =====================================================
    // CLOSE ALL DROPDOWNS
    // =====================================================

    function closeDropdowns() {

        // Notification
        if (notificationMenu) {

            notificationMenu.classList.add("hidden");

        }

        if (notificationToggle) {

            notificationToggle.setAttribute(
                "aria-expanded",
                "false"
            );

        }


        // Profile
        if (profileMenu) {

            profileMenu.classList.add("hidden");

        }

        if (profileToggle) {

            profileToggle.setAttribute(
                "aria-expanded",
                "false"
            );

        }

        if (profileArrow) {

            profileArrow.classList.remove(
                "rotate-180"
            );

        }

    }


    // =====================================================
    // NOTIFICATION DROPDOWN
    // =====================================================

    if (
        notificationToggle &&
        notificationMenu
    ) {

        notificationToggle.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();


                const isOpen =
                    !notificationMenu.classList.contains(
                        "hidden"
                    );


                // Close everything first
                closeDropdowns();


                // Open notification menu
                if (!isOpen) {

                    notificationMenu.classList.remove(
                        "hidden"
                    );

                    notificationToggle.setAttribute(
                        "aria-expanded",
                        "true"
                    );

                }

            }
        );

    }


    // =====================================================
    // PROFILE DROPDOWN
    // =====================================================

    if (
        profileToggle &&
        profileMenu
    ) {

        profileToggle.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();


                const isOpen =
                    !profileMenu.classList.contains(
                        "hidden"
                    );


                // Close everything first
                closeDropdowns();


                // Open profile menu
                if (!isOpen) {

                    profileMenu.classList.remove(
                        "hidden"
                    );

                    profileToggle.setAttribute(
                        "aria-expanded",
                        "true"
                    );


                    if (profileArrow) {

                        profileArrow.classList.add(
                            "rotate-180"
                        );

                    }

                }

            }
        );

    }


    // =====================================================
    // MARK ALL NOTIFICATIONS AS READ
    // =====================================================

    if (markAllRead) {

        markAllRead.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();


                notificationItems.forEach(
                    function (item) {

                        const unreadDot =
                            item.querySelector(
                                ".rounded-full"
                            );


                        if (unreadDot) {

                            unreadDot.classList.add(
                                "hidden"
                            );

                        }

                    }
                );


                // Remove notification badge
                if (notificationBadge) {

                    notificationBadge.textContent = "0";

                    notificationBadge.classList.add(
                        "hidden"
                    );

                }

            }
        );

    }


    // =====================================================
    // INDIVIDUAL NOTIFICATION CLICK
    // =====================================================

    notificationItems.forEach(
        function (item) {

            item.addEventListener(
                "click",
                function () {

                    const unreadDot =
                        this.querySelector(
                            ".rounded-full"
                        );


                    if (unreadDot) {

                        unreadDot.classList.add(
                            "hidden"
                        );

                    }


                    // Update notification count
                    if (notificationBadge) {

                        let count =
                            parseInt(
                                notificationBadge.textContent,
                                10
                            ) || 0;


                        if (count > 0) {

                            count--;

                            notificationBadge.textContent =
                                count;

                        }


                        if (count <= 0) {

                            notificationBadge.textContent =
                                "0";

                            notificationBadge.classList.add(
                                "hidden"
                            );

                        }

                    }

                }
            );

        }
    );


    // =====================================================
    // GLOBAL SEARCH DATA
    // =====================================================
    //
    // Temporary frontend search data.
    //
    // Later, this can be replaced with a Django
    // /search/ API endpoint so the search uses your
    // actual database.
    //
    // =====================================================

    const globalSearchData = [

        // -------------------------------------------------
        // RESIDENTS
        // -------------------------------------------------

        {
            type: "Resident",
            title: "Juan Dela Cruz",
            description: "Resident",
            url: "/residents/"
        },

        {
            type: "Resident",
            title: "Maria Santos",
            description: "Resident",
            url: "/residents/"
        },


        // -------------------------------------------------
        // COMPLAINTS
        // -------------------------------------------------

        {
            type: "Complaint",
            title: "Noise Complaint",
            description: "Complaint #CMP-001",
            url: "/complaints/"
        },

        {
            type: "Complaint",
            title: "Barangay Dispute",
            description: "Complaint #CMP-002",
            url: "/complaints/"
        },


        // -------------------------------------------------
        // DOCUMENTS
        // -------------------------------------------------

        {
            type: "Document",
            title: "Barangay Clearance",
            description: "Document",
            url: "/documents/"
        },

        {
            type: "Document",
            title: "Certificate of Residency",
            description: "Document",
            url: "/documents/"
        },


        // -------------------------------------------------
        // BLOCKCHAIN
        // -------------------------------------------------

        {
            type: "Blockchain",
            title: "Block #82910",
            description: "Blockchain Log",
            url: "/blockchain-logs/"
        }

    ];


    // =====================================================
    // SEARCH ICONS
    // =====================================================

    function getSearchIcon(type) {

        // -------------------------------------------------
        // RESIDENT
        // -------------------------------------------------

        if (type === "Resident") {

            return `
                <svg
                    class="h-5 w-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    stroke-width="1.8"
                >

                    <circle
                        cx="12"
                        cy="8"
                        r="4"
                    />

                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M4 21a8 8 0 0116 0"
                    />

                </svg>
            `;

        }


        // -------------------------------------------------
        // COMPLAINT
        // -------------------------------------------------

        if (type === "Complaint") {

            return `
                <svg
                    class="h-5 w-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    stroke-width="1.8"
                >

                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M12 9v4"
                    />

                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M12 17h.01"
                    />

                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M10.3 3.8 2.7 17a2 2 0 001.7 3h15.2a2 2 0 001.7-3L13.7 3.8a2 2 0 00-3.4 0Z"
                    />

                </svg>
            `;

        }


        // -------------------------------------------------
        // DOCUMENT
        // -------------------------------------------------

        if (type === "Document") {

            return `
                <svg
                    class="h-5 w-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    stroke-width="1.8"
                >

                    <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        d="M6 3h9l4 4v14H6V3Z"
                    />

                    <path
                        stroke-linecap="round"
                        d="M14 3v5h5"
                    />

                    <path
                        stroke-linecap="round"
                        d="M9 13h6"
                    />

                    <path
                        stroke-linecap="round"
                        d="M9 17h5"
                    />

                </svg>
            `;

        }


        // -------------------------------------------------
        // BLOCKCHAIN
        // -------------------------------------------------

        if (type === "Blockchain") {

            return `
                <svg
                    class="h-5 w-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    stroke-width="1.8"
                >

                    <rect
                        x="5"
                        y="5"
                        width="14"
                        height="14"
                        rx="2"
                    />

                    <path
                        stroke-linecap="round"
                        d="M9 9h6"
                    />

                    <path
                        stroke-linecap="round"
                        d="M9 12h6"
                    />

                    <path
                        stroke-linecap="round"
                        d="M9 15h4"
                    />

                </svg>
            `;

        }


        // -------------------------------------------------
        // DEFAULT
        // -------------------------------------------------

        return `
            <svg
                class="h-5 w-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                stroke-width="1.8"
            >

                <circle
                    cx="11"
                    cy="11"
                    r="7"
                />

                <path
                    stroke-linecap="round"
                    d="m20 20-4-4"
                />

            </svg>
        `;

    }


    // =====================================================
    // SHOW NO SEARCH RESULTS
    // =====================================================

    function showNoResults(query) {

        if (
            !searchResults ||
            !searchResultsContent
        ) {
            return;
        }


        searchResultsContent.innerHTML = `

            <div class="px-5 py-8 text-center">

                <div
                    class="mx-auto flex h-12 w-12
                           items-center justify-center
                           rounded-xl bg-slate-100
                           text-slate-400"
                >

                    <svg
                        class="h-6 w-6"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                        stroke-width="1.8"
                    >

                        <circle
                            cx="11"
                            cy="11"
                            r="7"
                        />

                        <path
                            stroke-linecap="round"
                            d="m20 20-4-4"
                        />

                    </svg>

                </div>


                <p
                    class="mt-3 text-sm font-semibold
                           text-slate-700"
                >
                    No results found
                </p>


                <p
                    class="mt-1 text-xs
                           text-slate-400"
                >
                    No results found for
                    "<span class="font-medium">
                        ${escapeHtml(query)}
                    </span>"
                </p>

            </div>

        `;


        searchResults.classList.remove(
            "hidden"
        );

    }


    // =====================================================
    // DISPLAY SEARCH RESULTS
    // =====================================================

    function displaySearchResults(
        results,
        query
    ) {

        if (
            !searchResults ||
            !searchResultsContent
        ) {
            return;
        }


        if (results.length === 0) {

            showNoResults(query);

            return;

        }


        searchResultsContent.innerHTML = `

            <!-- HEADER -->

            <div
                class="flex items-center
                       justify-between
                       border-b border-slate-100
                       px-5 py-3"
            >

                <p
                    class="text-xs font-semibold
                           uppercase tracking-wider
                           text-slate-400"
                >
                    Search Results
                </p>


                <span
                    class="text-xs text-slate-400"
                >
                    ${results.length}
                    result${results.length === 1 ? "" : "s"}
                </span>

            </div>


            <!-- RESULTS -->

            ${results.map(function (result) {

                return `

                    <a
                        href="${escapeHtml(result.url)}"
                        class="flex items-center gap-3
                               border-b border-slate-100
                               px-5 py-3.5
                               transition-colors
                               hover:bg-emerald-50"
                    >

                        <!-- ICON -->

                        <div
                            class="flex h-10 w-10
                                   shrink-0
                                   items-center
                                   justify-center
                                   rounded-xl
                                   bg-emerald-50
                                   text-emerald-600"
                        >

                            ${getSearchIcon(result.type)}

                        </div>


                        <!-- CONTENT -->

                        <div
                            class="min-w-0 flex-1"
                        >

                            <p
                                class="truncate
                                       text-sm
                                       font-semibold
                                       text-slate-700"
                            >
                                ${escapeHtml(result.title)}
                            </p>


                            <p
                                class="mt-0.5
                                       truncate
                                       text-xs
                                       text-slate-400"
                            >
                                ${escapeHtml(result.description)}
                            </p>

                        </div>


                        <!-- TYPE -->

                        <span
                            class="shrink-0
                                   rounded-full
                                   bg-slate-100
                                   px-2 py-1
                                   text-[10px]
                                   font-semibold
                                   text-slate-500"
                        >
                            ${escapeHtml(result.type)}
                        </span>

                    </a>

                `;

            }).join("")}

        `;


        searchResults.classList.remove(
            "hidden"
        );

    }


    // =====================================================
    // ESCAPE HTML
    // =====================================================

    function escapeHtml(value) {

        const div =
            document.createElement("div");

        div.textContent =
            String(value);

        return div.innerHTML;

    }


    // =====================================================
    // PERFORM GLOBAL SEARCH
    // =====================================================

    function performGlobalSearch(query) {

        const normalizedQuery =
            query.trim().toLowerCase();


        // Empty search
        if (!normalizedQuery) {

            if (searchResults) {

                searchResults.classList.add(
                    "hidden"
                );

            }


            if (searchLoading) {

                searchLoading.classList.add(
                    "hidden"
                );

            }

            return;

        }


        // Show loading
        if (searchLoading) {

            searchLoading.classList.remove(
                "hidden"
            );

        }


        // Cancel previous search
        clearTimeout(searchTimeout);


        searchTimeout =
            setTimeout(
                function () {

                    const results =
                        globalSearchData.filter(
                            function (item) {

                                const title =
                                    item.title
                                        .toLowerCase();

                                const description =
                                    item.description
                                        .toLowerCase();

                                const type =
                                    item.type
                                        .toLowerCase();


                                return (
                                    title.includes(
                                        normalizedQuery
                                    )
                                    ||
                                    description.includes(
                                        normalizedQuery
                                    )
                                    ||
                                    type.includes(
                                        normalizedQuery
                                    )
                                );

                            }
                        );


                    // Hide loading
                    if (searchLoading) {

                        searchLoading.classList.add(
                            "hidden"
                        );

                    }


                    displaySearchResults(
                        results,
                        query
                    );

                },
                250
            );

    }


    // =====================================================
    // SEARCH INPUT
    // =====================================================

    if (searchInput) {

        // Search while typing
        searchInput.addEventListener(
            "input",
            function () {

                performGlobalSearch(
                    this.value
                );

            }
        );


        // Search when focused
        searchInput.addEventListener(
            "focus",
            function () {

                const query =
                    this.value.trim();


                if (query) {

                    performGlobalSearch(
                        query
                    );

                }

            }
        );


        // Escape search
        searchInput.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Escape") {

                    this.value = "";


                    if (searchResults) {

                        searchResults.classList.add(
                            "hidden"
                        );

                    }


                    if (searchLoading) {

                        searchLoading.classList.add(
                            "hidden"
                        );

                    }


                    this.blur();

                }

            }
        );

    }


    // =====================================================
    // CLOSE SEARCH WHEN CLICKING OUTSIDE
    // =====================================================

    document.addEventListener(
        "click",
        function (event) {

            // Search
            if (
                searchInput &&
                searchResults &&
                !searchInput.contains(
                    event.target
                ) &&
                !searchResults.contains(
                    event.target
                )
            ) {

                searchResults.classList.add(
                    "hidden"
                );

            }


            // Notifications
            if (
                notificationToggle &&
                notificationMenu &&
                !notificationToggle.contains(
                    event.target
                ) &&
                !notificationMenu.contains(
                    event.target
                )
            ) {

                notificationMenu.classList.add(
                    "hidden"
                );

                notificationToggle.setAttribute(
                    "aria-expanded",
                    "false"
                );

            }


            // Profile
            if (
                profileToggle &&
                profileMenu &&
                !profileToggle.contains(
                    event.target
                ) &&
                !profileMenu.contains(
                    event.target
                )
            ) {

                profileMenu.classList.add(
                    "hidden"
                );

                profileToggle.setAttribute(
                    "aria-expanded",
                    "false"
                );


                if (profileArrow) {

                    profileArrow.classList.remove(
                        "rotate-180"
                    );

                }

            }

        }
    );


    // =====================================================
    // ESCAPE KEY
    // =====================================================

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                closeDropdowns();


                if (searchResults) {

                    searchResults.classList.add(
                        "hidden"
                    );

                }

            }

        }
    );


    // =====================================================
    // PREVENT SEARCH DROPDOWN FROM CLOSING
    // =====================================================

    if (searchResults) {

        searchResults.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

            }
        );

    }


    // =====================================================
    // INITIAL STATE
    // =====================================================

    closeDropdowns();

});