/* =========================================================
   BANTAYBARANGAY
   DASHBOARD
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeDashboardBars();
        initializeDashboardDonut();

    }
);


/* =========================================================
   MONTHLY COMPLAINT BARS
========================================================= */

function initializeDashboardBars() {

    const bars =
        document.querySelectorAll(
            ".bar[data-height]"
        );


    bars.forEach(function (bar) {

        let height =
            parseFloat(
                bar.dataset.height
            );


        if (Number.isNaN(height)) {

            height = 0;

        }


        height = Math.max(
            0,
            Math.min(
                100,
                height
            )
        );


        bar.style.height =
            height + "%";

    });

}


/* =========================================================
   COMPLAINT CATEGORY DONUT
========================================================= */

function initializeDashboardDonut() {

    const donut =
        document.querySelector(
            ".donut-chart.has-data"
        );


    if (!donut) {

        return;

    }


    const percentages = [

        getPercentage(
            donut.dataset.categoryOne
        ),

        getPercentage(
            donut.dataset.categoryTwo
        ),

        getPercentage(
            donut.dataset.categoryThree
        ),

        getPercentage(
            donut.dataset.categoryFour
        )

    ];


    const colors = [
        "#8eb89f",
        "#183f38",
        "#54776c",
        "#16bd88"
    ];


    let currentDegree = 0;

    const segments = [];


    percentages.forEach(
        function (percentage, index) {

            if (percentage <= 0) {

                return;

            }


            const segmentDegree =
                percentage * 3.6;


            const startDegree =
                currentDegree;


            const endDegree =
                currentDegree +
                segmentDegree;


            segments.push(
                colors[index] +
                " " +
                startDegree +
                "deg " +
                endDegree +
                "deg"
            );


            currentDegree =
                endDegree;

        }
    );


    /*
     * The dashboard displays only the top
     * four categories.
     *
     * If those categories do not total 100%,
     * the remaining part uses the neutral
     * background color.
     */

    if (currentDegree < 360) {

        segments.push(
            "#e8eeee " +
            currentDegree +
            "deg 360deg"
        );

    }


    if (segments.length === 0) {

        donut.classList.remove(
            "has-data"
        );

        donut.classList.add(
            "no-data"
        );

        return;

    }


    donut.style.background =
        "conic-gradient(" +
        segments.join(", ") +
        ")";

}


/* =========================================================
   SAFE PERCENTAGE
========================================================= */

function getPercentage(value) {

    let percentage =
        parseFloat(value);


    if (Number.isNaN(percentage)) {

        percentage = 0;

    }


    return Math.max(
        0,
        Math.min(
            100,
            percentage
        )
    );

}