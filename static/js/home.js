document.addEventListener("DOMContentLoaded", function () {

    /* =====================================================
       SCROLL REVEAL
    ===================================================== */

    const animatedElements = document.querySelectorAll(
        ".scroll-reveal, " +
        ".quick-card, " +
        ".service-card, " +
        ".announcement-card, " +
        ".project-card, " +
        ".community-card"
    );

    if ("IntersectionObserver" in window) {

        const observer = new IntersectionObserver(
            function (entries) {

                entries.forEach(function (entry) {

                    if (entry.isIntersecting) {

                        entry.target.classList.add("show");

                        observer.unobserve(entry.target);

                    }

                });

            },
            {
                threshold: 0.15
            }
        );


        animatedElements.forEach(function (element, index) {

            element.style.transitionDelay =
                `${(index % 4) * 0.1}s`;

            observer.observe(element);

        });

    } else {

        animatedElements.forEach(function (element) {
            element.classList.add("show");
        });

    }



    /* =====================================================
       NUMBER COUNTING EFFECT
    ===================================================== */

    const counters = document.querySelectorAll(".counter");


    if ("IntersectionObserver" in window && counters.length > 0) {

        const counterObserver = new IntersectionObserver(
            function (entries) {

                entries.forEach(function (entry) {

                    if (!entry.isIntersecting) {
                        return;
                    }


                    const counter = entry.target;


                    const target =
                        parseFloat(counter.dataset.target);


                    if (isNaN(target)) {
                        return;
                    }


                    const isDecimal =
                        counter.dataset.decimal === "true";


                    const duration = 1800;

                    const startTime =
                        performance.now();


                    function updateCounter(currentTime) {

                        const elapsed =
                            currentTime - startTime;


                        const progress =
                            Math.min(
                                elapsed / duration,
                                1
                            );


                        /*
                         * Ease-out animation
                         */
                        const easeOut =
                            1 -
                            Math.pow(
                                1 - progress,
                                3
                            );


                        const currentValue =
                            target * easeOut;


                        if (isDecimal) {

                            counter.textContent =
                                currentValue.toFixed(1);

                        } else {

                            counter.textContent =
                                Math.floor(currentValue)
                                    .toLocaleString();

                        }


                        if (progress < 1) {

                            requestAnimationFrame(
                                updateCounter
                            );

                        } else {

                            /*
                             * Make sure the final
                             * value is exact.
                             */

                            if (isDecimal) {

                                counter.textContent =
                                    target.toFixed(1);

                            } else {

                                counter.textContent =
                                    target.toLocaleString();

                            }

                        }

                    }


                    requestAnimationFrame(
                        updateCounter
                    );


                    /*
                     * Prevent the same counter
                     * from running again.
                     */

                    counterObserver.unobserve(counter);

                });

            },
            {
                threshold: 0.5
            }
        );


        counters.forEach(function (counter) {

            counterObserver.observe(counter);

        });

    } else {

        /*
         * Fallback for browsers without
         * IntersectionObserver.
         */

        counters.forEach(function (counter) {

            const target =
                parseFloat(counter.dataset.target);

            const isDecimal =
                counter.dataset.decimal === "true";


            if (isDecimal) {

                counter.textContent =
                    target.toFixed(1);

            } else {

                counter.textContent =
                    target.toLocaleString();

            }

        });

    }



    /* =====================================================
       PROFILE DROPDOWN
    ===================================================== */

    const profileButton =
        document.querySelector(".profile-button");

    const profileDropdown =
        document.querySelector(".profile-dropdown");


    if (profileButton && profileDropdown) {

        profileButton.addEventListener(
            "click",
            function (event) {

                event.stopPropagation();

                profileDropdown.classList.toggle("show");

            }
        );


        /*
         * Close dropdown when clicking
         * anywhere outside it.
         */

        document.addEventListener(
            "click",
            function (event) {

                if (
                    !profileButton.contains(event.target) &&
                    !profileDropdown.contains(event.target)
                ) {

                    profileDropdown.classList.remove("show");

                }

            }
        );


        /*
         * Close dropdown when pressing ESC.
         */

        document.addEventListener(
            "keydown",
            function (event) {

                if (event.key === "Escape") {

                    profileDropdown.classList.remove(
                        "show"
                    );

                }

            }
        );

    }

});