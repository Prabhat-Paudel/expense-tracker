import os
import csv
import io
import sqlite3
from datetime import date, datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "change-this-secret-key-in-production"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "expense_tracker.db")

CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Entertainment",
    "Bills",
    "Education",
    "Health",
    "Other"
]


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            budget REAL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            expense_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


def get_user(user_id):
    conn = get_db()

    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    return user


def get_user_expenses(user_id):
    conn = get_db()

    expenses = conn.execute(
        """
        SELECT *
        FROM expenses
        WHERE user_id = ?
        ORDER BY expense_date DESC, id DESC
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    return expenses


def get_dashboard_data(user_id):
    conn = get_db()

    expenses = conn.execute(
        """
        SELECT *
        FROM expenses
        WHERE user_id = ?
        ORDER BY expense_date DESC, id DESC
        """,
        (user_id,)
    ).fetchall()

    total_row = conn.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    average_row = conn.execute(
        """
        SELECT COALESCE(AVG(amount), 0) AS average
        FROM expenses
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    transaction_row = conn.execute(
        """
        SELECT COUNT(*) AS total
        FROM expenses
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    current_month = date.today().strftime("%Y-%m")

    current_month_row = conn.execute(
        """
        SELECT COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = ?
        AND substr(expense_date, 1, 7) = ?
        """,
        (
            user_id,
            current_month
        )
    ).fetchone()

    category_rows = conn.execute(
        """
        SELECT
            category,
            SUM(amount) AS total
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
        ORDER BY total DESC
        """,
        (user_id,)
    ).fetchall()

    monthly_rows = conn.execute(
        """
        SELECT
            substr(expense_date, 1, 7) AS month,
            SUM(amount) AS total
        FROM expenses
        WHERE user_id = ?
        GROUP BY substr(expense_date, 1, 7)
        ORDER BY month DESC
        LIMIT 6
        """,
        (user_id,)
    ).fetchall()

    highest_expense = conn.execute(
        """
        SELECT *
        FROM expenses
        WHERE user_id = ?
        ORDER BY amount DESC
        LIMIT 1
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    category_summary = []

    for row in category_rows:
        category_summary.append({
            "category": row["category"],
            "total": round(row["total"], 2)
        })

    monthly_trend = []

    for row in reversed(monthly_rows):
        monthly_trend.append({
            "month": row["month"],
            "total": round(row["total"], 2)
        })

    user = get_user(user_id)

    budget = 0

    if user:
        budget = user["budget"] or 0

    budget_progress = 0

    if budget > 0:
        budget_progress = (
            current_month_row["total"] / budget
        ) * 100

        budget_progress = min(
            round(budget_progress, 2),
            100
        )

    budget_remaining = max(
        budget - current_month_row["total"],
        0
    )

    return {
        "expenses": expenses,
        "total": round(total_row["total"], 2),
        "average_expense": round(average_row["average"], 2),
        "transaction_count": transaction_row["total"],
        "current_month_total": round(
            current_month_row["total"],
            2
        ),
        "category_summary": category_summary,
        "monthly_trend": monthly_trend,
        "highest_expense": highest_expense,
        "budget": round(budget, 2),
        "budget_progress": budget_progress,
        "budget_remaining": round(
            budget_remaining,
            2
        )
    }


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not username or not password:
            flash(
                "Username and password are required.",
                "error"
            )
            return render_template("register.html")

        if len(username) < 3:
            flash(
                "Username must contain at least 3 characters.",
                "error"
            )
            return render_template("register.html")

        if len(password) < 6:
            flash(
                "Password must contain at least 6 characters.",
                "error"
            )
            return render_template("register.html")

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "error"
            )
            return render_template("register.html")

        conn = get_db()

        existing_user = conn.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        if existing_user:
            conn.close()

            flash(
                "Username already exists.",
                "error"
            )

            return render_template("register.html")

        hashed_password = generate_password_hash(
            password
        )

        conn.execute(
            """
            INSERT INTO users (
                username,
                password,
                budget,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                hashed_password,
                0,
                datetime.now().isoformat()
            )
        )

        conn.commit()
        conn.close()

        flash(
            "Account created successfully. Please login.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        conn = get_db()

        user = conn.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(
            user["password"],
            password
        ):

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            flash(
                "Welcome back, " + user["username"] + "!",
                "success"
            )

            return redirect(url_for("dashboard"))

        flash(
            "Invalid username or password.",
            "error"
        )

    return render_template("login.html")


@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():

    data = get_dashboard_data(
        session["user_id"]
    )

    return render_template(
        "dashboard.html",
        username=session["username"],
        today=date.today().isoformat(),
        categories=CATEGORIES,
        **data
    )


@app.route("/add", methods=["POST"])
@login_required
def add():

    amount_text = request.form.get(
        "amount",
        ""
    ).strip()

    category = request.form.get(
        "category",
        ""
    ).strip()

    description = request.form.get(
        "description",
        ""
    ).strip()

    expense_date = request.form.get(
        "expense_date",
        ""
    ).strip()

    try:
        amount = float(amount_text)

    except (TypeError, ValueError):

        flash(
            "Please enter a valid amount.",
            "error"
        )

        return redirect(url_for("dashboard"))

    if amount <= 0:

        flash(
            "Amount must be greater than zero.",
            "error"
        )

        return redirect(url_for("dashboard"))

    if category not in CATEGORIES:

        flash(
            "Please select a valid category.",
            "error"
        )

        return redirect(url_for("dashboard"))

    if not expense_date:
        expense_date = date.today().isoformat()

    try:

        datetime.strptime(
            expense_date,
            "%Y-%m-%d"
        )

    except ValueError:

        flash(
            "Invalid date.",
            "error"
        )

        return redirect(url_for("dashboard"))

    if len(description) > 200:

        flash(
            "Description must be 200 characters or less.",
            "error"
        )

        return redirect(url_for("dashboard"))

    conn = get_db()

    conn.execute(
        """
        INSERT INTO expenses (
            user_id,
            amount,
            category,
            description,
            expense_date,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            amount,
            category,
            description,
            expense_date,
            datetime.now().isoformat()
        )
    )

    conn.commit()
    conn.close()

    flash(
        "Expense added successfully.",
        "success"
    )

    return redirect(url_for("dashboard"))


@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
@login_required
def edit_expense(expense_id):

    conn = get_db()

    expense = conn.execute(
        """
        SELECT *
        FROM expenses
        WHERE id = ?
        AND user_id = ?
        """,
        (
            expense_id,
            session["user_id"]
        )
    ).fetchone()

    if not expense:

        conn.close()

        flash(
            "Expense not found.",
            "error"
        )

        return redirect(url_for("dashboard"))

    if request.method == "POST":

        amount_text = request.form.get(
            "amount",
            ""
        ).strip()

        category = request.form.get(
            "category",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        expense_date = request.form.get(
            "expense_date",
            ""
        ).strip()

        try:
            amount = float(amount_text)

        except (TypeError, ValueError):

            conn.close()

            flash(
                "Please enter a valid amount.",
                "error"
            )

            return redirect(
                url_for(
                    "edit_expense",
                    expense_id=expense_id
                )
            )

        if amount <= 0:

            conn.close()

            flash(
                "Amount must be greater than zero.",
                "error"
            )

            return redirect(
                url_for(
                    "edit_expense",
                    expense_id=expense_id
                )
            )

        if category not in CATEGORIES:

            conn.close()

            flash(
                "Invalid category.",
                "error"
            )

            return redirect(
                url_for(
                    "edit_expense",
                    expense_id=expense_id
                )
            )

        try:

            datetime.strptime(
                expense_date,
                "%Y-%m-%d"
            )

        except ValueError:

            conn.close()

            flash(
                "Invalid date.",
                "error"
            )

            return redirect(
                url_for(
                    "edit_expense",
                    expense_id=expense_id
                )
            )

        if len(description) > 200:

            conn.close()

            flash(
                "Description must be 200 characters or less.",
                "error"
            )

            return redirect(
                url_for(
                    "edit_expense",
                    expense_id=expense_id
                )
            )

        conn.execute(
            """
            UPDATE expenses
            SET
                amount = ?,
                category = ?,
                description = ?,
                expense_date = ?
            WHERE id = ?
            AND user_id = ?
            """,
            (
                amount,
                category,
                description,
                expense_date,
                expense_id,
                session["user_id"]
            )
        )

        conn.commit()
        conn.close()

        flash(
            "Expense updated successfully.",
            "success"
        )

        return redirect(url_for("dashboard"))

    conn.close()

    return render_template(
        "edit_expense.html",
        expense=expense,
        categories=CATEGORIES
    )


@app.route("/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete(expense_id):

    conn = get_db()

    expense = conn.execute(
        """
        SELECT id
        FROM expenses
        WHERE id = ?
        AND user_id = ?
        """,
        (
            expense_id,
            session["user_id"]
        )
    ).fetchone()

    if not expense:

        conn.close()

        flash(
            "Expense not found.",
            "error"
        )

        return redirect(url_for("dashboard"))

    conn.execute(
        """
        DELETE FROM expenses
        WHERE id = ?
        AND user_id = ?
        """,
        (
            expense_id,
            session["user_id"]
        )
    )

    conn.commit()
    conn.close()

    flash(
        "Expense deleted successfully.",
        "success"
    )

    return redirect(url_for("dashboard"))


@app.route("/budget", methods=["POST"])
@login_required
def update_budget():

    budget_text = request.form.get(
        "budget",
        "0"
    ).strip()

    try:
        budget = float(budget_text)

    except (TypeError, ValueError):

        flash(
            "Please enter a valid budget.",
            "error"
        )

        return redirect(url_for("dashboard"))

    if budget < 0:

        flash(
            "Budget cannot be negative.",
            "error"
        )

        return redirect(url_for("dashboard"))

    conn = get_db()

    conn.execute(
        """
        UPDATE users
        SET budget = ?
        WHERE id = ?
        """,
        (
            budget,
            session["user_id"]
        )
    )

    conn.commit()
    conn.close()

    flash(
        "Monthly budget updated successfully.",
        "success"
    )

    return redirect(url_for("dashboard"))


@app.route("/export")
@login_required
def export_csv():

    conn = get_db()

    expenses = conn.execute(
        """
        SELECT
            expense_date,
            category,
            description,
            amount
        FROM expenses
        WHERE user_id = ?
        ORDER BY expense_date DESC
        """,
        (
            session["user_id"],
        )
    ).fetchall()

    conn.close()

    output = io.StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Date",
        "Category",
        "Description",
        "Amount"
    ])

    for expense in expenses:

        writer.writerow([
            expense["expense_date"],
            expense["category"],
            expense["description"] or "",
            expense["amount"]
        ])

    filename = (
        "expense_report_"
        + date.today().isoformat()
        + ".csv"
    )

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                f"attachment; filename={filename}"
        }
    )


@app.route("/api/expenses")
@login_required
def api_expenses():

    expenses = get_user_expenses(
        session["user_id"]
    )

    result = []

    for expense in expenses:

        result.append({
            "id": expense["id"],
            "amount": expense["amount"],
            "category": expense["category"],
            "description": expense["description"],
            "expense_date": expense["expense_date"]
        })

    return jsonify(result)


@app.route("/summary")
@login_required
def summary():

    try:

        year = int(
            request.args.get(
                "year",
                date.today().year
            )
        )

        month = int(
            request.args.get(
                "month",
                date.today().month
            )
        )

    except ValueError:

        flash(
            "Invalid year or month.",
            "error"
        )

        return redirect(url_for("dashboard"))

    if month < 1 or month > 12:

        flash(
            "Invalid month.",
            "error"
        )

        return redirect(url_for("dashboard"))

    selected_month = (
        f"{year:04d}-{month:02d}"
    )

    conn = get_db()

    total_row = conn.execute(
        """
        SELECT
            COALESCE(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = ?
        AND substr(expense_date, 1, 7) = ?
        """,
        (
            session["user_id"],
            selected_month
        )
    ).fetchone()

    category_rows = conn.execute(
        """
        SELECT
            category,
            SUM(amount) AS total
        FROM expenses
        WHERE user_id = ?
        AND substr(expense_date, 1, 7) = ?
        GROUP BY category
        ORDER BY total DESC
        """,
        (
            session["user_id"],
            selected_month
        )
    ).fetchall()

    conn.close()

    data = get_dashboard_data(
        session["user_id"]
    )

    data["current_month_total"] = round(
        total_row["total"],
        2
    )

    monthly_categories = []

    for row in category_rows:

        monthly_categories.append({
            "category": row["category"],
            "total": round(
                row["total"],
                2
            )
        })

    return render_template(
        "dashboard.html",
        username=session["username"],
        today=date.today().isoformat(),
        categories=CATEGORIES,
        summary_year=year,
        summary_month=month,
        monthly_categories=monthly_categories,
        **data
    )


if __name__ == "__main__":

    init_db()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )