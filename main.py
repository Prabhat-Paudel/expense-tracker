from datetime import date

from database import initialize_database
from service import (
    add_expense,
    list_expenses,
    get_monthly_summary,
    delete_expense,
)


def add_new_expense():

    print("\n--- Add Expense ---")

    try:

        amount = float(input("Enter amount: "))

        category = input("Enter category: ")

        description = input("Enter description: ")

        expense_date = input(
            "Enter date (YYYY-MM-DD) or press Enter for today: "
        )

        if not expense_date:
            expense_date = date.today().isoformat()

        expense_id = add_expense(
            amount,
            category,
            description,
            expense_date,
        )

        print(f"\nExpense #{expense_id} added successfully!")

    except ValueError as error:

        print(f"\nError: {error}")


def show_expenses():

    print("\n--- All Expenses ---")

    expenses = list_expenses()

    if not expenses:

        print("No expenses found.")

        return

    print("-" * 75)

    print(
        f"{'ID':<5}"
        f"{'Date':<12}"
        f"{'Category':<18}"
        f"{'Amount':>12}  "
        f"Description"
    )

    print("-" * 75)

    for expense in expenses:

        print(
            f"{expense['id']:<5}"
            f"{expense['expense_date']:<12}"
            f"{expense['category']:<18}"
            f"{expense['amount']:>12.2f}  "
            f"{expense['description']}"
        )


def show_monthly_summary():

    print("\n--- Monthly Summary ---")

    try:

        year = int(input("Enter year: "))

        month = int(input("Enter month (1-12): "))

        if month < 1 or month > 12:

            print("Invalid month.")

            return

        total, categories = get_monthly_summary(
            year,
            month,
        )

        print(
            f"\nExpense Summary for "
            f"{year}-{month:02d}"
        )

        print("-" * 40)

        print(f"Total Spending: Rs. {total:.2f}")

        print("\nSpending by Category:")

        if not categories:

            print("No expenses found.")

        else:

            for item in categories:

                print(
                    f"{item['category']}: "
                    f"Rs. {item['total']:.2f}"
                )

    except ValueError:

        print("Please enter valid numbers.")


def remove_expense():

    print("\n--- Delete Expense ---")

    try:

        expense_id = int(
            input("Enter expense ID: ")
        )

        deleted = delete_expense(
            expense_id
        )

        if deleted:

            print(
                "Expense deleted successfully!"
            )

        else:

            print(
                "Expense ID not found."
            )

    except ValueError:

        print("Please enter a valid ID.")


def show_menu():

    print("\n" + "=" * 40)

    print("       EXPENSE TRACKER")

    print("=" * 40)

    print("1. Add Expense")

    print("2. View Expenses")

    print("3. Monthly Summary")

    print("4. Delete Expense")

    print("5. Exit")


def main():

    initialize_database()

    while True:

        show_menu()

        choice = input(
            "\nChoose an option (1-5): "
        )

        if choice == "1":

            add_new_expense()

        elif choice == "2":

            show_expenses()

        elif choice == "3":

            show_monthly_summary()

        elif choice == "4":

            remove_expense()

        elif choice == "5":

            print(
                "\nThank you for using "
                "Expense Tracker!"
            )

            break

        else:

            print(
                "\nInvalid choice. "
                "Please try again."
            )


if __name__ == "__main__":

    main()