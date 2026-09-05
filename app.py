from datetime import date
from functools import wraps

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from werkzeug.security import check_password_hash, generate_password_hash

from database import get_connection, initialize_database

from service import (
    add_expense,
    list_expenses,
    get_monthly_summary,
    get_category_summary,
    get_monthly_trend,
    get_average_expense,
    get_highest_expense,
    delete_expense,
)


app = Flask(__name__)

# Change this to a long random value for a real deployment.
app.secret_key = "expenseflow-secret-key-change-this"


# ---------------------------------------------------------
# USER / LOGIN SYSTEM
# ---------------------------------------------------------

def initialize_users():
    """Create users table and default admin account."""

    initialize_database()

    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )

    existing_user = connection.execute(
        """
        SELECT id
        FROM users
        WHERE username = ?
        """,
        ("admin",),
    ).fetchone()

    # Create default account only if it doesn't exist.
    if existing_user is None:

        password_hash = generate_password_hash(
            "admin123"
        )

        connection.execute(
            """
            INSERT INTO users (
                username,
                password
            )
            VALUES (?, ?)
            """,
            (
                "admin",
                password_hash,
            ),
        )

    connection.commit()
    connection.close()


def login_required(function):
    """Protect pages that require login."""

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:

            flash(
                "Please log in to continue.",
                "error",
            )

            return redirect(
                url_for("login")
            )

        return function(*args, **kwargs)

    return wrapper


# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    # Already logged in
    if "user_id" in session:
        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        connection = get_connection()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (username,),
        ).fetchone()

        connection.close()

        if (
            user
            and check_password_hash(
                user["password"],
                password
            )
        ):

            session.clear()

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            flash(
                "Welcome back!",
                "success",
            )

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid username or password.",
            "error",
        )

    return render_template(
        "login.html"
    )


# ---------------------------------------------------------
# LOGOUT
# ---------------------------------------------------------

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success",
    )

    return redirect(
        url_for("login")
    )


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route("/")
@login_required
def dashboard():

    expenses = list_expenses()

    today = date.today()

    total = sum(
        expense["amount"]
        for expense in expenses
    )

    current_month_total, monthly_categories = (
        get_monthly_summary(
            today.year,
            today.month,
        )
    )

    category_summary = get_category_summary()

    monthly_trend = get_monthly_trend(6)

    average_expense = get_average_expense()

    highest_expense = get_highest_expense()

    return render_template(
        "dashboard.html",

        expenses=expenses,

        total=total,

        current_month_total=current_month_total,

        monthly_categories=monthly_categories,

        category_summary=category_summary,

        monthly_trend=monthly_trend,

        average_expense=average_expense,

        highest_expense=highest_expense,

        today=today.isoformat(),

        summary_year=today.year,

        summary_month=today.month,

        username=session.get(
            "username",
            "Admin",
        ),
    )


# ---------------------------------------------------------
# ADD EXPENSE
# ---------------------------------------------------------

@app.route("/add", methods=["POST"])
@login_required
def add():

    try:

        amount = request.form.get(
            "amount",
            "",
        )

        category = request.form.get(
            "category",
            "",
        )

        description = request.form.get(
            "description",
            "",
        )

        expense_date = request.form.get(
            "expense_date",
            "",
        )

        if not expense_date:
            expense_date = date.today().isoformat()

        add_expense(
            amount,
            category,
            description,
            expense_date,
        )

        flash(
            "Expense added successfully!",
            "success",
        )

    except ValueError as error:

        flash(
            str(error),
            "error",
        )

    return redirect(
        url_for("dashboard")
    )


# ---------------------------------------------------------
# DELETE EXPENSE
# ---------------------------------------------------------

@app.route(
    "/delete/<int:expense_id>",
    methods=["POST"],
)
@login_required
def delete(expense_id):

    deleted = delete_expense(
        expense_id
    )

    if deleted:

        flash(
            "Expense deleted successfully.",
            "success",
        )

    else:

        flash(
            "Expense was not found.",
            "error",
        )

    return redirect(
        url_for("dashboard")
    )


# ---------------------------------------------------------
# MONTHLY SUMMARY
# ---------------------------------------------------------

@app.route("/summary")
@login_required
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

            raise ValueError(
                "Month must be between 1 and 12."
            )

        expenses = list_expenses()

        today = date.today()

        total = sum(
            expense["amount"]
            for expense in expenses
        )

        current_month_total, monthly_categories = (
            get_monthly_summary(
                year,
                month,
            )
        )

        return render_template(
            "dashboard.html",

            expenses=expenses,

            total=total,

            current_month_total=current_month_total,

            monthly_categories=monthly_categories,

            category_summary=get_category_summary(),

            monthly_trend=get_monthly_trend(6),

            average_expense=get_average_expense(),

            highest_expense=get_highest_expense(),

            today=today.isoformat(),

            summary_year=year,

            summary_month=month,

            username=session.get(
                "username",
                "Admin",
            ),
        )

    except ValueError as error:

        flash(
            str(error),
            "error",
        )

        return redirect(
            url_for("dashboard")
        )


# ---------------------------------------------------------
# START APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":

    initialize_users()

    app.run(
        debug=True
    )