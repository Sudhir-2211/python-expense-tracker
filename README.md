# Python Personal Expense Tracker

[![Tests](https://img.shields.io/badge/tests-9%20passed-brightgreen.svg)]()
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)]()
[![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey.svg)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A personal finance management application with **persistent SQLite storage**, parameterized SQL queries, date range and category filtering, interactive spending visualizations powered by **Plotly**, a web UI built with **Streamlit**, and a companion **CLI management tool**.

Developed by **[Sudhir Kumar](https://github.com/Sudhir-2211)** as part of the student placement portfolio.

---

## 📌 Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Database Schema & Design](#database-schema--design)
- [Folder Structure](#folder-structure)
- [Installation & Setup](#installation--setup)
- [Running the Streamlit Dashboard](#running-the-streamlit-dashboard)
- [Command Line Interface (CLI)](#command-line-interface-cli)
- [Automated Testing](#automated-testing)
- [Security & Safe Access Patterns](#security--safe-access-patterns)
- [Limitations & Future Improvements](#limitations--future-improvements)
- [License](#license)

---

## 📖 Project Overview

Budgeting and expenditure tracking are critical life and business skills. Many simple expense trackers rely on in-memory lists or unindexed text files that lose state upon application restarts.

**Python Personal Expense Tracker** provides:
- **ACID-compliant SQLite database persistence** with automatic schema initialization and index creation on date and category columns.
- **Robust input validation** enforcing non-empty titles, valid ISO `YYYY-MM-DD` dates, and strictly positive amounts (`CHECK (amount > 0)`).
- **Interactive web dashboard** for visual analytics (donut charts, trend bars, transaction ledger).
- **Terminal CLI** for rapid transaction logging and terminal summary reports.
- **Zero remote API requirements** and 100% offline, privacy-first execution.

---

## ✨ Key Features

1. **Full CRUD Operations**:
   - Create, Read, Update, and Delete expense entries with instant data synchronization.
2. **Category & Tag Classification**:
   - Standard categories: *Food & Dining, Transportation, Housing & Rent, Utilities & Bills, Entertainment & Leisure, Healthcare & Medical, Shopping & Groceries, Education & Career, Personal & Miscellaneous*.
3. **Advanced Filtering & Search**:
   - Filter by timeframe presets: *Today, This Month, Last 30 Days, This Year, or Custom Date Picker*.
   - Filter by specific spending category.
   - Case-insensitive keyword search across expense titles and notes.
4. **Interactive Financial Analytics**:
   - Metric cards: Total Outflow, Transaction Count, Average Spending per Transaction, Top Spending Category.
   - Interactive category allocation donut chart.
   - Monthly trend bar charts showing historical spend trajectory.
5. **Data Portability**:
   - Single-click CSV export of all recorded transactions.
   - Automated sample data generator (`seed.py`) for demonstration and testing.

---

## 🛠️ Architecture & Tech Stack

- **Backend**: Python 3.10+ (tested on Python 3.13)
- **Database**: SQLite 3 (Standard Library `sqlite3` with parameterized statements and context-managed connections)
- **Web UI**: Streamlit 1.30+
- **Charts & Graphs**: Plotly Express & Plotly Graph Objects
- **Data Manipulation**: Pandas
- **Automated Testing**: PyTest

---

## 🗄️ Database Schema & Design

```sql
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

CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
```

---

## 📁 Folder Structure

```text
python-expense-tracker/
├── .gitignore               # Ignores *.db, cache, and virtual environments
├── LICENSE                  # MIT License
├── README.md                # Project documentation
├── requirements.txt         # Project dependencies
├── app.py                   # Streamlit web dashboard
├── cli.py                   # Command-line utility for expense logging
├── src/
│   ├── __init__.py          # Package initializer
│   ├── database.py          # SQLite database connection & query engine
│   ├── models.py            # Dataclasses and domain constants
│   └── seed.py              # Sample dataset generator
└── tests/
    ├── __init__.py
    └── test_tracker.py      # Automated PyTest test suite
```

---

## 🚀 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sudhir-2211/python-expense-tracker.git
   cd python-expense-tracker
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🖥️ Running the Streamlit Dashboard

Start the local web application:
```bash
streamlit run app.py
```

Open your browser at `http://localhost:8501`.

If the database is fresh, click **"🌱 Load Sample Data (40 Transactions)"** to populate the dashboard with realistic multi-month test records.

---

## 💻 Command Line Interface (CLI)

The CLI allows fast logging and summary generation directly from PowerShell or Bash:

### 1. Seed Sample Data
```bash
python cli.py seed
```

### 2. Add an Expense
```bash
python cli.py add --date 2024-03-20 --title "Trader Joe's" --amount 42.50 --category "Shopping & Groceries" --payment "Debit Card"
```

### 3. View Recent Expenses
```bash
python cli.py list --limit 10
```

### 4. Search Expenses
```bash
python cli.py list --search "coffee"
```

### 5. Display Financial Summary Report
```bash
python cli.py summary
```

### 6. Delete an Expense by ID
```bash
python cli.py delete 14
```

---

## 🧪 Automated Testing

Automated unit tests use temporary isolated SQLite databases to test:
- Record creation, retrieval, updates, and deletion.
- Schema constraints (`CHECK (amount > 0)` and negative value rejection).
- Date validation (`YYYY-MM-DD`).
- Empty titles and malformed input rejection.
- Summary calculations and category breakdowns.

Run test suite:
```bash
python -m pytest -v
```

Expected output:
```text
============================== 9 passed in 0.64s ==============================
```

---

## 🔒 Security & Safe Access Patterns

1. **SQL Injection Prevention**: All queries use strict parameterized queries (`?` placeholders) with bound parameters; no raw SQL string concatenation is ever performed.
2. **Resource Management**: Uses Python's `@contextmanager` to ensure all database connections and cursors close deterministically, preventing database lockups on Windows.
3. **No Secrets**: Database credentials or sensitive payment details are never stored.

---

## ⚠️ Limitations & Future Improvements

- **Current Limitations**: Single-user local application designed for individual finance tracking.
- **Future Improvements**:
  - Add recurring expense automation (monthly subscriptions, rent).
  - Add monthly budget threshold alerts (e.g. notify when Dining out exceeds $300/month).
  - Multi-currency support with dynamic foreign exchange conversion.

---

## 📄 License

This repository is licensed under the [MIT License](LICENSE).
