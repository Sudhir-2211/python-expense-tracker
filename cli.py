"""Command Line Interface for Python Expense Tracker.

Author: Sudhir Kumar (GitHub: Sudhir-2211)
"""

import argparse
import sys
from datetime import datetime
from src.database import ExpenseDatabase
from src.models import CATEGORIES, PAYMENT_METHODS
from src.seed import seed_database


def format_currency(amt: float) -> str:
    return f"${amt:,.2f}"


def main():
    parser = argparse.ArgumentParser(description="Terminal Expense Tracker Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available sub-commands")

    # Command: add
    add_parser = subparsers.add_parser("add", help="Add a new expense")
    add_parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="Date (YYYY-MM-DD)")
    add_parser.add_argument("--title", required=True, help="Expense title")
    add_parser.add_argument("--amount", type=float, required=True, help="Expense amount")
    add_parser.add_argument("--category", default="Food & Dining", choices=CATEGORIES, help="Expense category")
    add_parser.add_argument("--payment", default="Credit Card", choices=PAYMENT_METHODS, help="Payment method")
    add_parser.add_argument("--notes", default="", help="Optional notes")

    # Command: list
    list_parser = subparsers.add_parser("list", help="List recorded expenses")
    list_parser.add_argument("--limit", type=int, default=20, help="Maximum number of records to show")
    list_parser.add_argument("--category", default=None, help="Filter by category")
    list_parser.add_argument("--search", default=None, help="Keyword search in title or notes")

    # Command: summary
    subparsers.add_parser("summary", help="Show financial summary")

    # Command: delete
    del_parser = subparsers.add_parser("delete", help="Delete an expense by ID")
    del_parser.add_argument("id", type=int, help="Expense ID to remove")

    # Command: seed
    subparsers.add_parser("seed", help="Seed database with sample records")

    args = parser.parse_args()
    db = ExpenseDatabase()

    if args.command == "add":
        exp_id = db.add_expense(
            date=args.date,
            title=args.title,
            amount=args.amount,
            category=args.category,
            payment_method=args.payment,
            notes=args.notes,
        )
        print(f"[SUCCESS] Recorded expense #{exp_id}: '{args.title}' for {format_currency(args.amount)}")

    elif args.command == "list":
        records = db.list_expenses(category=args.category, search_query=args.search, limit=args.limit)
        if not records:
            print("No expenses found matching query.")
            return

        print("\n" + "=" * 80)
        print(f"{'ID':<5} {'Date':<12} {'Title':<25} {'Category':<22} {'Amount':>10}")
        print("=" * 80)
        for r in records:
            print(f"{r.id:<5} {r.date:<12} {r.title[:24]:<25} {r.category[:21]:<22} {format_currency(r.amount):>10}")
        print("=" * 80 + "\n")

    elif args.command == "summary":
        s = db.get_summary()
        print("\n" + "=" * 50)
        print("           FINANCIAL SUMMARY REPORT")
        print("=" * 50)
        print(f"Total Expenditure   : {format_currency(s.total_spent)}")
        print(f"Transactions Count  : {s.transaction_count}")
        print(f"Average Transaction : {format_currency(s.avg_transaction)}")
        print(f"Top Category        : {s.top_category} ({format_currency(s.top_category_amount)})")
        print("-" * 50)
        print("Category Breakdown:")
        for cat, total in sorted(s.category_totals.items(), key=lambda x: x[1], reverse=True):
            pct = (total / s.total_spent) * 100 if s.total_spent else 0
            print(f"  • {cat:<24} : {format_currency(total):>10} ({pct:5.1f}%)")
        print("=" * 50 + "\n")

    elif args.command == "delete":
        deleted = db.delete_expense(args.id)
        if deleted:
            print(f"[SUCCESS] Expense #{args.id} deleted.")
        else:
            print(f"[ERROR] Expense #{args.id} not found.")

    elif args.command == "seed":
        count = seed_database(db, 30)
        print(f"[SUCCESS] Seeded {count} realistic expense records.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
