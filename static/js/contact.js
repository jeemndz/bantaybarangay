/* =========================================================
   BANTAYBARANGAY
   CONTACT PAGE
========================================================= */


document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeContactForm();

    }
);


/* =========================================================
   INITIALIZE CONTACT FORM
========================================================= */

function initializeContactForm() {

    const form =
        document.getElementById(
            "contactForm"
        );

    if (!form) {
        return;
    }


    form.addEventListener(
        "submit",
        function (event) {

            event.preventDefault();

            handleContactForm(
                form
            );

        }
    );

}


/* =========================================================
   HANDLE CONTACT FORM
========================================================= */

function handleContactForm(form) {

    const nameInput =
        document.getElementById(
            "contactName"
        );

    const emailInput =
        document.getElementById(
            "contactEmail"
        );

    const subjectInput =
        document.getElementById(
            "contactSubject"
        );

    const categoryInput =
        document.getElementById(
            "contactCategory"
        );

    const messageInput =
        document.getElementById(
            "contactMessage"
        );


    const name =
        nameInput
            ? nameInput.value.trim()
            : "";

    const email =
        emailInput
            ? emailInput.value.trim()
            : "";

    const subject =
        subjectInput
            ? subjectInput.value.trim()
            : "";

    const category =
        categoryInput
            ? categoryInput.value.trim()
            : "";

    const message =
        messageInput
            ? messageInput.value.trim()
            : "";


    /* =====================================================
       REQUIRED FIELDS
    ====================================================== */

    if (
        !name ||
        !email ||
        !subject ||
        !category ||
        !message
    ) {

        showContactNotice(
            "Please complete all required fields.",
            "error"
        );

        return;
    }


    /* =====================================================
       EMAIL VALIDATION
    ====================================================== */

    if (!isValidEmail(email)) {

        showContactNotice(
            "Please enter a valid email address.",
            "error"
        );

        return;
    }


    /* =====================================================
       FRONTEND-ONLY NOTICE
    ====================================================== */

    showContactNotice(
        "Your form is complete. Online inquiry submission " +
        "has not been connected to the BantayBarangay " +
        "backend yet.",
        "info"
    );

}


/* =========================================================
   EMAIL VALIDATION
========================================================= */

function isValidEmail(email) {

    const pattern =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    return pattern.test(
        email
    );

}


/* =========================================================
   FORM NOTICE
========================================================= */

function showContactNotice(
    message,
    type
) {

    const notice =
        document.getElementById(
            "contactFormNotice"
        );

    if (!notice) {
        return;
    }


    notice.textContent =
        message;


    notice.classList.remove(
        "show",
        "info",
        "error"
    );


    notice.classList.add(
        "show",
        type
    );


    notice.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });

}