/* =========================================================
   BANTAYBARANGAY
   USER MANAGEMENT JAVASCRIPT
========================================================= */

let selectedUser = null;


/* =========================================================
   INITIALIZATION
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    initializeIcons();

    initializeSearch();

    initializeFilters();

    initializeCreateForm();

    initializeModalEvents();

});


/* =========================================================
   LUCIDE ICONS
========================================================= */

function initializeIcons() {

    if (typeof lucide !== "undefined") {

        lucide.createIcons();

    }

}


function refreshIcons() {

    if (typeof lucide !== "undefined") {

        lucide.createIcons();

    }

}


/* =========================================================
   SEARCH
========================================================= */

function initializeSearch() {

    const searchInput =
        document.getElementById("userSearch");

    if (!searchInput) {
        return;
    }

    searchInput.addEventListener(
        "input",
        filterUsers
    );

}


function focusSearch() {

    const searchInput =
        document.getElementById("userSearch");

    if (searchInput) {

        searchInput.focus();

    }

}


/* =========================================================
   FILTERS
========================================================= */

function initializeFilters() {

    const roleFilter =
        document.getElementById("roleFilter");

    const statusFilter =
        document.getElementById("statusFilter");

    const clearFilters =
        document.getElementById("clearFilters");


    if (roleFilter) {

        roleFilter.addEventListener(
            "change",
            filterUsers
        );

    }


    if (statusFilter) {

        statusFilter.addEventListener(
            "change",
            filterUsers
        );

    }


    if (clearFilters) {

        clearFilters.addEventListener(
            "click",
            function () {

                const search =
                    document.getElementById(
                        "userSearch"
                    );

                if (search) {
                    search.value = "";
                }

                if (roleFilter) {
                    roleFilter.value = "";
                }

                if (statusFilter) {
                    statusFilter.value = "";
                }

                filterUsers();

            }
        );

    }

}


/* =========================================================
   FILTER USERS
========================================================= */

function filterUsers() {

    const searchInput =
        document.getElementById("userSearch");

    const roleFilter =
        document.getElementById("roleFilter");

    const statusFilter =
        document.getElementById("statusFilter");


    const searchValue =
        searchInput
            ? searchInput.value
                .trim()
                .toLowerCase()
            : "";


    const roleValue =
        roleFilter
            ? roleFilter.value.toLowerCase()
            : "";


    const statusValue =
        statusFilter
            ? statusFilter.value.toLowerCase()
            : "";


    const rows =
        document.querySelectorAll(
            "#usersTableBody .user-row"
        );


    let visibleCount = 0;


    rows.forEach(function (row) {

        const username =
            row.dataset.username || "";

        const email =
            row.dataset.email || "";

        const role =
            row.dataset.role || "";

        const status =
            row.dataset.status || "";


        const matchesSearch =
            !searchValue ||
            username.includes(searchValue) ||
            email.includes(searchValue) ||
            role.includes(searchValue) ||
            status.includes(searchValue);


        const matchesRole =
            !roleValue ||
            role === roleValue;


        const matchesStatus =
            !statusValue ||
            status === statusValue;


        const shouldDisplay =
            matchesSearch &&
            matchesRole &&
            matchesStatus;


        row.style.display =
            shouldDisplay
                ? ""
                : "none";


        if (shouldDisplay) {

            visibleCount++;

        }

    });


    updateVisibleUserCount(visibleCount);

}


/* =========================================================
   USER COUNT
========================================================= */

function updateVisibleUserCount(count) {

    const counter =
        document.getElementById(
            "userCountText"
        );

    if (!counter) {
        return;
    }

    counter.textContent =
        "Showing " +
        count +
        " user" +
        (count === 1 ? "" : "s");

}


/* =========================================================
   SELECT USER ROW
========================================================= */

function selectUserRow(row) {

    if (!row) {
        return;
    }


    document
        .querySelectorAll(".user-row")
        .forEach(function (item) {

            item.classList.remove(
                "selected"
            );

        });


    row.classList.add("selected");


    const actionButtons =
        row.querySelectorAll(
            ".table-actions button"
        );


    if (actionButtons.length > 0) {

        actionButtons[0].click();

    }

}


/* =========================================================
   SHOW USER DETAILS
========================================================= */

function showUserDetails(
    id,
    username,
    email,
    role,
    isActive,
    created
) {

    const active =
        String(isActive).toLowerCase()
        === "true";


    selectedUser = {
        id: id,
        username: username,
        email: email,
        role: role,
        isActive: active,
        created: created
    };


    const empty =
        document.getElementById(
            "profileEmpty"
        );

    const content =
        document.getElementById(
            "profileContent"
        );


    if (empty) {

        empty.classList.add("hidden");

    }


    if (content) {

        content.classList.remove("hidden");

    }


    setText(
        "profileUsername",
        username
    );

    setText(
        "profileRole",
        formatRole(role)
    );

    setText(
        "profileEmail",
        email
    );

    setText(
        "profileUserId",
        id
    );

    setText(
        "profileRoleValue",
        formatRole(role)
    );

    setText(
        "profileStatus",
        active
            ? "Active"
            : "Disabled"
    );

    setText(
        "profileCreated",
        created
    );


    const avatar =
        document.getElementById(
            "profileAvatar"
        );

    if (avatar) {

        avatar.textContent =
            username
                ? username
                    .charAt(0)
                    .toUpperCase()
                : "U";

    }


    updateProfileStatus(active);

    refreshIcons();

}


/* =========================================================
   PROFILE STATUS
========================================================= */

function updateProfileStatus(active) {

    const indicator =
        document.getElementById(
            "profileStatusIndicator"
        );

    const button =
        document.getElementById(
            "disableAccountButton"
        );


    if (indicator) {

        indicator.classList.toggle(
            "disabled",
            !active
        );

    }


    if (!button) {
        return;
    }


    if (active) {

        button.classList.remove(
            "enable"
        );

        button.innerHTML = `
            <i data-lucide="user-x"></i>
            Disable Account
        `;

    } else {

        button.classList.add(
            "enable"
        );

        button.innerHTML = `
            <i data-lucide="user-check"></i>
            Enable Account
        `;

    }


    refreshIcons();

}


/* =========================================================
   TEXT HELPER
========================================================= */

function setText(id, value) {

    const element =
        document.getElementById(id);

    if (element) {

        element.textContent =
            value || "—";

    }

}


/* =========================================================
   FORMAT ROLE
========================================================= */

function formatRole(role) {

    if (!role) {
        return "—";
    }


    const normalized =
        role.toLowerCase();


    if (
        normalized === "admin" ||
        normalized === "administrator"
    ) {

        return "Administrator";

    }


    if (normalized === "officer") {

        return "Officer";

    }


    if (normalized === "staff") {

        return "Staff";

    }


    return (
        role.charAt(0).toUpperCase() +
        role.slice(1)
    );

}


/* =========================================================
   CREATE USER MODAL
========================================================= */

function openCreateUserModal() {

    openModal("createUserModal");


    const username =
        document.getElementById(
            "createUsername"
        );


    setTimeout(function () {

        if (username) {
            username.focus();
        }

    }, 100);

}


function closeCreateUserModal() {

    closeModal("createUserModal");

}


/* =========================================================
   EDIT USER
========================================================= */

function openEditUserModal(
    id,
    username,
    email,
    role,
    isActive
) {

    document.getElementById(
        "editUserId"
    ).value = id;


    document.getElementById(
        "editUsername"
    ).value = username;


    document.getElementById(
        "editEmail"
    ).value = email;


    const roleSelect =
        document.getElementById(
            "editRole"
        );


    if (roleSelect) {

        let normalizedRole =
            String(role)
                .toLowerCase();


        if (
            normalizedRole ===
            "administrator"
        ) {

            normalizedRole = "admin";

        }


        roleSelect.value =
            normalizedRole;

    }


    document.getElementById(
        "editStatus"
    ).value =
        String(isActive)
            .toLowerCase()
            === "true"
            ? "1"
            : "0";


    openModal("editUserModal");

}


function editSelectedUser() {

    if (!selectedUser) {

        return;

    }


    openEditUserModal(
        selectedUser.id,
        selectedUser.username,
        selectedUser.email,
        selectedUser.role,
        selectedUser.isActive
            ? "true"
            : "false"
    );

}


function closeEditUserModal() {

    closeModal("editUserModal");

}


/* =========================================================
   RESET PASSWORD
========================================================= */

function openResetPasswordModal() {

    if (!selectedUser) {
        return;
    }


    const userId =
        document.getElementById(
            "resetPasswordUserId"
        );


    if (userId) {

        userId.value =
            selectedUser.id;

    }


    const password =
        document.getElementById(
            "newPassword"
        );


    if (password) {

        password.value = "";

    }


    openModal(
        "resetPasswordModal"
    );

}


function closeResetPasswordModal() {

    closeModal(
        "resetPasswordModal"
    );

}


/* =========================================================
   DISABLE / ENABLE USER
========================================================= */

function openDisableModal() {

    if (!selectedUser) {
        return;
    }


    const userId =
        document.getElementById(
            "disableUserId"
        );

    const action =
        document.getElementById(
            "statusAction"
        );

    const title =
        document.getElementById(
            "disableModalTitle"
        );

    const message =
        document.getElementById(
            "disableModalMessage"
        );

    const button =
        document.getElementById(
            "confirmStatusButton"
        );


    if (userId) {

        userId.value =
            selectedUser.id;

    }


    if (selectedUser.isActive) {

        if (action) {
            action.value =
                "disable_user";
        }

        if (title) {
            title.textContent =
                "Disable Account?";
        }

        if (message) {

            message.textContent =
                selectedUser.username +
                " will no longer be able " +
                "to access BantayBarangay.";

        }

        if (button) {

            button.textContent =
                "Disable Account";

            button.className =
                "btn-danger";

        }

    } else {

        if (action) {
            action.value =
                "enable_user";
        }

        if (title) {
            title.textContent =
                "Enable Account?";
        }

        if (message) {

            message.textContent =
                selectedUser.username +
                " will regain access " +
                "to BantayBarangay.";

        }

        if (button) {

            button.textContent =
                "Enable Account";

            button.className =
                "btn-primary";

        }

    }


    openModal(
        "disableUserModal"
    );

}


function closeDisableModal() {

    closeModal(
        "disableUserModal"
    );

}


/* =========================================================
   GENERIC MODAL
========================================================= */

function openModal(id) {

    const modal =
        document.getElementById(id);


    if (!modal) {
        return;
    }


    modal.classList.remove("hidden");

    document.body.style.overflow =
        "hidden";


    refreshIcons();

}


function closeModal(id) {

    const modal =
        document.getElementById(id);


    if (!modal) {
        return;
    }


    modal.classList.add("hidden");


    const openModal =
        document.querySelector(
            ".modal-overlay:not(.hidden)"
        );


    if (!openModal) {

        document.body.style.overflow =
            "";

    }

}


/* =========================================================
   MODAL EVENTS
========================================================= */

function initializeModalEvents() {

    document
        .querySelectorAll(
            ".modal-overlay"
        )
        .forEach(function (modal) {

            modal.addEventListener(
                "click",
                function (event) {

                    if (
                        event.target === modal
                    ) {

                        closeModal(
                            modal.id
                        );

                    }

                }
            );

        });


    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key !== "Escape"
            ) {
                return;
            }


            const openModal =
                document.querySelector(
                    ".modal-overlay:not(.hidden)"
                );


            if (openModal) {

                closeModal(
                    openModal.id
                );

            }

        }
    );

}


/* =========================================================
   CREATE FORM VALIDATION
========================================================= */

function initializeCreateForm() {

    const form =
        document.getElementById(
            "createUserForm"
        );


    if (!form) {
        return;
    }


    form.addEventListener(
        "submit",
        function (event) {

            const password =
                document.getElementById(
                    "createPassword"
                );

            const confirm =
                document.getElementById(
                    "confirmPassword"
                );

            const error =
                document.getElementById(
                    "passwordMatchError"
                );


            if (
                !password ||
                !confirm
            ) {
                return;
            }


            if (
                password.value !==
                confirm.value
            ) {

                event.preventDefault();


                if (error) {

                    error.classList.remove(
                        "hidden"
                    );

                }


                confirm.focus();

                return;

            }


            if (error) {

                error.classList.add(
                    "hidden"
                );

            }

        }
    );

}


/* =========================================================
   PASSWORD VISIBILITY
========================================================= */

function togglePassword(
    inputId,
    button
) {

    const input =
        document.getElementById(
            inputId
        );


    if (!input) {
        return;
    }


    const showPassword =
        input.type === "password";


    input.type =
        showPassword
            ? "text"
            : "password";


    if (button) {

        button.innerHTML =
            showPassword
                ? '<i data-lucide="eye-off"></i>'
                : '<i data-lucide="eye"></i>';

    }


    refreshIcons();

}


/* =========================================================
   EXPORT USERS
========================================================= */

function exportUsers() {

    const rows =
        document.querySelectorAll(
            "#usersTableBody .user-row"
        );


    if (!rows.length) {

        alert(
            "There are no users to export."
        );

        return;

    }


    const data = [
        [
            "User ID",
            "Username",
            "Email",
            "Role",
            "Status"
        ]
    ];


    rows.forEach(function (row) {

        if (
            row.style.display === "none"
        ) {
            return;
        }


        data.push([
            row.dataset.userId || "",
            row.dataset.username || "",
            row.dataset.email || "",
            row.dataset.role || "",
            row.dataset.status || ""
        ]);

    });


    const csv =
        data
            .map(function (row) {

                return row
                    .map(escapeCSV)
                    .join(",");

            })
            .join("\n");


    const blob =
        new Blob(
            [csv],
            {
                type:
                    "text/csv;charset=utf-8;"
            }
        );


    const url =
        URL.createObjectURL(blob);


    const link =
        document.createElement("a");


    link.href = url;

    link.download =
        "bantaybarangay_users.csv";


    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);


    URL.revokeObjectURL(url);

}


/* =========================================================
   CSV HELPER
========================================================= */

function escapeCSV(value) {

    const stringValue =
        String(value ?? "");


    return (
        '"' +
        stringValue.replace(
            /"/g,
            '""'
        ) +
        '"'
    );

}