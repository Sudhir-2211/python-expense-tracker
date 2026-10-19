"""Automated unit tests for Expense Tracker database and logic."""

import pytest
import os
import tempfile
from src.database import ExpenseDatabase


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = ExpenseDatabase(db_path=path)
    yield db
    if os.path.exists(path):
        os.remove(path)


def test_add_and_get_expense(temp_db):
    exp_id = temp_db.add_expense(
        date="2024-03-15",
        title="Grocery Market",
        amount=54.25,
        category="Shopping & Groceries",
        payment_method="Credit Card",
        notes="Weekly grocery run",
    )
    assert exp_id > 0

    record = temp_db.get_expense(exp_id)
    assert record is not None
    assert record.id == exp_id
    assert record.date == "2024-03-15"
    assert record.title == "Grocery Market"
    assert record.amount == 54.25
    assert record.category == "Shopping & Groceries"
    assert record.notes == "Weekly grocery run"


def test_invalid_date(temp_db):
    with pytest.raises(ValueError, match="Invalid date format"):
        temp_db.add_expense(
            date="15-03-2024",
            title="Coffee",
            amount=5.0,
            category="Food & Dining",
        )


def test_invalid_amount(temp_db):
    with pytest.raises(ValueError, match="greater than zero"):
        temp_db.add_expense(
            date="2024-03-15",
            title="Free snack",
            amount=0.0,
            category="Food & Dining",
        )

    with pytest.raises(ValueError, match="greater than zero"):
        temp_db.add_expense(
            date="2024-03-15",
            title="Negative refund",
            amount=-20.0,
            category="Food & Dining",
        )


def test_empty_title(temp_db):
    with pytest.raises(ValueError, match="cannot be empty"):
        temp_db.add_expense(
            date="2024-03-15",
            title="   ",
            amount=10.0,
            category="Food & Dining",
        )


def test_update_expense(temp_db):
    exp_id = temp_db.add_expense(
        date="2024-03-15",
        title="Lunch",
        amount=15.0,
        category="Food & Dining",
    )
    updated = temp_db.update_expense(
        expense_id=exp_id,
        date="2024-03-16",
        title="Lunch with team",
        amount=25.50,
        category="Food & Dining",
        payment_method="Cash",
        notes="Split with Alex",
    )
    assert updated is True

    record = temp_db.get_expense(exp_id)
    assert record.date == "2024-03-16"
    assert record.title == "Lunch with team"
    assert record.amount == 25.50
    assert record.payment_method == "Cash"


def test_delete_expense(temp_db):
    exp_id = temp_db.add_expense(
        date="2024-03-15",
        title="Item to Delete",
        amount=10.0,
        category="Personal & Miscellaneous",
    )
    assert temp_db.delete_expense(exp_id) is True
    assert temp_db.get_expense(exp_id) is None
    # Deleting non-existent returns False
    assert temp_db.delete_expense(9999) is False


def test_list_and_filters(temp_db):
    temp_db.add_expense("2024-01-10", "Books", 30.0, "Education & Career")
    temp_db.add_expense("2024-02-15", "Subway", 45.0, "Transportation")
    temp_db.add_expense("2024-03-20", "Cinema", 20.0, "Entertainment & Leisure")

    # Date filter
    feb_expenses = temp_db.list_expenses(start_date="2024-02-01", end_date="2024-02-28")
    assert len(feb_expenses) == 1
    assert feb_expenses[0].title == "Subway"

    # Category filter
    edu_expenses = temp_db.list_expenses(category="Education & Career")
    assert len(edu_expenses) == 1
    assert edu_expenses[0].title == "Books"

    # Search filter
    search_res = temp_db.list_expenses(search_query="ine")
    assert len(search_res) == 1
    assert search_res[0].title == "Cinema"


def test_summary_and_breakdown(temp_db):
    temp_db.add_expense("2024-01-05", "Grocery 1", 100.0, "Shopping & Groceries")
    temp_db.add_expense("2024-01-10", "Grocery 2", 150.0, "Shopping & Groceries")
    temp_db.add_expense("2024-01-15", "Dinner", 50.0, "Food & Dining")

    summary = temp_db.get_summary()
    assert summary.total_spent == 300.0
    assert summary.transaction_count == 3
    assert summary.avg_transaction == 100.0
    assert summary.top_category == "Shopping & Groceries"
    assert summary.top_category_amount == 250.0

    df_cats = temp_db.get_category_breakdown()
    assert len(df_cats) == 2
    assert df_cats.iloc[0]["category"] == "Shopping & Groceries"
    assert df_cats.iloc[0]["total_spent"] == 250.0


def test_empty_summary(temp_db):
    summary = temp_db.get_summary()
    assert summary.total_spent == 0.0
    assert summary.transaction_count == 0
    assert summary.top_category == "None"
