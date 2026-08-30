import sqlite3
from pathlib import Path


DATABASE_NAME = "expenses.db"


def get_connection():
    """Create a connection to the SQLite database."""

    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create the expenses table."""

    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL CHECK(amount > 0),
            category TEXT NOT NULL,
            description TEXT,
            expense_date TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()