/* =========================================================
   BANTAYBARANGAY
   REPORTS & ANALYTICS
========================================================= */

"use strict";


/* =========================================================
   GLOBAL VARIABLES
========================================================= */

let complaintsChart = null;
let categoryChart = null;
let resolutionChart = null;
let blockchainChart = null;


/* =========================================================
   CHART DATA
========================================================= */

const complaintData = {

    "12": {
        labels: [
            "JAN",
            "FEB",
            "MAR",
            "APR",
            "MAY",
            "JUN",
            "JUL",
            "AUG",
            "SEP",
            "OCT",
            "NOV"
        ],

        values: [
            42,
            50,
            60,
            69,
            73,
            74,
            81,
            92,
            87,
            71,
            93
        ]
    },


    "6": {
        labels: [
            "JUN",
            "JUL",
            "AUG",
            "SEP",
            "OCT",
            "NOV"
        ],

        values: [
            74,
            81,
            92,
            87,
            71,
            93
        ]
    },


    "3": {
        labels: [
            "SEP",
            "OCT",
            "NOV"
        ],

        values: [
            87,
            71,
            93
        ]
    }

};


/* =========================================================
   DOM READY
========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeReports();

    }
);


/* =========================================================
   INITIALIZE REPORTS
========================================================= */

function initializeReports() {

    initializeExportButtons();

    initializePeriodSelector();

    initializePersonnelButton();


    /*
     * Chart.js is loaded from the CDN in reports.html.
     * Stop chart initialization if the library did not load.
     */

    if (typeof Chart === "undefined") {

        console.error(
            "Chart.js is not available. Reports charts cannot be created."
        );

        return;

    }


    configureChartDefaults();

    initializeComplaintsChart();

    initializeCategoryChart();

    initializeResolutionChart();

    initializeBlockchainChart();

}


/* =========================================================
   CHART DEFAULTS
========================================================= */

function configureChartDefaults() {

    Chart.defaults.font.family =
        "Inter, Arial, Helvetica, sans-serif";

    Chart.defaults.color =
        "#52605c";

}


/* =========================================================
   MONTHLY COMPLAINTS
========================================================= */

function initializeComplaintsChart() {

    const canvas =
        document.getElementById(
            "complaintsChart"
        );


    if (!canvas) {
        return;
    }


    const context =
        canvas.getContext("2d");


    const gradient =
        context.createLinearGradient(
            0,
            0,
            0,
            310
        );


    gradient.addColorStop(
        0,
        "rgba(35, 103, 87, 0.22)"
    );


    gradient.addColorStop(
        1,
        "rgba(35, 103, 87, 0.01)"
    );


    const data =
        complaintData["12"];


    complaintsChart =
        new Chart(
            context,
            {

                type: "line",


                data: {

                    labels:
                        data.labels,

                    datasets: [

                        {

                            label:
                                "Complaints",

                            data:
                                data.values,

                            borderColor:
                                "#0c342b",

                            backgroundColor:
                                gradient,

                            borderWidth:
                                2.5,

                            fill:
                                true,

                            tension:
                                0.42,

                            pointRadius:
                                0,

                            pointHoverRadius:
                                5,

                            pointHoverBorderWidth:
                                2,

                            pointHoverBorderColor:
                                "#ffffff",

                            pointHoverBackgroundColor:
                                "#0c342b"

                        }

                    ]

                },


                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,


                    interaction: {

                        intersect:
                            false,

                        mode:
                            "index"

                    },


                    plugins: {

                        legend: {
                            display: false
                        },


                        tooltip: {

                            backgroundColor:
                                "#0b3028",

                            titleColor:
                                "#ffffff",

                            bodyColor:
                                "#ffffff",

                            padding:
                                11,

                            cornerRadius:
                                8,

                            displayColors:
                                false,


                            callbacks: {

                                label:
                                    function (context) {

                                        return (
                                            context.parsed.y +
                                            " complaints"
                                        );

                                    }

                            }

                        }

                    },


                    scales: {

                        x: {

                            border: {
                                display: false
                            },


                            grid: {

                                display:
                                    true,

                                color:
                                    "rgba(32, 109, 88, 0.055)",

                                lineWidth:
                                    1

                            },


                            ticks: {

                                color:
                                    "#53635e",

                                font: {

                                    size:
                                        9,

                                    weight:
                                        "600"

                                },

                                maxRotation:
                                    0,

                                minRotation:
                                    0

                            }

                        },


                        y: {

                            beginAtZero:
                                true,

                            suggestedMax:
                                110,


                            border: {
                                display: false
                            },


                            grid: {
                                display: false
                            },


                            ticks: {
                                display: false
                            }

                        }

                    }

                }

            }
        );

}


/* =========================================================
   CATEGORY DOUGHNUT
========================================================= */

function initializeCategoryChart() {

    const canvas =
        document.getElementById(
            "categoryChart"
        );


    if (!canvas) {
        return;
    }


    categoryChart =
        new Chart(
            canvas,
            {

                type:
                    "doughnut",


                data: {

                    labels: [
                        "Civil Issues",
                        "Others"
                    ],


                    datasets: [

                        {

                            data: [
                                74,
                                26
                            ],

                            backgroundColor: [
                                "#91b99d",
                                "#dceee0"
                            ],

                            borderWidth:
                                0,

                            hoverOffset:
                                0

                        }

                    ]

                },


                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    cutout:
                        "79%",


                    plugins: {

                        legend: {
                            display: false
                        },


                        tooltip: {

                            callbacks: {

                                label:
                                    function (context) {

                                        return (
                                            context.label +
                                            ": " +
                                            context.parsed +
                                            "%"
                                        );

                                    }

                            }

                        }

                    }

                }

            }
        );

}


/* =========================================================
   RESOLUTION TREND
========================================================= */

function initializeResolutionChart() {

    const canvas =
        document.getElementById(
            "resolutionChart"
        );


    if (!canvas) {
        return;
    }


    resolutionChart =
        new Chart(
            canvas,
            {

                type:
                    "bar",


                data: {

                    labels: [
                        "Week 1",
                        "Week 2",
                        "Week 3",
                        "Week 4"
                    ],


                    datasets: [

                        {

                            label:
                                "Filed",

                            data: [
                                75,
                                90,
                                66,
                                80
                            ],

                            backgroundColor:
                                "#062e26",

                            borderRadius:
                                3,

                            borderSkipped:
                                false,

                            barPercentage:
                                0.72,

                            categoryPercentage:
                                0.72

                        },


                        {

                            label:
                                "Resolved",

                            data: [
                                70,
                                80,
                                66,
                                77
                            ],

                            backgroundColor:
                                "#a5cfc3",

                            borderRadius:
                                3,

                            borderSkipped:
                                false,

                            barPercentage:
                                0.72,

                            categoryPercentage:
                                0.72

                        }

                    ]

                },


                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,


                    interaction: {

                        intersect:
                            false,

                        mode:
                            "index"

                    },


                    plugins: {

                        legend: {
                            display: false
                        },


                        tooltip: {

                            backgroundColor:
                                "#0b3028",

                            padding:
                                10,

                            cornerRadius:
                                8

                        }

                    },


                    scales: {

                        x: {

                            border: {
                                display: false
                            },


                            grid: {
                                display: false
                            },


                            ticks: {

                                color:
                                    "#596963",

                                font: {
                                    size: 9
                                }

                            }

                        },


                        y: {

                            beginAtZero:
                                true,

                            suggestedMax:
                                100,


                            border: {
                                display: false
                            },


                            grid: {
                                display: false
                            },


                            ticks: {
                                display: false
                            }

                        }

                    }

                }

            }
        );

}


/* =========================================================
   BLOCKCHAIN VERIFICATION
========================================================= */

function initializeBlockchainChart() {

    const canvas =
        document.getElementById(
            "blockchainChart"
        );


    if (!canvas) {
        return;
    }


    blockchainChart =
        new Chart(
            canvas,
            {

                type:
                    "doughnut",


                data: {

                    datasets: [

                        {

                            data: [
                                98.2,
                                1.8
                            ],

                            backgroundColor: [
                                "#07392f",
                                "#dceee0"
                            ],

                            borderWidth:
                                0,

                            borderRadius:
                                8,

                            hoverOffset:
                                0

                        }

                    ]

                },


                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    cutout:
                        "86%",

                    rotation:
                        0,

                    circumference:
                        360,


                    plugins: {

                        legend: {
                            display: false
                        },


                        tooltip: {
                            enabled: false
                        }

                    }

                }

            }
        );

}


/* =========================================================
   PERIOD SELECTOR
========================================================= */

function initializePeriodSelector() {

    const selector =
        document.getElementById(
            "complaintPeriod"
        );


    if (!selector) {
        return;
    }


    selector.addEventListener(
        "change",
        function () {

            updateComplaintPeriod(
                this.value
            );

        }
    );

}


/* =========================================================
   UPDATE COMPLAINT PERIOD
========================================================= */

function updateComplaintPeriod(period) {

    if (!complaintsChart) {
        return;
    }


    const selectedData =
        complaintData[period];


    if (!selectedData) {
        return;
    }


    complaintsChart.data.labels =
        selectedData.labels;


    complaintsChart
        .data
        .datasets[0]
        .data =
        selectedData.values;


    complaintsChart.update();

}


/* =========================================================
   EXPORT BUTTONS
========================================================= */

function initializeExportButtons() {

    const pdfButton =
        document.getElementById(
            "exportPdfBtn"
        );


    const excelButton =
        document.getElementById(
            "exportExcelBtn"
        );


    const csvButton =
        document.getElementById(
            "exportCsvBtn"
        );


    if (pdfButton) {

        pdfButton.addEventListener(
            "click",
            function () {

                showExportMessage(
                    "PDF"
                );

            }
        );

    }


    if (excelButton) {

        excelButton.addEventListener(
            "click",
            function () {

                showExportMessage(
                    "Excel"
                );

            }
        );

    }


    if (csvButton) {

        csvButton.addEventListener(
            "click",
            function () {

                exportReportCSV();

            }
        );

    }

}


/* =========================================================
   EXPORT MESSAGE
========================================================= */

function showExportMessage(type) {

    alert(
        type +
        " export is not connected to the Django backend yet."
    );

}


/* =========================================================
   CSV EXPORT
========================================================= */

function exportReportCSV() {

    const data = [

        [
            "Metric",
            "Value"
        ],

        [
            "Monthly Complaints",
            "128"
        ],

        [
            "Incident Reports",
            "45"
        ],

        [
            "Resolution Rate",
            "94%"
        ],

        [
            "Verified Documents",
            "2431"
        ],

        [
            "Officer Performance",
            "4.8/5"
        ]

    ];


    const csvContent =
        data
            .map(
                function (row) {

                    return row
                        .map(
                            escapeCSVValue
                        )
                        .join(",");

                }
            )
            .join("\n");


    const blob =
        new Blob(
            [
                "\uFEFF" +
                csvContent
            ],
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
        "bantaybarangay_reports.csv";


    link.style.display =
        "none";


    document.body.appendChild(
        link
    );


    link.click();


    document.body.removeChild(
        link
    );


    URL.revokeObjectURL(
        url
    );

}


/* =========================================================
   ESCAPE CSV VALUE
========================================================= */

function escapeCSVValue(value) {

    const stringValue =
        String(value);


    if (
        stringValue.includes(",") ||
        stringValue.includes('"') ||
        stringValue.includes("\n")
    ) {

        return (
            '"' +
            stringValue.replace(
                /"/g,
                '""'
            ) +
            '"'
        );

    }


    return stringValue;

}


/* =========================================================
   VIEW PERSONNEL
========================================================= */

function initializePersonnelButton() {

    const button =
        document.getElementById(
            "viewPersonnelBtn"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        function () {

            /*
             * Add the personnel URL here later if you
             * create a dedicated officer/personnel page.
             */

            console.log(
                "View All Personnel clicked."
            );

        }
    );

}