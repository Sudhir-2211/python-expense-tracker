"""Streamlit Web Dashboard for Python Expense Tracker.

Author: Sudhir Kumar (GitHub: Sudhir-2211)
"""

import io
from datetime import datetime, timedelta
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.database import ExpenseDatabase
from src.models import CATEGORIES, PAYMENT_METHODS
from src.seed import seed_database

# Page Configuration
st.set_page_config(
    page_title="Personal Expense Tracker | Sudhir Kumar",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0F766E;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-header">💰 Personal Finance & Expense Tracker</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Persistent SQLite personal finance management with analytics, category budgeting, and interactive spending charts.</div>',
    unsafe_allow_html=True,
)

# Initialize Database
db = ExpenseDatabase()

# Check if DB has data; if empty, offer quick seed
all_existing = db.list_expenses(limit=1)
if not all_existing:
    st.info("💡 Your expense database is currently empty. Click below to load realistic sample expenses.")
    if st.button("🌱 Load Sample Data (40 Transactions)"):
        seed_database(db)
        st.success("Sample data seeded successfully!")
        st.rerun()

# Sidebar: Filter Controls
st.sidebar.header("🔍 Filters & Search")

date_preset = st.sidebar.selectbox(
    "Date Range Preset",
    ["All Time", "This Month", "Last 30 Days", "This Year", "Custom Range"],
)

today = datetime.now().date()
start_date = None
end_date = None

if date_preset == "This Month":
    start_date = today.replace(day=1).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
elif date_preset == "Last 30 Days":
    start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
elif date_preset == "This Year":
    start_date = today.replace(month=1, day=1).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
elif date_preset == "Custom Range":
    d_range = st.sidebar.date_input(
        "Select Range",
        value=(today - timedelta(days=30), today),
    )
    if isinstance(d_range, tuple) and len(d_range) == 2:
        start_date = d_range[0].strftime("%Y-%m-%d")
        end_date = d_range[1].strftime("%Y-%m-%d")

selected_category = st.sidebar.selectbox("Filter by Category", ["All"] + CATEGORIES)
search_query = st.sidebar.text_input("Search Title / Notes", placeholder="e.g. coffee, rent, uber")

# Fetch filtered data
expenses = db.list_expenses(
    start_date=start_date,
    end_date=end_date,
    category=selected_category if selected_category != "All" else None,
    search_query=search_query if search_query else None,
)
summary = db.get_summary(start_date=start_date, end_date=end_date)

# High-Level Metric Cards
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Spending", f"${summary.total_spent:,.2f}")
with m2:
    st.metric("Total Transactions", f"{len(expenses)}")
with m3:
    st.metric("Avg Transaction", f"${summary.avg_transaction:,.2f}")
with m4:
    st.metric("Top Spending Category", f"{summary.top_category} (${summary.top_category_amount:,.2f})")

st.markdown("---")

# Main Interface Tabs
tab_analytics, tab_manage, tab_add, tab_export = st.tabs(
    ["📊 Spending Analytics", "📋 Transaction History", "➕ Add Expense", "💾 Export & Tools"]
)

# Tab 1: Analytics
with tab_analytics:
    cat_df = db.get_category_breakdown(start_date=start_date, end_date=end_date)
    month_df = db.get_monthly_trends()

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.subheader("Category Spending Breakdown")
        if not cat_df.empty:
            fig_pie = px.pie(
                cat_df,
                names="category",
                values="total_spent",
                hole=0.45,
                color_discrete_sequence=px.colors.qualitative.Safe,
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(margin=dict(t=20, b=20, l=20, r=20), showlegend=False)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense data available for the selected range.")

    with col_chart2:
        st.subheader("Monthly Spending Trends")
        if not month_df.empty:
            fig_bar = px.bar(
                month_df,
                x="month",
                y="total_spent",
                text="total_spent",
                labels={"month": "Month", "total_spent": "Total ($)"},
                color_discrete_sequence=["#0F766E"],
            )
            fig_bar.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
            fig_bar.update_layout(margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No monthly data recorded yet.")

# Tab 2: Manage Transactions
with tab_manage:
    st.subheader(f"Transactions ({len(expenses)} records)")

    if expenses:
        exp_data = [
            {
                "ID": e.id,
                "Date": e.date,
                "Title": e.title,
                "Amount ($)": f"${e.amount:,.2f}",
                "Category": e.category,
                "Payment Method": e.payment_method,
                "Notes": e.notes,
            }
            for e in expenses
        ]
        st.dataframe(pd.DataFrame(exp_data), use_container_width=True)

        # Edit / Delete Section
        st.markdown("#### ✏️ Modify or Delete Transaction")
        del_col1, del_col2 = st.columns([1, 2])
        with del_col1:
            selected_id = st.number_input("Enter Expense ID", min_value=1, step=1)
            target = db.get_expense(int(selected_id))

        if target:
            with st.expander(f"Edit Expense #{target.id}: {target.title}", expanded=True):
                with st.form("edit_form"):
                    e_date = st.date_input("Date", value=datetime.strptime(target.date, "%Y-%m-%d").date())
                    e_title = st.text_input("Title", value=target.title)
                    e_amount = st.number_input("Amount ($)", min_value=0.01, value=float(target.amount), step=1.0)
                    e_cat = st.selectbox(
                        "Category",
                        CATEGORIES,
                        index=CATEGORIES.index(target.category) if target.category in CATEGORIES else 0,
                    )
                    e_pm = st.selectbox(
                        "Payment Method",
                        PAYMENT_METHODS,
                        index=PAYMENT_METHODS.index(target.payment_method) if target.payment_method in PAYMENT_METHODS else 0,
                    )
                    e_notes = st.text_area("Notes", value=target.notes or "")

                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        update_submitted = st.form_submit_button("💾 Save Changes")
                    with btn_col2:
                        delete_submitted = st.form_submit_button("🗑️ Delete Expense", type="primary")

                    if update_submitted:
                        db.update_expense(
                            expense_id=target.id,
                            date=e_date.strftime("%Y-%m-%d"),
                            title=e_title,
                            amount=e_amount,
                            category=e_cat,
                            payment_method=e_pm,
                            notes=e_notes,
                        )
                        st.success(f"Expense #{target.id} updated!")
                        st.rerun()

                    if delete_submitted:
                        db.delete_expense(target.id)
                        st.warning(f"Expense #{target.id} deleted.")
                        st.rerun()
    else:
        st.info("No transactions match the selected filter criteria.")

# Tab 3: Add Expense
with tab_add:
    st.subheader("Add New Expense")
    with st.form("add_expense_form", clear_on_submit=True):
        f_date = st.date_input("Expense Date", value=today)
        f_title = st.text_input("Expense Title", placeholder="e.g. Grocery shopping, Gas, Lunch")
        f_amount = st.number_input("Amount ($)", min_value=0.01, step=1.0, format="%.2f")
        f_category = st.selectbox("Category", CATEGORIES)
        f_payment = st.selectbox("Payment Method", PAYMENT_METHODS)
        f_notes = st.text_area("Optional Notes", placeholder="e.g. Paid split with roommates")

        submitted = st.form_submit_button("➕ Record Expense")
        if submitted:
            if not f_title.strip():
                st.error("Please enter a valid expense title.")
            else:
                try:
                    new_id = db.add_expense(
                        date=f_date.strftime("%Y-%m-%d"),
                        title=f_title.strip(),
                        amount=f_amount,
                        category=f_category,
                        payment_method=f_payment,
                        notes=f_notes.strip(),
                    )
                    st.success(f"Expense recorded successfully! (ID: {new_id})")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Failed to record expense: {ex}")

# Tab 4: Export & Tools
with tab_export:
    st.subheader("Data Management & CSV Export")
    all_data = db.list_expenses()
    if all_data:
        export_df = pd.DataFrame([
            {
                "id": e.id,
                "date": e.date,
                "title": e.title,
                "amount": e.amount,
                "category": e.category,
                "payment_method": e.payment_method,
                "notes": e.notes,
                "created_at": e.created_at,
            }
            for e in all_data
        ])

        csv_str = export_df.to_csv(index=False)
        st.download_button(
            label="📥 Download All Expenses as CSV",
            data=csv_str.encode("utf-8"),
            file_name=f"expenses_export_{today}.csv",
            mime="text/csv",
        )

    st.markdown("---")
    st.markdown("#### Database Seeding & Reset")
    if st.button("🌱 Add 20 Random Sample Expenses"):
        added = seed_database(db, num_records=20)
        st.success(f"Added {added} sample records.")
        st.rerun()
