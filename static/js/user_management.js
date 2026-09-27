/* =========================================================
   BANTAYBARANGAY
   USER MANAGEMENT
========================================================= */

let selectedUser = null;


/* =========================================================
   INITIALIZATION
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    initializeLucideIcons();

    initializeUserSearch();

    initializeUserFilters();

    initializeModalEvents();

    initializeForms();

    updateUserCount();

});


/* =========================================================
   LUCIDE
========================================================= */

function initializeLucideIcons() {

    if (
        window.lucide &&
        typeof window.lucide.createIcons === "function"
    ) {

        window.lucide.createIcons();

    }

}


function refreshLucideIcons() {

    initializeLucideIcons();

}


/* =========================================================
   GET USER FROM ROW
========================================================= */

function getUserFromRow(row) {

    if (!row) {
        return null;
    }


    return {

        id:
            row.dataset.userId || "",

        username:
            row.dataset.username || "",

        email:
            row.dataset.email || "",

        role:
            row.dataset.role || "",

        status:
            row.dataset.status || "",

        active:
            row.dataset.active === "true",

        created:
            row.dataset.created || "—",

        row:
            row

    };

}


/* =========================================================
   SELECT USER
========================================================= */

function selectUserRow(row) {

    if (!row) {
        return;
    }


    /* REMOVE PREVIOUS SELECTION */

    document
        .querySelectorAll(".user-row")
        .forEach(function (currentRow) {

            currentRow.classList.remove(
                "selected"
            );

        });


    /* SELECT ROW */

    row.classList.add(
        "selected"
    );


    /* STORE USER */

    selectedUser =
        getUserFromRow(row);


    if (!selectedUser) {
        return;
    }


    /* DISPLAY PROFILE */

    displaySelectedUser();

}


/* =========================================================
   DISPLAY SELECTED USER
========================================================= */

function displaySelectedUser() {

    if (!selectedUser) {
        return;
    }


    const emptyState =
        document.getElementById(
            "profileEmpty"
        );

    const profileContent =
        document.getElementById(
            "profileContent"
        );


    /* HIDE EMPTY STATE */

    if (emptyState) {

        emptyState.classList.add(
            "hidden"
        );

    }


    /* SHOW PROFILE */

    if (profileContent) {

        profileContent.classList.remove(
            "hidden"
        );

    }


    /* USERNAME */

    setElementText(
        "profileUsername",
        selectedUser.username
    );


    /* ROLE */

    setElementText(
        "profileRole",
        formatRole(
            selectedUser.role
        )
    );


    /* USER ID */

    setElementText(
        "profileUserId",
        selectedUser.id
    );


    /* EMAIL */

    setElementText(
        "profileEmail",
        selectedUser.email || "No email"
    );


    /* STATUS */

    setElementText(
        "profileStatus",
        selectedUser.active
            ? "Active"
            : "Disabled"
    );


    /* CREATED */

    setElementText(
        "profileCreated",
        selectedUser.created
    );


    /* AVATAR */

    const avatar =
        document.getElementById(
            "profileAvatar"
        );


    if (avatar) {

        avatar.textContent =
            selectedUser.username
                ? selectedUser.username
                    .charAt(0)
                    .toUpperCase()
                : "U";

    }


    updateSelectedUserStatus();


    refreshLucideIcons();

}


/* =========================================================
   SET TEXT
========================================================= */

function setElementText(id, text) {

    const element =
        document.getElementById(id);


    if (!element) {
        return;
    }


    element.textContent =
        text || "—";

}


/* =========================================================
   FORMAT ROLE
========================================================= */

function formatRole(role) {

    const value =
        String(
            role || ""
        ).toLowerCase();


    if (value === "admin") {

        return "Administrator";

    }


    if (value === "official") {

        return "Barangay Official";

    }


    if (!value) {

        return "—";

    }


    return (
        value.charAt(0).toUpperCase() +
        value.slice(1)
    );

}


/* =========================================================
   UPDATE STATUS BUTTON
========================================================= */

function updateSelectedUserStatus() {

    if (!selectedUser) {
        return;
    }


    const statusIndicator =
        document.getElementById(
            "profileStatusIndicator"
        );

    const button =
        document.getElementById(
            "disableAccountButton"
        );

    const text =
        document.getElementById(
            "disableAccountText"
        );

    const icon =
        document.getElementById(
            "disableAccountIcon"
        );


    /* STATUS INDICATOR */

    if (statusIndicator) {

        if (selectedUser.active) {

            statusIndicator.classList.remove(
                "disabled"
            );

        } else {

            statusIndicator.classList.add(
                "disabled"
            );

        }

    }


    if (!button) {
        return;
    }


    /* ACTIVE USER */

    if (selectedUser.active) {

        button.classList.remove(
            "enable"
        );


        if (text) {

            text.textContent =
                "Disable Account";

        }


        if (icon) {

            icon.setAttribute(
                "data-lucide",
                "user-x"
            );

        }

    }


    /* DISABLED USER */

    else {

        button.classList.add(
            "enable"
        );


        if (text) {

            text.textContent =
                "Enable Account";

        }


        if (icon) {

            icon.setAttribute(
                "data-lucide",
                "user-check"
            );

        }

    }


    refreshLucideIcons();

}


/* =========================================================
   VIEW BUTTON
========================================================= */

function viewUserFromButton(
    event,
    button
) {

    event.preventDefault();

    event.stopPropagation();


    const row =
        button.closest(
            ".user-row"
        );


    if (!row) {
        return;
    }


    selectUserRow(row);

}


/* =========================================================
   EDIT BUTTON
========================================================= */

function editUserFromButton(
    event,
    button
) {

    event.preventDefault();

    event.stopPropagation();


    const row =
        button.closest(
            ".user-row"
        );


    if (!row) {
        return;
    }


    selectUserRow(row);


    editSelectedUser();

}


/* =========================================================
   MORE BUTTON
========================================================= */

function moreUserActions(
    event,
    button
) {

    event.preventDefault();

    event.stopPropagation();


    const row =
        button.closest(
            ".user-row"
        );


    if (!row) {
        return;
    }


    selectUserRow(row);


    openDisableModal();

}


/* =========================================================
   EDIT SELECTED USER
========================================================= */

function editSelectedUser() {

    if (!selectedUser) {

        alert(
            "Please select a user first."
        );

        return;

    }


    const userId =
        document.getElementById(
            "editUserId"
        );

    const username =
        document.getElementById(
            "editUsername"
        );

    const email =
        document.getElementById(
            "editEmail"
        );

    const role =
        document.getElementById(
            "editRole"
        );

    const status =
        document.getElementById(
            "editStatus"
        );


    if (userId) {

        userId.value =
            selectedUser.id;

    }


    if (username) {

        username.value =
            selectedUser.username;

    }


    if (email) {

        email.value =
            selectedUser.email;

    }


    if (role) {

        role.value =
            selectedUser.role;

    }


    if (status) {

        status.value =
            selectedUser.active
                ? "1"
                : "0";

    }


    openModal(
        "editUserModal"
    );

}


/* =========================================================
   CREATE USER
========================================================= */

function openCreateUserModal() {

    const form =
        document.getElementById(
            "createUserForm"
        );


    if (form) {

        form.reset();

    }


    openModal(
        "createUserModal"
    );


    setTimeout(
        function () {

            const username =
                document.getElementById(
                    "createUsername"
                );


            if (username) {

                username.focus();

            }

        },
        100
    );

}


function closeCreateUserModal() {

    closeModal(
        "createUserModal"
    );

}


/* =========================================================
   EDIT MODAL
========================================================= */

function closeEditUserModal() {

    closeModal(
        "editUserModal"
    );

}


/* =========================================================
   RESET PASSWORD
========================================================= */

function openResetPasswordModal() {

    if (!selectedUser) {

        alert(
            "Please select a user first."
        );

        return;

    }


    const userId =
        document.getElementById(
            "resetPasswordUserId"
        );

    const password =
        document.getElementById(
            "newPassword"
        );


    if (userId) {

        userId.value =
            selectedUser.id;

    }


    if (password) {

        password.value = "";

    }


    openModal(
        "resetPasswordModal"
    );


    setTimeout(
        function () {

            if (password) {

                password.focus();

            }

        },
        100
    );

}


function closeResetPasswordModal() {

    closeModal(
        "resetPasswordModal"
    );

}


/* =========================================================
   ENABLE / DISABLE
========================================================= */

function openDisableModal() {

    if (!selectedUser) {

        alert(
            "Please select a user first."
        );

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


    /* DISABLE */

    if (selectedUser.active) {

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
                " will no longer be able to access " +
                "BantayBarangay until the account is enabled again.";

        }


        if (button) {

            button.textContent =
                "Disable Account";

            button.className =
                "btn-danger";

        }

    }


    /* ENABLE */

    else {

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
                " will regain access to BantayBarangay.";

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
   MODALS
========================================================= */

function openModal(id) {

    const modal =
        document.getElementById(id);


    if (!modal) {

        console.error(
            "Modal not found:",
            id
        );

        return;

    }


    modal.classList.remove(
        "hidden"
    );


    document.body.style.overflow =
        "hidden";


    refreshLucideIcons();

}


function closeModal(id) {

    const modal =
        document.getElementById(id);


    if (!modal) {
        return;
    }


    modal.classList.add(
        "hidden"
    );


    const remainingModal =
        document.querySelector(
            ".modal-overlay:not(.hidden)"
        );


    if (!remainingModal) {

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
                        event.target ===
                        modal
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
                event.key !==
                "Escape"
            ) {
                return;
            }


            const modal =
                document.querySelector(
                    ".modal-overlay:not(.hidden)"
                );


            if (modal) {

                closeModal(
                    modal.id
                );

            }

        }
    );

}


/* =========================================================
   PASSWORD TOGGLE
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


    const hidden =
        input.type ===
        "password";


    input.type =
        hidden
            ? "text"
            : "password";


    if (button) {

        button.innerHTML =
            hidden
                ? '<i data-lucide="eye-off"></i>'
                : '<i data-lucide="eye"></i>';

    }


    refreshLucideIcons();

}


/* =========================================================
   SEARCH
========================================================= */

function initializeUserSearch() {

    const search =
        document.getElementById(
            "userSearchInput"
        );


    if (!search) {
        return;
    }


    search.addEventListener(
        "input",
        filterUsers
    );

}


function focusSearch() {

    const search =
        document.getElementById(
            "userSearchInput"
        );


    if (search) {

        search.focus();

    }

}


/* =========================================================
   FILTER EVENTS
========================================================= */

function initializeUserFilters() {

    const role =
        document.getElementById(
            "roleFilter"
        );

    const status =
        document.getElementById(
            "statusFilter"
        );

    const clear =
        document.getElementById(
            "clearFilters"
        );


    if (role) {

        role.addEventListener(
            "change",
            filterUsers
        );

    }


    if (status) {

        status.addEventListener(
            "change",
            filterUsers
        );

    }


    if (clear) {

        clear.addEventListener(
            "click",
            clearUserFilters
        );

    }

}


/* =========================================================
   FILTER USERS
========================================================= */

function filterUsers() {

    const searchElement =
        document.getElementById(
            "userSearchInput"
        );

    const roleElement =
        document.getElementById(
            "roleFilter"
        );

    const statusElement =
        document.getElementById(
            "statusFilter"
        );


    const search =
        searchElement
            ? searchElement.value
                .trim()
                .toLowerCase()
            : "";


    const role =
        roleElement
            ? roleElement.value
                .toLowerCase()
            : "";


    const status =
        statusElement
            ? statusElement.value
                .toLowerCase()
            : "";


    let visible =
        0;


    document
        .querySelectorAll(
            "#usersTableBody .user-row"
        )
        .forEach(function (row) {

            const username =
                (
                    row.dataset.username ||
                    ""
                ).toLowerCase();

            const email =
                (
                    row.dataset.email ||
                    ""
                ).toLowerCase();

            const userRole =
                (
                    row.dataset.role ||
                    ""
                ).toLowerCase();

            const userStatus =
                (
                    row.dataset.status ||
                    ""
                ).toLowerCase();


            const searchMatch =
                !search ||
                username.includes(search) ||
                email.includes(search) ||
                userRole.includes(search) ||
                userStatus.includes(search);


            const roleMatch =
                !role ||
                userRole === role;


            const statusMatch =
                !status ||
                userStatus === status;


            const show =
                searchMatch &&
                roleMatch &&
                statusMatch;


            row.style.display =
                show
                    ? ""
                    : "none";


            if (show) {

                visible++;

            }

        });


    updateUserCount(
        visible
    );

}


/* =========================================================
   CLEAR FILTERS
========================================================= */

function clearUserFilters() {

    const search =
        document.getElementById(
            "userSearchInput"
        );

    const role =
        document.getElementById(
            "roleFilter"
        );

    const status =
        document.getElementById(
            "statusFilter"
        );


    if (search) {
        search.value = "";
    }


    if (role) {
        role.value = "";
    }


    if (status) {
        status.value = "";
    }


    filterUsers();

}


/* =========================================================
   USER COUNT
========================================================= */

function updateUserCount(
    count = null
) {

    const counter =
        document.getElementById(
            "userCountText"
        );


    if (!counter) {
        return;
    }


    if (count === null) {

        count =
            document.querySelectorAll(
                "#usersTableBody .user-row"
            ).length;

    }


    counter.textContent =
        "Showing " +
        count +
        " user" +
        (
            count === 1
                ? ""
                : "s"
        );

}


/* =========================================================
   FORM VALIDATION
========================================================= */

function initializeForms() {

    const createForm =
        document.getElementById(
            "createUserForm"
        );

    const resetForm =
        document.getElementById(
            "resetPasswordForm"
        );


    if (createForm) {

        createForm.addEventListener(
            "submit",
            function (event) {

                const password =
                    document.getElementById(
                        "createPassword"
                    );


                if (
                    password &&
                    password.value.length < 8
                ) {

                    event.preventDefault();

                    alert(
                        "Password must contain at least 8 characters."
                    );

                    password.focus();

                }

            }
        );

    }


    if (resetForm) {

        resetForm.addEventListener(
            "submit",
            function (event) {

                const password =
                    document.getElementById(
                        "newPassword"
                    );


                if (
                    password &&
                    password.value.length < 8
                ) {

                    event.preventDefault();

                    alert(
                        "Password must contain at least 8 characters."
                    );

                    password.focus();

                }

            }
        );

    }

}


/* =========================================================
   EXPORT
========================================================= */

function exportUsers() {

    const rows =
        document.querySelectorAll(
            "#usersTableBody .user-row"
        );


    const data = [
        [
            "User ID",
            "Username",
            "Email",
            "Role",
            "Status",
            "Created"
        ]
    ];


    rows.forEach(function (row) {

        if (
            row.style.display ===
            "none"
        ) {
            return;
        }


        data.push(
            [
                row.dataset.userId || "",
                row.dataset.username || "",
                row.dataset.email || "",
                formatRole(
                    row.dataset.role
                ),
                row.dataset.status || "",
                row.dataset.created || ""
            ]
        );

    });


    if (data.length === 1) {

        alert(
            "There are no users to export."
        );

        return;

    }


    const csv =
        data
            .map(function (row) {

                return row
                    .map(
                        escapeCSV
                    )
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
        URL.createObjectURL(
            blob
        );


    const link =
        document.createElement(
            "a"
        );


    link.href =
        url;

    link.download =
        "bantaybarangay_users.csv";


    document.body.appendChild(
        link
    );


    link.click();


    link.remove();


    URL.revokeObjectURL(
        url
    );

}


/* =========================================================
   CSV ESCAPE
========================================================= */

function escapeCSV(value) {

    const string =
        String(
            value ?? ""
        );


    return (
        '"' +
        string.replace(
            /"/g,
            '""'
        ) +
        '"'
    );

}