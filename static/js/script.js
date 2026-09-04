document.addEventListener(
    "DOMContentLoaded",
    function () {

        const expenseForm =
            document.querySelector(".expense-form");


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
                        parseFloat(amount) <= 0
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

                        return;
                    }

                }
            );

        }


        /*
         * Smooth scrolling
         */

        document
            .querySelectorAll(
                '.sidebar a[href^="#"]'
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

                            if (
                                targetId === "#"
                            ) {
                                return;
                            }

                            const target =
                                document.querySelector(
                                    targetId
                                );

                            if (target) {

                                event.preventDefault();

                                target.scrollIntoView({
                                    behavior: "smooth"
                                });

                            }

                        }
                    );

                }
            );

    }
);