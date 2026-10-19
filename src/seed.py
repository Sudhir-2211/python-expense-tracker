"""Seed realistic sample data into the expense tracker database."""

import random
from datetime import datetime, timedelta
from .database import ExpenseDatabase
from .models import CATEGORIES, PAYMENT_METHODS


SAMPLE_ITEMS = [
    ("Whole Foods Groceries", "Shopping & Groceries", (35.0, 160.0)),
    ("Trader Joe's", "Shopping & Groceries", (20.0, 85.0)),
    ("Uber Ride to Office", "Transportation", (12.0, 35.0)),
    ("Subway Metro Card", "Transportation", (30.0, 60.0)),
    ("Gas Station Refill", "Transportation", (40.0, 75.0)),
    ("Monthly Apartment Rent", "Housing & Rent", (1200.0, 1500.0)),
    ("Electric & Utility Bill", "Utilities & Bills", (60.0, 130.0)),
    ("High-Speed Internet Bill", "Utilities & Bills", (50.0, 75.0)),
    ("Chipotle Lunch", "Food & Dining", (12.0, 22.0)),
    ("Dinner with Friends", "Food & Dining", (40.0, 110.0)),
    ("Starbucks Morning Coffee", "Food & Dining", (4.5, 9.0)),
    ("Cinema Movie Tickets", "Entertainment & Leisure", (18.0, 36.0)),
    ("Netflix & Spotify Subscription", "Entertainment & Leisure", (20.0, 25.0)),
    ("Pharmacy Prescription", "Healthcare & Medical", (15.0, 45.0)),
    ("Dental Checkup Co-pay", "Healthcare & Medical", (50.0, 90.0)),
    ("Technical Book on Python", "Education & Career", (25.0, 55.0)),
    ("Online Course Subscription", "Education & Career", (20.0, 45.0)),
    ("Gym Membership", "Personal & Miscellaneous", (35.0, 50.0)),
    ("Haircut & Grooming", "Personal & Miscellaneous", (25.0, 40.0)),
]


def seed_database(db: ExpenseDatabase, num_records: int = 40) -> int:
    """Populates database with sample expenses spanning the last 90 days."""
    today = datetime.now()
    count = 0

    for _ in range(num_records):
        days_ago = random.randint(0, 90)
        date_val = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        title, cat, (min_amt, max_amt) = random.choice(SAMPLE_ITEMS)
        amount = round(random.uniform(min_amt, max_amt), 2)
        payment = random.choice(PAYMENT_METHODS)

        db.add_expense(
            date=date_val,
            title=title,
            amount=amount,
            category=cat,
            payment_method=payment,
            notes=f"Sample verified entry #{count+1}",
        )
        count += 1

    return count


if __name__ == "__main__":
    db = ExpenseDatabase()
    added = seed_database(db)
    print(f"Successfully seeded {added} sample expense records.")
