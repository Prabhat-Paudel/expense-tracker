from datetime import date, datetime

from database import get_connection, initialize_database

def add_expense(
user_id,
amount,
category,
description="",
expense_date=None
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
        user_id,
        amount,
        category,
        description,
        expense_date
    )
    VALUES (?, ?, ?, ?, ?)
    """,
    (
        user_id,
        amount,
        category,
        str(description).strip(),
        expense_date
    )
)

connection.commit()

expense_id = cursor.lastrowid

connection.close()

return expense_id

def list_expenses(user_id):
initialize_database()

connection = get_connection()

rows = connection.execute(
    """
    SELECT *
    FROM expenses
    WHERE user_id = ?
    ORDER BY expense_date DESC, id DESC
    """,
    (user_id,)
).fetchall()

connection.close()

return [dict(row) for row in rows]

def get_expense(user_id, expense_id):
initialize_database()

connection = get_connection()

row = connection.execute(
    """
    SELECT *
    FROM expenses
    WHERE id = ?
    AND user_id = ?
    """,
    (
        expense_id,
        user_id
    )
).fetchone()

connection.close()

if row:
    return dict(row)

return None


def update_expense(
user_id,
expense_id,
amount,
category,
description,
expense_date
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

try:
    datetime.strptime(
        expense_date,
        "%Y-%m-%d"
    )
except ValueError:
    raise ValueError(
        "Date must be in YYYY-MM-DD format."
    )

connection = get_connection()

cursor = connection.execute(
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
        str(description).strip(),
        expense_date,
        expense_id,
        user_id
    )
)

connection.commit()

updated = cursor.rowcount > 0

connection.close()

return updated


def delete_expense(user_id, expense_id):
initialize_database()


connection = get_connection()

cursor = connection.execute(
    """
    DELETE FROM expenses
    WHERE id = ?
    AND user_id = ?
    """,
    (
        expense_id,
        user_id
    )
)

connection.commit()

deleted = cursor.rowcount > 0

connection.close()

return deleted


def get_monthly_summary(user_id, year, month):
initialize_database()

date_prefix = f"{year:04d}-{month:02d}%"

connection = get_connection()

total = connection.execute(
    """
    SELECT COALESCE(SUM(amount), 0)
    FROM expenses
    WHERE user_id = ?
    AND expense_date LIKE ?
    """,
    (
        user_id,
        date_prefix
    )
).fetchone()[0]

categories = connection.execute(
    """
    SELECT
        category,
        SUM(amount) AS total
    FROM expenses
    WHERE user_id = ?
    AND expense_date LIKE ?
    GROUP BY category
    ORDER BY total DESC
    """,
    (
        user_id,
        date_prefix
    )
).fetchall()

connection.close()

return total, [dict(row) for row in categories]


def get_category_summary(user_id):
initialize_database()


connection = get_connection()

rows = connection.execute(
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

connection.close()

return [dict(row) for row in rows]


def get_monthly_trend(user_id, months=6):
initialize_database()


connection = get_connection()

rows = connection.execute(
    """
    SELECT
        substr(expense_date, 1, 7) AS month,
        COALESCE(SUM(amount), 0) AS total
    FROM expenses
    WHERE user_id = ?
    GROUP BY substr(expense_date, 1, 7)
    ORDER BY month DESC
    LIMIT ?
    """,
    (
        user_id,
        months
    )
).fetchall()

connection.close()

results = [dict(row) for row in rows]

results.reverse()

return results


def get_average_expense(user_id):
initialize_database()


connection = get_connection()

result = connection.execute(
    """
    SELECT COALESCE(AVG(amount), 0)
    FROM expenses
    WHERE user_id = ?
    """,
    (user_id,)
).fetchone()[0]

connection.close()

return result


def get_highest_expense(user_id):
initialize_database()


connection = get_connection()

row = connection.execute(
    """
    SELECT *
    FROM expenses
    WHERE user_id = ?
    ORDER BY amount DESC
    LIMIT 1
    """,
    (user_id,)
).fetchone()

connection.close()

if row:
    return dict(row)

return None

