import sqlite3

DATABASE_NAME = "expenses.db"

def get_connection():
connection = sqlite3.connect(DATABASE_NAME)
connection.row_factory = sqlite3.Row
return connection

def initialize_database():
connection = get_connection()


# Users table
connection.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """
)

# Expenses table
connection.execute(
    """
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL CHECK(amount > 0),
        category TEXT NOT NULL,
        description TEXT,
        expense_date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """
)

connection.commit()
connection.close()
