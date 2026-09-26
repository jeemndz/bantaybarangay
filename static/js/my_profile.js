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
        document.getElementById("contactModal");

    const openButton =
        document.getElementById("editContactButton");

    if (!modal) {
        return;
    }


    if (openButton) {

        openButton.addEventListener(
            "click",
            function () {

                openProfileModal(modal);

            }
        );

    }


    modal
        .querySelectorAll("[data-close-modal]")
        .forEach(function (button) {

            button.addEventListener(
                "click",
                function () {

                    closeProfileModal(modal);

                }
            );

        });


    const overlay =
        modal.querySelector(".profile-modal-overlay");


    if (overlay) {

        overlay.addEventListener(
            "click",
            function () {

                closeProfileModal(modal);

            }
        );

    }


    document.addEventListener(
        "keydown",
        function (event) {

            if (
                event.key === "Escape" &&
                modal.classList.contains("show")
            ) {

                closeProfileModal(modal);

            }

        }
    );

}


function openProfileModal(modal) {

    modal.classList.add("show");

    modal.setAttribute(
        "aria-hidden",
        "false"
    );

    document.body.style.overflow = "hidden";

}


function closeProfileModal(modal) {

    modal.classList.remove("show");

    modal.setAttribute(
        "aria-hidden",
        "true"
    );

    document.body.style.overflow = "";

}


/* =========================================================
   COPY BLOCKCHAIN HASH
========================================================= */

function initializeHashCopy() {

    const copyButton =
        document.getElementById("copyHashButton");

    const hash =
        document.getElementById("identityHash");


    if (!copyButton || !hash) {
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

                fallbackCopyText(value);

            }

        }
    );

}


/* =========================================================
   FALLBACK COPY
========================================================= */

function fallbackCopyText(value) {

    const textarea =
        document.createElement("textarea");

    textarea.value = value;

    textarea.style.position = "fixed";
    textarea.style.opacity = "0";

    document.body.appendChild(textarea);

    textarea.select();

    try {

        document.execCommand("copy");

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
        document.getElementById("syncProfileButton");


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

            button.disabled = true;


            /*
             * Replace this timeout with a Django
             * fetch/AJAX request later if you want
             * real blockchain synchronization.
             */

            window.setTimeout(
                function () {

                    button.classList.remove(
                        "is-loading"
                    );

                    button.disabled = false;

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
        document.getElementById("downloadQrButton");


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        function () {

            /*
             * Connect this to the real resident
             * QR file when your backend generates it.
             */

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
        document.getElementById("viewFamilyButton");


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
        document.getElementById("logoutButton");


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
             * Change this to your actual Django
             * logout URL if the URL name differs.
             */

            window.location.href = "/logout/";

        }
    );

}


/* =========================================================
   TOAST
========================================================= */

let profileToastTimeout = null;


function showProfileToast(message) {

    const toast =
        document.getElementById("profileToast");

    const text =
        document.getElementById(
            "profileToastText"
        );


    if (!toast || !text) {
        return;
    }


    text.textContent = message;

    toast.classList.add("show");


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