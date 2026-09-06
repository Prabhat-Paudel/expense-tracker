
import sqlite3


DATABASE_NAME = "expenses.db"


def get_connection():
    """Create a connection to the SQLite database."""

    connection = sqlite3.connect(DATABASE_NAME)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """Create the application database tables."""

    connection = get_connection()

    # Expenses belong to a specific user.
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            amount REAL NOT NULL CHECK(amount > 0),

            category TEXT NOT NULL,

            description TEXT,

            expense_date TEXT NOT NULL,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
        )
        """
    )

    # Users table.
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL
        )
        """
    )

    connection.commit()

    connection.close()

