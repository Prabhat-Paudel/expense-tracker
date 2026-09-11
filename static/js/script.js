document.addEventListener(
"DOMContentLoaded",
function () {

 
    initializeTheme();

    initializeSearch();

    initializeNavigation();

    initializeCharts();

    initializePasswordValidation();

}
 

);

function initializeTheme() {

 
const themeToggle =
    document.getElementById(
        "themeToggle"
    );


const themeIcon =
    document.getElementById(
        "themeIcon"
    );


const themeText =
    document.getElementById(
        "themeText"
    );


const savedTheme =
    localStorage.getItem(
        "expenseTrackerTheme"
    );


if (savedTheme === "dark") {

    document.body.classList.add(
        "dark"
    );

}


updateThemeButton();


if (!themeToggle) {

    return;

}


themeToggle.addEventListener(
    "click",
    function () {

        document.body.classList.toggle(
            "dark"
        );


        const isDark =
            document.body.classList.contains(
                "dark"
            );


        localStorage.setItem(
            "expenseTrackerTheme",
            isDark
                ? "dark"
                : "light"
        );


        updateThemeButton();

    }
);


function updateThemeButton() {

    const isDark =
        document.body.classList.contains(
            "dark"
        );


    if (themeIcon) {

        themeIcon.textContent =
            isDark
                ? "☀️"
                : "🌙";

    }


    if (themeText) {

        themeText.textContent =
            isDark
                ? "Light Mode"
                : "Dark Mode";

    }

}
 

}

function initializeSearch() {

 
const searchInput =
    document.getElementById(
        "searchInput"
    );


const categoryFilter =
    document.getElementById(
        "categoryFilter"
    );


const dateFilter =
    document.getElementById(
        "dateFilter"
    );


const table =
    document.getElementById(
        "expenseTable"
    );


if (
    !searchInput ||
    !categoryFilter ||
    !table
) {

    return;

}


function filterTable() {

    const search =
        searchInput.value
            .toLowerCase()
            .trim();


    const category =
        categoryFilter.value
            .toLowerCase();


    const selectedDate =
        dateFilter
            ? dateFilter.value
            : "";


    const rows =
        table.querySelectorAll(
            "tbody tr"
        );


    rows.forEach(
        function (row) {

            const description =
                (
                    row.dataset.description
                    || ""
                ).toLowerCase();


            const rowCategory =
                (
                    row.dataset.category
                    || ""
                ).toLowerCase();


            const rowDate =
                row.dataset.date
                || "";


            const matchesSearch =
                !search ||
                description.includes(
                    search
                );


            const matchesCategory =
                !category ||
                rowCategory === category;


            const matchesDate =
                !selectedDate ||
                rowDate === selectedDate;


            if (
                matchesSearch &&
                matchesCategory &&
                matchesDate
            ) {

                row.style.display =
                    "";

            } else {

                row.style.display =
                    "none";

            }

        }
    );

}


searchInput.addEventListener(
    "input",
    filterTable
);


categoryFilter.addEventListener(
    "change",
    filterTable
);


if (dateFilter) {

    dateFilter.addEventListener(
        "change",
        filterTable
    );

}
 

}

function initializeNavigation() {

 
const links =
    document.querySelectorAll(
        ".nav-link"
    );


if (!links.length) {

    return;

}


links.forEach(
    function (link) {

        link.addEventListener(
            "click",
            function () {

                links.forEach(
                    function (item) {

                        item.classList.remove(
                            "active"
                        );

                    }
                );


                link.classList.add(
                    "active"
                );

            }
        );

    }
);
 

}

function initializeCharts() {

 
if (
    typeof Chart ===
    "undefined"
) {

    return;

}


createMonthlyChart();

createCategoryChart();
 

}

function createMonthlyChart() {

 
const canvas =
    document.getElementById(
        "monthlyChart"
    );


if (
    !canvas ||
    typeof monthlyData ===
    "undefined"
) {

    return;

}


const labels =
    monthlyData.map(
        function (item) {

            return formatMonth(
                item.month
            );

        }
    );


const values =
    monthlyData.map(
        function (item) {

            return item.total;

        }
    );


new Chart(
    canvas,
    {
        type: "line",

        data: {

            labels: labels,

            datasets: [
                {
                    label:
                        "Monthly Spending",

                    data: values,

                    borderWidth: 3,

                    tension: 0.35,

                    fill: false,

                    pointRadius: 4,

                    pointHoverRadius: 6
                }
            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio:
                false,

            plugins: {

                legend: {
                    display: false
                }

            },

            scales: {

                y: {

                    beginAtZero: true,

                    ticks: {

                        callback:
                            function (value) {

                                return "Rs. "
                                    + value;

                            }

                    }

                }

            }

        }

    }
);
 

}

function createCategoryChart() {

 
const canvas =
    document.getElementById(
        "categoryChart"
    );


if (
    !canvas ||
    typeof categoryData ===
    "undefined" ||
    !categoryData.length
) {

    return;

}


const labels =
    categoryData.map(
        function (item) {

            return item.category;

        }
    );


const values =
    categoryData.map(
        function (item) {

            return item.total;

        }
    );


new Chart(
    canvas,
    {
        type: "doughnut",

        data: {

            labels: labels,

            datasets: [
                {
                    data: values,

                    borderWidth: 2
                }
            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio:
                false,

            plugins: {

                legend: {

                    position: "bottom",

                    labels: {

                        padding: 12,

                        font: {
                            size: 11
                        }

                    }

                }

            }

        }

    }
);
 

}

function formatMonth(
monthString
) {

 
if (
    !monthString ||
    monthString.length !== 7
) {

    return monthString;

}


const parts =
    monthString.split("-");


const year =
    parts[0];


const month =
    parseInt(
        parts[1],
        10
    );


const names = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec"
];


return (
    names[month - 1]
    + " "
    + year
);
 

}

function initializePasswordValidation() {

 
const registerForm =
    document.querySelector(
        'form[action*="register"]'
    );


if (!registerForm) {

    return;

}


registerForm.addEventListener(
    "submit",
    function (event) {

        const password =
            document.getElementById(
                "password"
            );


        const confirmPassword =
            document.getElementById(
                "confirm_password"
            );


        if (
            password &&
            confirmPassword &&
            password.value !==
            confirmPassword.value
        ) {

            event.preventDefault();

            alert(
                "Passwords do not match."
            );

        }

    }
);
 

}
