from service import add_expense


def test_add_expense():

    expense_id = add_expense(
        100,
        "Food",
        "Test expense",
        "2026-08-30",
    )

    assert expense_id > 0