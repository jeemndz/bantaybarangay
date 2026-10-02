/* =========================================================
   BANTAYBARANGAY
   RESIDENT PROFILE
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeProfilePage();

    }
);


/* =========================================================
   INITIALIZE
========================================================= */

function initializeProfilePage() {

    initializeContactModal();
    initializeChangePasswordModal();
    initializePasswordToggles();
    initializePasswordValidation();

    initializeHashCopy();
    initializeProfileSync();
    initializeQrDownload();
    initializeFamilyButton();
    initializeSecurityButtons();
    initializeLogoutButton();

}


/* =========================================================
   CONTACT MODAL
========================================================= */

function initializeContactModal() {

    const modal =
        document.getElementById(
            "contactModal"
        );

    const openButton =
        document.getElementById(
            "editContactButton"
        );

    if (!modal) {
        return;
    }


    if (openButton) {

        openButton.addEventListener(
            "click",
            function () {

                openProfileModal(
                    modal
                );

            }
        );

    }


    modal
        .querySelectorAll(
            "[data-close-modal]"
        )
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    closeProfileModal(
                        modal
                    );

                }
            );

        });


    const overlay =
        modal.querySelector(
            ".profile-modal-overlay"
        );


    if (overlay) {

        overlay.addEventListener(
            "click",
            function () {

                closeProfileModal(
                    modal
                );

            }
        );

    }

}


/* =========================================================
   CHANGE PASSWORD MODAL
========================================================= */

function initializeChangePasswordModal() {

    const modal =
        document.getElementById(
            "changePasswordModal"
        );

    const openButton =
        document.getElementById(
            "changePasswordButton"
        );

    if (!modal) {
        return;
    }


    /* =====================================================
       OPEN MODAL
    ===================================================== */

    if (openButton) {

        openButton.addEventListener(
            "click",
            function () {

                resetPasswordForm();

                openProfileModal(
                    modal
                );


                const currentPassword =
                    document.getElementById(
                        "current_password"
                    );


                if (currentPassword) {

                    window.setTimeout(
                        function () {

                            currentPassword.focus();

                        },
                        100
                    );

                }

            }
        );

    }


    /* =====================================================
       CLOSE BUTTONS
    ===================================================== */

    modal
        .querySelectorAll(
            "[data-close-password-modal]"
        )
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    closePasswordModal(
                        modal
                    );

                }
            );

        });


    /* =====================================================
       OVERLAY
    ===================================================== */

    const overlay =
        modal.querySelector(
            ".profile-modal-overlay"
        );


    if (overlay) {

        overlay.addEventListener(
            "click",
            function () {

                closePasswordModal(
                    modal
                );

            }
        );

    }

}


/* =========================================================
   OPEN PROFILE MODAL
========================================================= */

function openProfileModal(modal) {

    if (!modal) {
        return;
    }


    modal.classList.add(
        "show"
    );

    modal.setAttribute(
        "aria-hidden",
        "false"
    );

    document.body.style.overflow =
        "hidden";

}


/* =========================================================
   CLOSE PROFILE MODAL
========================================================= */

function closeProfileModal(modal) {

    if (!modal) {
        return;
    }


    modal.classList.remove(
        "show"
    );

    modal.setAttribute(
        "aria-hidden",
        "true"
    );

    document.body.style.overflow =
        "";

}


/* =========================================================
   CLOSE PASSWORD MODAL
========================================================= */

function closePasswordModal(modal) {

    closeProfileModal(
        modal
    );

    resetPasswordForm();

}


/* =========================================================
   ESCAPE KEY
========================================================= */

document.addEventListener(
    "keydown",
    function (event) {

        if (event.key !== "Escape") {
            return;
        }


        const contactModal =
            document.getElementById(
                "contactModal"
            );

        const passwordModal =
            document.getElementById(
                "changePasswordModal"
            );


        if (
            passwordModal &&
            passwordModal.classList.contains(
                "show"
            )
        ) {

            closePasswordModal(
                passwordModal
            );

            return;

        }


        if (
            contactModal &&
            contactModal.classList.contains(
                "show"
            )
        ) {

            closeProfileModal(
                contactModal
            );

        }

    }
);


/* =========================================================
   PASSWORD SHOW / HIDE
========================================================= */

function initializePasswordToggles() {

    const toggleButtons =
        document.querySelectorAll(
            "[data-password-target]"
        );


    toggleButtons.forEach(
        function (button) {

            button.addEventListener(
                "click",
                function () {

                    const targetId =
                        button.getAttribute(
                            "data-password-target"
                        );

                    if (!targetId) {
                        return;
                    }


                    const input =
                        document.getElementById(
                            targetId
                        );

                    if (!input) {
                        return;
                    }


                    const icon =
                        button.querySelector(
                            "i"
                        );


                    if (
                        input.type ===
                        "password"
                    ) {

                        input.type =
                            "text";

                        button.setAttribute(
                            "aria-label",
                            "Hide password"
                        );


                        if (icon) {

                            icon.classList.remove(
                                "fa-eye"
                            );

                            icon.classList.add(
                                "fa-eye-slash"
                            );

                        }

                    }

                    else {

                        input.type =
                            "password";

                        button.setAttribute(
                            "aria-label",
                            "Show password"
                        );


                        if (icon) {

                            icon.classList.remove(
                                "fa-eye-slash"
                            );

                            icon.classList.add(
                                "fa-eye"
                            );

                        }

                    }

                }
            );

        }
    );

}


/* =========================================================
   PASSWORD VALIDATION
========================================================= */

function initializePasswordValidation() {

    const form =
        document.getElementById(
            "changePasswordForm"
        );

    const newPassword =
        document.getElementById(
            "new_password"
        );

    const confirmPassword =
        document.getElementById(
            "confirm_password"
        );

    const message =
        document.getElementById(
            "passwordMatchMessage"
        );


    if (
        !form ||
        !newPassword ||
        !confirmPassword
    ) {
        return;
    }


    /* =====================================================
       LIVE VALIDATION
    ===================================================== */

    newPassword.addEventListener(
        "input",
        validatePasswordMatch
    );

    confirmPassword.addEventListener(
        "input",
        validatePasswordMatch
    );


    /* =====================================================
       SUBMIT VALIDATION
    ===================================================== */

    form.addEventListener(
        "submit",
        function (event) {

            const newValue =
                newPassword.value;

            const confirmValue =
                confirmPassword.value;


            if (newValue.length < 8) {

                event.preventDefault();

                showPasswordMessage(
                    "Password must contain at least 8 characters.",
                    "error"
                );

                newPassword.focus();

                return;

            }


            if (
                newValue !==
                confirmValue
            ) {

                event.preventDefault();

                showPasswordMessage(
                    "Passwords do not match.",
                    "error"
                );

                confirmPassword.focus();

                return;

            }


            showPasswordMessage(
                "Passwords match.",
                "success"
            );


            const submitButton =
                document.getElementById(
                    "savePasswordButton"
                );


            if (submitButton) {

                submitButton.disabled =
                    true;

                submitButton.innerHTML =
                    '<i class="fa-solid fa-spinner fa-spin"></i> Changing Password...';

            }

        }
    );


    /* =====================================================
       CHECK MATCH
    ===================================================== */

    function validatePasswordMatch() {

        const newValue =
            newPassword.value;

        const confirmValue =
            confirmPassword.value;


        if (!confirmValue) {

            clearPasswordMessage();

            confirmPassword.setCustomValidity(
                ""
            );

            return;

        }


        if (
            newValue ===
            confirmValue
        ) {

            confirmPassword.setCustomValidity(
                ""
            );

            showPasswordMessage(
                "Passwords match.",
                "success"
            );

        }

        else {

            confirmPassword.setCustomValidity(
                "Passwords do not match."
            );

            showPasswordMessage(
                "Passwords do not match.",
                "error"
            );

        }

    }


    /* =====================================================
       SHOW MESSAGE
    ===================================================== */

    function showPasswordMessage(
        text,
        type
    ) {

        if (!message) {
            return;
        }


        message.textContent =
            text;

        message.classList.remove(
            "success",
            "error"
        );


        if (type) {

            message.classList.add(
                type
            );

        }

    }


    /* =====================================================
       CLEAR MESSAGE
    ===================================================== */

    function clearPasswordMessage() {

        if (!message) {
            return;
        }


        message.textContent =
            "";

        message.classList.remove(
            "success",
            "error"
        );

    }

}


/* =========================================================
   RESET PASSWORD FORM
========================================================= */

function resetPasswordForm() {

    const form =
        document.getElementById(
            "changePasswordForm"
        );

    const message =
        document.getElementById(
            "passwordMatchMessage"
        );

    const submitButton =
        document.getElementById(
            "savePasswordButton"
        );


    if (form) {

        form.reset();

    }


    if (message) {

        message.textContent =
            "";

        message.classList.remove(
            "success",
            "error"
        );

    }


    document
        .querySelectorAll(
            "#changePasswordModal input[type='text'], " +
            "#changePasswordModal input[type='password']"
        )
        .forEach(function (input) {

            input.type =
                "password";

            input.setCustomValidity(
                ""
            );

        });


    document
        .querySelectorAll(
            "#changePasswordModal .password-toggle"
        )
        .forEach(function (button) {

            const icon =
                button.querySelector(
                    "i"
                );


            button.setAttribute(
                "aria-label",
                "Show password"
            );


            if (icon) {

                icon.classList.remove(
                    "fa-eye-slash"
                );

                icon.classList.add(
                    "fa-eye"
                );

            }

        });


    if (submitButton) {

        submitButton.disabled =
            false;

        submitButton.innerHTML =
            '<i class="fa-solid fa-lock"></i> Change Password';

    }

}


/* =========================================================
   COPY BLOCKCHAIN HASH
========================================================= */

function initializeHashCopy() {

    const copyButton =
        document.getElementById(
            "copyHashButton"
        );

    const hash =
        document.getElementById(
            "identityHash"
        );


    if (
        !copyButton ||
        !hash
    ) {
        return;
    }


    copyButton.addEventListener(
        "click",
        async function () {

            const value =
                hash.textContent.trim();


            try {

                await navigator.clipboard.writeText(
                    value
                );

                showProfileToast(
                    "Identity hash copied to clipboard."
                );

            }

            catch (error) {

                fallbackCopyText(
                    value
                );

            }

        }
    );

}


/* =========================================================
   FALLBACK COPY
========================================================= */

function fallbackCopyText(value) {

    const textarea =
        document.createElement(
            "textarea"
        );

    textarea.value =
        value;

    textarea.style.position =
        "fixed";

    textarea.style.opacity =
        "0";


    document.body.appendChild(
        textarea
    );

    textarea.select();


    try {

        document.execCommand(
            "copy"
        );

        showProfileToast(
            "Identity hash copied to clipboard."
        );

    }

    catch (error) {

        showProfileToast(
            "Unable to copy identity hash."
        );

    }


    textarea.remove();

}


/* =========================================================
   PROFILE SYNC
========================================================= */

function initializeProfileSync() {

    const button =
        document.getElementById(
            "syncProfileButton"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        function () {

            if (
                button.classList.contains(
                    "is-loading"
                )
            ) {
                return;
            }


            button.classList.add(
                "is-loading"
            );

            button.disabled =
                true;


            window.setTimeout(
                function () {

                    button.classList.remove(
                        "is-loading"
                    );

                    button.disabled =
                        false;

                    showProfileToast(
                        "Resident profile synchronized."
                    );

                },
                900
            );

        }
    );

}


/* =========================================================
   QR DOWNLOAD
========================================================= */

function initializeQrDownload() {

    const button =
        document.getElementById(
            "downloadQrButton"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        function () {

            showProfileToast(
                "QR ID download will use the resident's generated QR file."
            );

        }
    );

}


/* =========================================================
   FAMILY MEMBERS
========================================================= */

function initializeFamilyButton() {

    const button =
        document.getElementById(
            "viewFamilyButton"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        function () {

            showProfileToast(
                "Family member list selected."
            );

        }
    );

}


/* =========================================================
   SECURITY BUTTONS
========================================================= */

function initializeSecurityButtons() {

    const twoFactorButton =
        document.getElementById(
            "configure2faButton"
        );

    const alertsButton =
        document.getElementById(
            "manageAlertsButton"
        );

    const logoutDevicesButton =
        document.getElementById(
            "logoutDevicesButton"
        );


    if (twoFactorButton) {

        twoFactorButton.addEventListener(
            "click",
            function () {

                showProfileToast(
                    "Two-factor authentication settings selected."
                );

            }
        );

    }


    if (alertsButton) {

        alertsButton.addEventListener(
            "click",
            function () {

                showProfileToast(
                    "Notification settings selected."
                );

            }
        );

    }


    if (logoutDevicesButton) {

        logoutDevicesButton.addEventListener(
            "click",
            function () {

                const confirmed =
                    window.confirm(
                        "Log out all other devices?"
                    );


                if (!confirmed) {
                    return;
                }


                showProfileToast(
                    "Other sessions have been selected for logout."
                );

            }
        );

    }

}


/* =========================================================
   LOGOUT
========================================================= */

function initializeLogoutButton() {

    const button =
        document.getElementById(
            "logoutButton"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        function (event) {

            event.preventDefault();


            const confirmed =
                window.confirm(
                    "Are you sure you want to log out?"
                );


            if (!confirmed) {
                return;
            }


            /*
             * This matches your current logout URL.
             */

            window.location.href =
                "/logout/";

        }
    );

}


/* =========================================================
   TOAST
========================================================= */

let profileToastTimeout =
    null;


function showProfileToast(message) {

    const toast =
        document.getElementById(
            "profileToast"
        );

    const text =
        document.getElementById(
            "profileToastText"
        );


    if (
        !toast ||
        !text
    ) {
        return;
    }


    text.textContent =
        message;

    toast.classList.add(
        "show"
    );


    if (profileToastTimeout) {

        window.clearTimeout(
            profileToastTimeout
        );

    }


    profileToastTimeout =
        window.setTimeout(
            function () {

                toast.classList.remove(
                    "show"
                );

            },
            3000
        );

}