from datetime import date, datetime

from database import get_connection, initialize_database


def add_expense(
    amount,
    category,
    description="",
    expense_date=None,
):
    initialize_database()

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a valid number.")

    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    category = str(category).strip()

    if not category:
        raise ValueError("Category cannot be empty.")

    if expense_date is None:
        expense_date = date.today().isoformat()

    try:
        datetime.strptime(expense_date, "%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must be in YYYY-MM-DD format.")

    connection = get_connection()

    cursor = connection.execute(
        """
        INSERT INTO expenses (
            amount,
            category,
            description,
            expense_date
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            amount,
            category,
            str(description).strip(),
            expense_date,
        ),
    )

    connection.commit()

    expense_id = cursor.lastrowid

    connection.close()

    return expense_id


def list_expenses():
    initialize_database()

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM expenses
        ORDER BY expense_date DESC, id DESC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_monthly_summary(year, month):
    initialize_database()

    date_prefix = f"{year:04d}-{month:02d}%"

    connection = get_connection()

    total = connection.execute(
        """
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE expense_date LIKE ?
        """,
        (date_prefix,),
    ).fetchone()[0]

    categories = connection.execute(
        """
        SELECT
            category,
            SUM(amount) AS total
        FROM expenses
        WHERE expense_date LIKE ?
        GROUP BY category
        ORDER BY total DESC
        """,
        (date_prefix,),
    ).fetchall()

    connection.close()

    return total, [dict(row) for row in categories]


def get_category_summary():
    initialize_database()

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            category,
            SUM(amount) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_monthly_trend(months=6):
    initialize_database()

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT
            substr(expense_date, 1, 7) AS month,
            COALESCE(SUM(amount), 0) AS total
        FROM expenses
        GROUP BY substr(expense_date, 1, 7)
        ORDER BY month DESC
        LIMIT ?
        """,
        (months,),
    ).fetchall()

    connection.close()

    results = [dict(row) for row in rows]

    results.reverse()

    return results


def get_average_expense():
    initialize_database()

    connection = get_connection()

    result = connection.execute(
        """
        SELECT COALESCE(AVG(amount), 0)
        FROM expenses
        """
    ).fetchone()[0]

    connection.close()

    return result


def get_highest_expense():
    initialize_database()

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM expenses
        ORDER BY amount DESC
        LIMIT 1
        """
    ).fetchone()

    connection.close()

    return dict(row) if row else None


def delete_expense(expense_id):
    initialize_database()

    connection = get_connection()

    cursor = connection.execute(
        """
        DELETE FROM expenses
        WHERE id = ?
        """,
        (expense_id,),
    )

    connection.commit()

    deleted = cursor.rowcount > 0

    connection.close()

    return deleted