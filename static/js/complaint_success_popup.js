/* =====================================================
   BANTAYBARANGAY
   COMPLAINT SUCCESS POPUP
===================================================== */


document.addEventListener(
    "DOMContentLoaded",
    function () {

        /* =================================================
           GET POPUP
        ================================================= */

        const popup =
            document.getElementById(
                "complaintSuccessPopup"
            );


        /*
         * The popup only exists when Django sends:
         *
         * complaint_submitted = True
         */

        if (!popup) {

            console.log(
                "No complaint success popup on this page."
            );

            return;

        }


        /* =================================================
           OPEN POPUP
        ================================================= */

        openComplaintSuccessPopup();

    }
);


/* =====================================================
   OPEN COMPLAINT SUCCESS POPUP
===================================================== */

function openComplaintSuccessPopup() {

    const popup =
        document.getElementById(
            "complaintSuccessPopup"
        );


    if (!popup) {

        console.warn(
            "Complaint success popup element was not found."
        );

        return;

    }


    /* =================================================
       RESET STATE
    ================================================= */

    popup.classList.remove(
        "hidden"
    );

    popup.classList.remove(
        "popup-closing"
    );


    /* =================================================
       FORCE REFLOW
    ================================================= */

    void popup.offsetWidth;


    /* =================================================
       SHOW POPUP
    ================================================= */

    popup.classList.add(
        "popup-visible"
    );


    popup.setAttribute(
        "aria-hidden",
        "false"
    );


    /* =================================================
       PREVENT BACKGROUND SCROLLING
    ================================================= */

    document.body.classList.add(
        "overflow-hidden"
    );


    /* =================================================
       FOCUS CLOSE BUTTON
    ================================================= */

    const closeButton =
        popup.querySelector(
            "[data-popup-close]"
        );


    if (closeButton) {

        setTimeout(
            function () {

                closeButton.focus();

            },
            100
        );

    }

}


/* =====================================================
   CLOSE COMPLAINT SUCCESS POPUP
===================================================== */

function closeComplaintSuccessPopup() {

    const popup =
        document.getElementById(
            "complaintSuccessPopup"
        );


    if (!popup) {
        return;
    }


    /* =================================================
       CLOSING STATE
    ================================================= */

    popup.classList.add(
        "popup-closing"
    );


    popup.classList.remove(
        "popup-visible"
    );


    popup.setAttribute(
        "aria-hidden",
        "true"
    );


    document.body.classList.remove(
        "overflow-hidden"
    );


    /* =================================================
       HIDE AFTER ANIMATION
    ================================================= */

    setTimeout(
        function () {

            popup.classList.add(
                "hidden"
            );


            popup.classList.remove(
                "popup-closing"
            );

        },
        200
    );

}


/* =====================================================
   CLOSE BUTTON
===================================================== */

document.addEventListener(
    "click",
    function (event) {

        const closeButton =
            event.target.closest(
                "[data-popup-close]"
            );


        if (!closeButton) {
            return;
        }


        event.preventDefault();

        closeComplaintSuccessPopup();

    }
);


/* =====================================================
   CLICK OUTSIDE
===================================================== */

document.addEventListener(
    "click",
    function (event) {

        const popup =
            document.getElementById(
                "complaintSuccessPopup"
            );


        if (!popup) {
            return;
        }


        if (event.target === popup) {

            closeComplaintSuccessPopup();

        }

    }
);


/* =====================================================
   ESCAPE KEY
===================================================== */

document.addEventListener(
    "keydown",
    function (event) {

        if (event.key !== "Escape") {
            return;
        }


        const popup =
            document.getElementById(
                "complaintSuccessPopup"
            );


        if (!popup) {
            return;
        }


        if (
            popup.classList.contains(
                "hidden"
            )
        ) {
            return;
        }


        closeComplaintSuccessPopup();

    }
);


/* =====================================================
   GLOBAL FUNCTIONS
===================================================== */

window.openComplaintSuccessPopup =
    openComplaintSuccessPopup;


window.closeComplaintSuccessPopup =
    closeComplaintSuccessPopup;