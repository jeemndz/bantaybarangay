/* =========================================================
   BANTAYBARANGAY
   COMPLAINT MANAGEMENT
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeComplaintMessages();

    }
);


/* =========================================================
   DJANGO MESSAGES
========================================================= */

function initializeComplaintMessages() {

    document
        .querySelectorAll(
            ".complaint-message"
        )
        .forEach(function (message) {

            const closeButton =
                message.querySelector(
                    ".complaint-message-close"
                );


            if (closeButton) {

                closeButton.addEventListener(
                    "click",
                    function () {

                        hideComplaintMessage(
                            message
                        );

                    }
                );

            }


            window.setTimeout(
                function () {

                    hideComplaintMessage(
                        message
                    );

                },

                5000
            );

        });

}


/* =========================================================
   HIDE MESSAGE
========================================================= */

function hideComplaintMessage(message) {

    if (!message) {
        return;
    }


    message.classList.add(
        "is-hiding"
    );


    window.setTimeout(
        function () {

            message.remove();

        },

        200
    );

}