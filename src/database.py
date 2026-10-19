"""SQLite Database Management Layer for Expense Tracker.

Author: Sudhir Kumar (GitHub: Sudhir-2211)
"""

import sqlite3
import re
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple, Generator
import pandas as pd
from .models import Expense, ExpenseSummary, CATEGORIES, PAYMENT_METHODS


class ExpenseDatabase:
    """Manages persistent SQLite storage and analytical queries for expenses."""

    def __init__(self, db_path: str = "expenses.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Provides a managed SQLite connection that closes automatically."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Initializes database schema and indices."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    title TEXT NOT NULL,
                    amount REAL NOT NULL CHECK (amount > 0),
                    category TEXT NOT NULL,
                    payment_method TEXT NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);")
            conn.commit()

    @staticmethod
    def validate_date(date_str: str) -> bool:
        """Validates that date string is in YYYY-MM-DD format."""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except (ValueError, TypeError):
            return False

    def add_expense(
        self,
        date: str,
        title: str,
        amount: float,
        category: str,
        payment_method: str = "Credit Card",
        notes: str = "",
    ) -> int:
        """Adds a new expense record with input validation."""
        if not self.validate_date(date):
            raise ValueError(f"Invalid date format '{date}'. Expected YYYY-MM-DD.")

        title = str(title).strip()
        if not title:
            raise ValueError("Expense title cannot be empty.")

        try:
            amount = float(amount)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid amount '{amount}'. Must be a numeric value.")

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if category not in CATEGORIES:
            category = category.strip() if category and category.strip() else "Personal & Miscellaneous"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO expenses (date, title, amount, category, payment_method, notes)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (date, title, amount, category, payment_method, notes),
            )
            conn.commit()
            return cursor.lastrowid

    def get_expense(self, expense_id: int) -> Optional[Expense]:
        """Retrieves an expense by its primary key ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses WHERE id = ?;", (expense_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return Expense(
                id=row["id"],
                date=row["date"],
                title=row["title"],
                amount=row["amount"],
                category=row["category"],
                payment_method=row["payment_method"],
                notes=row["notes"],
                created_at=row["created_at"],
            )

    def update_expense(
        self,
        expense_id: int,
        date: str,
        title: str,
        amount: float,
        category: str,
        payment_method: str,
        notes: str = "",
    ) -> bool:
        """Updates an existing expense record."""
        if not self.validate_date(date):
            raise ValueError(f"Invalid date format '{date}'. Expected YYYY-MM-DD.")

        title = str(title).strip()
        if not title:
            raise ValueError("Expense title cannot be empty.")

        amount = float(amount)
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE expenses
                SET date = ?, title = ?, amount = ?, category = ?, payment_method = ?, notes = ?
                WHERE id = ?;
                """,
                (date, title, amount, category, payment_method, notes, expense_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_expense(self, expense_id: int) -> bool:
        """Deletes an expense record by its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?;", (expense_id,))
            conn.commit()
            return cursor.rowcount > 0

    def list_expenses(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Expense]:
        """Queries expenses with optional date range, category, and search filters."""
        query = "SELECT * FROM expenses WHERE 1=1"
        params: List[Any] = []

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if category and category != "All":
            query += " AND category = ?"
            params.append(category)
        if search_query:
            query += " AND (title LIKE ? OR notes LIKE ?)"
            term = f"%{search_query.strip()}%"
            params.extend([term, term])

        query += " ORDER BY date DESC, id DESC"

        if limit and limit > 0:
            query += " LIMIT ?"
            params.append(limit)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [
                Expense(
                    id=r["id"],
                    date=r["date"],
                    title=r["title"],
                    amount=r["amount"],
                    category=r["category"],
                    payment_method=r["payment_method"],
                    notes=r["notes"],
                    created_at=r["created_at"],
                )
                for r in rows
            ]

    def get_summary(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> ExpenseSummary:
        """Calculates aggregated spending statistics for the selected timeframe."""
        query = "SELECT amount, category FROM expenses WHERE 1=1"
        params: List[Any] = []

        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

        if not rows:
            return ExpenseSummary(
                total_spent=0.0,
                transaction_count=0,
                avg_transaction=0.0,
                top_category="None",
                top_category_amount=0.0,
                category_totals={},
            )

        total_spent = 0.0
        cat_totals: Dict[str, float] = {}

        for r in rows:
            amt = float(r["amount"])
            cat = str(r["category"])
            total_spent += amt
            cat_totals[cat] = cat_totals.get(cat, 0.0) + amt

        top_cat = max(cat_totals.items(), key=lambda x: x[1])

        return ExpenseSummary(
            total_spent=round(total_spent, 2),
            transaction_count=len(rows),
            avg_transaction=round(total_spent / len(rows), 2),
            top_category=top_cat[0],
            top_category_amount=round(top_cat[1], 2),
            category_totals={k: round(v, 2) for k, v in cat_totals.items()},
        )

    def get_monthly_trends(self, year: Optional[int] = None) -> pd.DataFrame:
        """Returns monthly spending aggregated by year-month."""
        query = "SELECT strftime('%Y-%m', date) as month, SUM(amount) as total_spent, COUNT(id) as count FROM expenses"
        params: List[Any] = []
        if year:
            query += " WHERE strftime('%Y', date) = ?"
            params.append(str(year))
        query += " GROUP BY month ORDER BY month ASC;"

        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
        return df

    def get_category_breakdown(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Returns category breakdown as a DataFrame for plotting."""
        query = "SELECT category, SUM(amount) as total_spent, COUNT(id) as count FROM expenses WHERE 1=1"
        params: List[Any] = []
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        query += " GROUP BY category ORDER BY total_spent DESC;"

        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=params)
        return df
