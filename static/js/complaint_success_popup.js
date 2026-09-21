/* =====================================================
   COMPLAINT SUCCESS POPUP
===================================================== */

function closeComplaintSuccessPopup() {

    const popup =
        document.getElementById("complaintSuccessPopup");

    if (!popup) {
        return;
    }


    popup.classList.add("popup-closing");


    setTimeout(function () {

        popup.remove();

    }, 200);

}


/* =====================================================
   CLOSE WHEN CLICKING OUTSIDE
===================================================== */

document.addEventListener(
    "click",
    function (event) {

        const popup =
            document.getElementById("complaintSuccessPopup");

        if (!popup) {
            return;
        }


        if (event.target === popup) {

            closeComplaintSuccessPopup();

        }

    }
);


/* =====================================================
   CLOSE WITH ESCAPE
===================================================== */

document.addEventListener(
    "keydown",
    function (event) {

        if (event.key === "Escape") {

            closeComplaintSuccessPopup();

        }

    }
);