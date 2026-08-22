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



    /* =====================================================
       NUMBER COUNTING EFFECT
    ===================================================== */

    const counters = document.querySelectorAll(".counter");

    const counterObserver = new IntersectionObserver(
        function (entries) {

            entries.forEach(function (entry) {

                if (!entry.isIntersecting) {
                    return;
                }


                const counter = entry.target;

                const target =
                    parseFloat(counter.dataset.target);


                const isDecimal =
                    counter.dataset.decimal === "true";


                const duration = 1800;

                const startTime = performance.now();


                function updateCounter(currentTime) {

                    const elapsed =
                        currentTime - startTime;


                    const progress =
                        Math.min(elapsed / duration, 1);


                    /*
                     * Ease-out animation
                     * Makes the number slow down
                     * near the final value.
                     */

                    const easeOut =
                        1 - Math.pow(1 - progress, 3);


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

});