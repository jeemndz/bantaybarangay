/* =========================================================
   BANTAYBARANGAY
   REPORTS & ANALYTICS
========================================================= */

"use strict";


/* =========================================================
   GLOBAL CHARTS
========================================================= */

let complaintsChart = null;
let categoryChart = null;
let resolutionChart = null;
let blockchainChart = null;


/* =========================================================
   DJANGO DATA
========================================================= */

const complaintLabels =
    getJsonData(
        "complaint-chart-labels",
        []
    );

const complaintValues =
    getJsonData(
        "complaint-chart-values",
        []
    );

const categoryLabels =
    getJsonData(
        "category-chart-labels",
        []
    );

const categoryValues =
    getJsonData(
        "category-chart-values",
        []
    );

const resolutionLabels =
    getJsonData(
        "resolution-labels",
        []
    );

const resolutionFiled =
    getJsonData(
        "resolution-filed",
        []
    );

const resolutionResolved =
    getJsonData(
        "resolution-resolved",
        []
    );

const blockchainRate =
    Number(
        getJsonData(
            "blockchain-rate",
            0
        )
    ) || 0;


const reportMonthlyComplaints =
    Number(
        getJsonData(
            "report-monthly-complaints",
            0
        )
    ) || 0;

const reportIncidentReports =
    Number(
        getJsonData(
            "report-incident-reports",
            0
        )
    ) || 0;

const reportResolutionRate =
    Number(
        getJsonData(
            "report-resolution-rate",
            0
        )
    ) || 0;

const reportVerifiedDocuments =
    Number(
        getJsonData(
            "report-verified-documents",
            0
        )
    ) || 0;

const reportResolvedComplaints =
    Number(
        getJsonData(
            "report-resolved-complaints",
            0
        )
    ) || 0;


/* =========================================================
   READ DJANGO JSON
========================================================= */

function getJsonData(id, fallback) {

    const element =
        document.getElementById(id);

    if (!element) {
        return fallback;
    }

    try {

        return JSON.parse(
            element.textContent
        );

    } catch (error) {

        console.error(
            "Unable to read report data:",
            id,
            error
        );

        return fallback;
    }
}


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
   INITIALIZE
========================================================= */

function initializeReports() {

    initializeExportButtons();
    initializePeriodSelector();
    initializePersonnelButton();

    // Apply database percentages to incident progress bars
    initializeProgressBars();

    if (typeof Chart === "undefined") {

        console.error(
            "Chart.js is not available."
        );

        return;
    }

    configureChartDefaults();

    initializeComplaintsChart();
    initializeCategoryChart();
    initializeResolutionChart();
    initializeBlockchainChart();
}
function initializeProgressBars() {

    const progressBars =
        document.querySelectorAll(
            ".incident-progress-fill[data-progress]"
        );

    progressBars.forEach(
        function (bar) {

            let progress =
                parseFloat(
                    bar.dataset.progress
                );

            if (Number.isNaN(progress)) {
                progress = 0;
            }

            progress =
                Math.max(
                    0,
                    Math.min(
                        100,
                        progress
                    )
                );

            bar.style.width =
                progress + "%";
        }
    );
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
   COMPLAINT PERIOD DATA
========================================================= */

function getComplaintPeriodData(period) {

    const numberOfMonths =
        parseInt(
            period,
            10
        );

    if (
        Number.isNaN(numberOfMonths) ||
        numberOfMonths <= 0
    ) {

        return {
            labels: complaintLabels,
            values: complaintValues
        };
    }

    return {

        labels:
            complaintLabels.slice(
                -numberOfMonths
            ),

        values:
            complaintValues.slice(
                -numberOfMonths
            )

    };
}


/* =========================================================
   MONTHLY COMPLAINTS CHART
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
        getComplaintPeriodData("12");

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
                        intersect: false,
                        mode: "index"
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
                                display: true,
                                color:
                                    "rgba(32, 109, 88, 0.055)"
                            },

                            ticks: {

                                color:
                                    "#53635e",

                                font: {
                                    size: 9,
                                    weight: "600"
                                },

                                maxRotation: 0,
                                minRotation: 0
                            }
                        },

                        y: {

                            beginAtZero:
                                true,

                            border: {
                                display: false
                            },

                            grid: {
                                display: false
                            },

                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            }
        );
}


/* =========================================================
   CATEGORY CHART
========================================================= */

function initializeCategoryChart() {

    const canvas =
        document.getElementById(
            "categoryChart"
        );

    if (!canvas) {
        return;
    }

    let labels =
        categoryLabels;

    let values =
        categoryValues;

    if (!values.length) {

        labels = [
            "No Data"
        ];

        values = [
            1
        ];
    }

    const colors = [
        "#91b99d",
        "#0c342b",
        "#52786d",
        "#16a77a",
        "#b8d3c2",
        "#dceee0",
        "#789b8c",
        "#aec7ba"
    ];

    categoryChart =
        new Chart(
            canvas,
            {
                type:
                    "doughnut",

                data: {

                    labels:
                        labels,

                    datasets: [
                        {
                            data:
                                values,

                            backgroundColor:
                                values.length === 1 &&
                                labels[0] === "No Data"
                                    ? ["#e6eeeb"]
                                    : colors,

                            borderWidth:
                                0,

                            hoverOffset:
                                3
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

                                        if (
                                            context.label ===
                                            "No Data"
                                        ) {
                                            return "No complaint data";
                                        }

                                        const total =
                                            context.dataset.data.reduce(
                                                function (sum, value) {
                                                    return sum + Number(value);
                                                },
                                                0
                                            );

                                        const value =
                                            Number(
                                                context.raw
                                            );

                                        const percentage =
                                            total
                                                ? (
                                                    value /
                                                    total *
                                                    100
                                                ).toFixed(1)
                                                : 0;

                                        return (
                                            context.label +
                                            ": " +
                                            value +
                                            " (" +
                                            percentage +
                                            "%)"
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
   RESOLUTION CHART
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

                    labels:
                        resolutionLabels,

                    datasets: [

                        {
                            label:
                                "Filed",

                            data:
                                resolutionFiled,

                            backgroundColor:
                                "#062e26",

                            borderRadius:
                                3,

                            borderSkipped:
                                false
                        },

                        {
                            label:
                                "Resolved",

                            data:
                                resolutionResolved,

                            backgroundColor:
                                "#a5cfc3",

                            borderRadius:
                                3,

                            borderSkipped:
                                false
                        }
                    ]
                },

                options: {

                    responsive:
                        true,

                    maintainAspectRatio:
                        false,

                    interaction: {
                        intersect: false,
                        mode: "index"
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

                            border: {
                                display: false
                            },

                            grid: {
                                display: false
                            },

                            ticks: {
                                precision: 0
                            }
                        }
                    }
                }
            }
        );
}


/* =========================================================
   BLOCKCHAIN CHART
========================================================= */

function initializeBlockchainChart() {

    const canvas =
        document.getElementById(
            "blockchainChart"
        );

    if (!canvas) {
        return;
    }

    const safeRate =
        Math.max(
            0,
            Math.min(
                100,
                blockchainRate
            )
        );

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
                                safeRate,
                                100 - safeRate
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
        getComplaintPeriodData(
            period
        );

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

    const csvButton =
        document.getElementById(
            "exportCsvBtn"
        );


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
   REPORT EXPORT DATA
========================================================= */

function getReportExportData() {

    return [
        [
            "Metric",
            "Value"
        ],

        [
            "Monthly Complaints",
            reportMonthlyComplaints
        ],

        [
            "Incident Reports",
            reportIncidentReports
        ],

        [
            "Resolution Rate",
            reportResolutionRate + "%"
        ],

        [
            "Released Documents",
            reportVerifiedDocuments
        ],

        [
            "Resolved Cases",
            reportResolvedComplaints
        ],

        [
            "Blockchain Registration Rate",
            blockchainRate + "%"
        ]
    ];
}


/* =========================================================
   CSV EXPORT
========================================================= */

function exportReportCSV() {

    const data =
        getReportExportData();

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

    downloadTextFile(
        "\uFEFF" + csvContent,
        "bantaybarangay_reports.csv",
        "text/csv;charset=utf-8;"
    );
}


/* =========================================================
   EXCEL-COMPATIBLE EXPORT
========================================================= */

function exportReportExcel() {

    const data =
        getReportExportData();

    const rows =
        data
            .map(
                function (row) {

                    return (
                        "<tr>" +
                        row
                            .map(
                                function (value) {

                                    return (
                                        "<td>" +
                                        escapeHTML(value) +
                                        "</td>"
                                    );
                                }
                            )
                            .join("") +
                        "</tr>"
                    );
                }
            )
            .join("");

    const content =
        `
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            <table>
                ${rows}
            </table>
        </body>
        </html>
        `;

    downloadTextFile(
        "\uFEFF" + content,
        "bantaybarangay_reports.xls",
        "application/vnd.ms-excel;charset=utf-8;"
    );
}


/* =========================================================
   DOWNLOAD TEXT FILE
========================================================= */

function downloadTextFile(
    content,
    filename,
    type
) {

    const blob =
        new Blob(
            [content],
            {
                type: type
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
        filename;

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
   ESCAPE CSV
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
   ESCAPE HTML
========================================================= */

function escapeHTML(value) {

    return String(value)
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
}


/* =========================================================
   PERSONNEL BUTTON
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

            console.log(
                "Personnel page is not connected yet."
            );

        }
    );
}