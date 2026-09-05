document.addEventListener(
    "DOMContentLoaded",
    function () {

        /* =========================
           DARK MODE
        ========================= */

        const themeToggle =
            document.getElementById(
                "themeToggle"
            );

        const themeIcon =
            document.getElementById(
                "themeIcon"
            );

        const savedTheme =
            localStorage.getItem(
                "expenseTheme"
            );

        if (savedTheme === "dark") {

            document.body.classList.add(
                "dark"
            );

            themeIcon.textContent = "☀️";
        }


        if (themeToggle) {

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
                        "expenseTheme",
                        isDark
                            ? "dark"
                            : "light"
                    );

                    themeIcon.textContent =
                        isDark
                            ? "☀️"
                            : "🌙";

                }
            );

        }


        /* =========================
           SEARCH
        ========================= */

        const searchInput =
            document.getElementById(
                "searchInput"
            );

        const categoryFilter =
            document.getElementById(
                "categoryFilter"
            );

        const table =
            document.getElementById(
                "expenseTable"
            );


        function filterTransactions() {

            if (!table) {
                return;
            }

            const searchText =
                searchInput
                    ? searchInput.value
                        .toLowerCase()
                        .trim()
                    : "";

            const selectedCategory =
                categoryFilter
                    ? categoryFilter.value
                    : "";

            const rows =
                table.querySelectorAll(
                    "tbody tr"
                );

            rows.forEach(
                function (row) {

                    const rowText =
                        row.textContent
                            .toLowerCase();

                    const categoryElement =
                        row.querySelector(
                            ".category-badge"
                        );

                    const rowCategory =
                        categoryElement
                            ? categoryElement.textContent.trim()
                            : "";

                    const matchesSearch =
                        rowText.includes(
                            searchText
                        );

                    const matchesCategory =
                        !selectedCategory ||
                        rowCategory ===
                        selectedCategory;

                    row.style.display =
                        matchesSearch &&
                        matchesCategory
                            ? ""
                            : "none";

                }
            );
        }


        if (searchInput) {

            searchInput.addEventListener(
                "input",
                filterTransactions
            );

        }


        if (categoryFilter) {

            categoryFilter.addEventListener(
                "change",
                filterTransactions
            );

        }


        /* =========================
           FORM VALIDATION
        ========================= */

        const expenseForm =
            document.querySelector(
                ".expense-form"
            );

        if (expenseForm) {

            expenseForm.addEventListener(
                "submit",
                function (event) {

                    const amount =
                        document.getElementById(
                            "amount"
                        ).value;

                    const category =
                        document.getElementById(
                            "category"
                        ).value;

                    if (
                        !amount ||
                        Number(amount) <= 0
                    ) {

                        event.preventDefault();

                        alert(
                            "Please enter a valid amount."
                        );

                        return;
                    }

                    if (!category) {

                        event.preventDefault();

                        alert(
                            "Please select a category."
                        );

                    }

                }
            );

        }


        /* =========================
           SMOOTH NAVIGATION
        ========================= */

        document
            .querySelectorAll(
                '.nav-link[href^="#"]'
            )
            .forEach(
                function (link) {

                    link.addEventListener(
                        "click",
                        function (event) {

                            const targetId =
                                this.getAttribute(
                                    "href"
                                );

                            const target =
                                document.querySelector(
                                    targetId
                                );

                            if (target) {

                                event.preventDefault();

                                target.scrollIntoView(
                                    {
                                        behavior: "smooth"
                                    }
                                );

                            }

                        }
                    );

                }
            );


        /* =========================
           MONTHLY CHART
        ========================= */

        const monthlyCanvas =
            document.getElementById(
                "monthlyChart"
            );


        if (
            monthlyCanvas &&
            typeof Chart !== "undefined"
        ) {

            const labels =
                monthlyData.map(
                    function (item) {

                        return item.month;

                    }
                );

            const values =
                monthlyData.map(
                    function (item) {

                        return item.total;

                    }
                );


            new Chart(
                monthlyCanvas,
                {
                    type: "line",

                    data: {

                        labels: labels,

                        datasets: [
                            {
                                label:
                                    "Spending",

                                data: values,

                                borderColor:
                                    "#2563eb",

                                backgroundColor:
                                    "rgba(37, 99, 235, 0.10)",

                                borderWidth: 3,

                                fill: true,

                                tension: 0.4,

                                pointRadius: 4,

                                pointHoverRadius: 6
                            }
                        ]
                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        plugins: {

                            legend: {
                                display: false
                            }

                        },

                        scales: {

                            x: {
                                grid: {
                                    display: false
                                }
                            },

                            y: {

                                beginAtZero: true,

                                grid: {
                                    color:
                                        "rgba(148, 163, 184, 0.15)"
                                },

                                ticks: {

                                    callback:
                                        function (
                                            value
                                        ) {

                                            return "Rs. " +
                                                value;

                                        }

                                }

                            }

                        }
                    }
                }
            );

        }


        /* =========================
           CATEGORY CHART
        ========================= */

        const categoryCanvas =
            document.getElementById(
                "categoryChart"
            );


        if (
            categoryCanvas &&
            typeof Chart !== "undefined"
        ) {

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
                categoryCanvas,
                {
                    type: "doughnut",

                    data: {

                        labels: labels,

                        datasets: [
                            {
                                data: values,

                                backgroundColor: [
                                    "#2563eb",
                                    "#7c3aed",
                                    "#16a34a",
                                    "#ea580c",
                                    "#db2777",
                                    "#0891b2",
                                    "#dc2626",
                                    "#64748b"
                                ],

                                borderWidth: 0,

                                hoverOffset: 8
                            }
                        ]
                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false,

                        cutout: "68%",

                        plugins: {

                            legend: {

                                position: "bottom",

                                labels: {

                                    usePointStyle: true,

                                    padding: 15,

                                    font: {
                                        size: 10
                                    }

                                }

                            }

                        }
                    }
                }
            );

        }


        /* =========================
           AUTO HIDE NOTIFICATIONS
        ========================= */

        setTimeout(
            function () {

                document
                    .querySelectorAll(
                        ".notification"
                    )
                    .forEach(
                        function (notification) {

                            notification.style.opacity =
                                "0";

                            notification.style.transform =
                                "translateY(-5px)";

                            notification.style.transition =
                                "0.4s";

                            setTimeout(
                                function () {

                                    notification.remove();

                                },
                                400
                            );

                        }
                    );

            },
            4000
        );

    }
);