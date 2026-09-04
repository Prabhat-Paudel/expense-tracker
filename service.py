from datetime import date

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

    category = category.strip()

    if not category:
        raise ValueError("Category cannot be empty.")

    if expense_date is None:
        expense_date = date.today().isoformat()

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
            description.strip(),
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