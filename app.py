from datetime import date, datetime

from flask import Flask, render_template, request, redirect, url_for

from database import initialize_database
from service import (
    add_expense,
    list_expenses,
    get_monthly_summary,
    delete_expense,
)


app = Flask(__name__)


@app.route("/")
def dashboard():
    expenses = list_expenses()

    today = date.today()

    total = sum(
        expense["amount"]
        for expense in expenses
    )

    current_month_total, categories = get_monthly_summary(
        today.year,
        today.month,
    )

    return render_template(
        "dashboard.html",
        expenses=expenses,
        total=total,
        current_month_total=current_month_total,
        categories=categories,
        today=today.isoformat(),
    )


@app.route("/add", methods=["POST"])
def add():
    try:
        amount = request.form.get("amount", "")
        category = request.form.get("category", "")
        description = request.form.get("description", "")
        expense_date = request.form.get("expense_date", "")

        if not expense_date:
            expense_date = date.today().isoformat()

        datetime.strptime(
            expense_date,
            "%Y-%m-%d",
        )

        add_expense(
            amount,
            category,
            description,
            expense_date,
        )

    except ValueError as error:
        return render_template(
            "dashboard.html",
            expenses=list_expenses(),
            total=sum(
                expense["amount"]
                for expense in list_expenses()
            ),
            current_month_total=0,
            categories=[],
            today=date.today().isoformat(),
            error=str(error),
        )

    return redirect(url_for("dashboard"))


@app.route(
    "/delete/<int:expense_id>",
    methods=["POST"],
)
def delete(expense_id):
    delete_expense(expense_id)

    return redirect(url_for("dashboard"))


@app.route("/summary")
def summary():
    try:
        year = int(
            request.args.get(
                "year",
                date.today().year,
            )
        )

        month = int(
            request.args.get(
                "month",
                date.today().month,
            )
        )

        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12.")

        total, categories = get_monthly_summary(
            year,
            month,
        )

        return render_template(
            "dashboard.html",
            expenses=list_expenses(),
            total=sum(
                expense["amount"]
                for expense in list_expenses()
            ),
            current_month_total=total,
            categories=categories,
            summary_year=year,
            summary_month=month,
            today=date.today().isoformat(),
        )

    except ValueError as error:
        return render_template(
            "dashboard.html",
            expenses=list_expenses(),
            total=sum(
                expense["amount"]
                for expense in list_expenses()
            ),
            current_month_total=0,
            categories=[],
            today=date.today().isoformat(),
            error=str(error),
        )


if __name__ == "__main__":
    initialize_database()

    app.run(debug=True)