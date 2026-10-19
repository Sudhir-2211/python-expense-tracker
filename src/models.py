"""Domain models and data classes for Expense Tracker."""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any


CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Housing & Rent",
    "Utilities & Bills",
    "Entertainment & Leisure",
    "Healthcare & Medical",
    "Shopping & Groceries",
    "Education & Career",
    "Personal & Miscellaneous",
]

PAYMENT_METHODS = [
    "Cash",
    "Credit Card",
    "Debit Card",
    "UPI / Mobile Pay",
    "Bank Transfer",
]


@dataclass
class Expense:
    """Represents a single financial expense record."""
    id: Optional[int]
    date: str  # YYYY-MM-DD
    title: str
    amount: float
    category: str
    payment_method: str = "Credit Card"
    notes: Optional[str] = ""
    created_at: Optional[str] = None


@dataclass
class ExpenseSummary:
    """Aggregated financial summary metrics."""
    total_spent: float
    transaction_count: int
    avg_transaction: float
    top_category: str
    top_category_amount: float
    category_totals: Dict[str, float]
