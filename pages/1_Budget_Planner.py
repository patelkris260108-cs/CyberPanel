"""Personal Budget Planner – Streamlit page."""

from __future__ import annotations

import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from budget_planner.calculations import (
    category_totals,
    remaining_budget,
    total_expenses,
)
from budget_planner.exceptions import InvalidBudgetError, InvalidExpenseError
from budget_planner.models import BudgetPlan, Expense
from budget_planner.storage import load_expenses, save_expenses
from budget_planner.validators import ALLOWED_CATEGORIES

DATA_PATH = Path("data/expenses.csv")

st.set_page_config(
    page_title="💰 Personal Budget Planner",
    page_icon="💰",
    layout="wide",
)

# ── Session-state initialisation (runs once per session) ──────────────────────
if "plan" not in st.session_state:
    loaded = load_expenses(DATA_PATH)
    st.session_state.plan = BudgetPlan(monthly_budget=0.0)
    for exp in loaded:
        st.session_state.plan.add_expense(exp)

if "monthly_budget" not in st.session_state:
    st.session_state.monthly_budget = 0.0

# ── Sidebar – budget input ─────────────────────────────────────────────────────
with st.sidebar:
    st.header("💰 Personal Budget Planner")
    budget_input = st.number_input(
        "Monthly Budget ($)",
        min_value=0.0,
        step=1.0,
        value=float(st.session_state.monthly_budget),
        format="%.2f",
    )
    if st.button("Save Budget", use_container_width=True):
        try:
            st.session_state.plan.monthly_budget = float(budget_input)
            st.session_state.monthly_budget = float(budget_input)
            st.success(f"Budget saved: ${budget_input:,.2f}")
        except InvalidBudgetError as exc:
            st.error(str(exc))

# ── Main area ─────────────────────────────────────────────────────────────────
st.title("💰 Personal Budget Planner")

# ── Expense entry form ────────────────────────────────────────────────────────
st.subheader("Add an Expense")
with st.form("expense_form", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    with col_a:
        category = st.selectbox("Category", options=ALLOWED_CATEGORIES)
        amount = st.number_input(
            "Amount ($)", min_value=0.01, step=0.01, format="%.2f"
        )
    with col_b:
        description = st.text_input("Description (optional)", max_chars=200)
        date = st.date_input("Date", value=datetime.date.today())

    submitted = st.form_submit_button("➕ Add Expense", use_container_width=True)

if submitted:
    try:
        expense = Expense(
            date=date,
            amount=amount,
            category=category,
            description=description,
        )
        st.session_state.plan.add_expense(expense)
        save_expenses(st.session_state.plan.expenses, DATA_PATH)
        st.success(
            f"✅ Added **${amount:,.2f}** in **{category}** on {date.isoformat()}"
        )
    except InvalidExpenseError as exc:
        st.error(str(exc))
    except InvalidBudgetError as exc:
        st.error(str(exc))
    except Exception:
        st.error("An unexpected error occurred. Please try again.")

# ── Summary metrics ────────────────────────────────────────────────────────────
plan: BudgetPlan = st.session_state.plan
total = total_expenses(plan.expenses)
remaining = remaining_budget(plan.monthly_budget, plan.expenses)

st.divider()
m1, m2, m3 = st.columns(3)
m1.metric("Monthly Budget", f"${plan.monthly_budget:,.2f}")
m2.metric("Total Spent", f"${total:,.2f}")
delta_color = "normal" if remaining >= 0 else "inverse"
m3.metric(
    "Remaining Budget",
    f"${remaining:,.2f}",
    delta=f"${remaining:,.2f}",
    delta_color=delta_color,
)

# ── Category-wise spending chart ──────────────────────────────────────────────
st.subheader("Category-wise Spending")
cat_totals = category_totals(plan.expenses)

if cat_totals:
    cat_df = pd.DataFrame(
        cat_totals.items(), columns=["Category", "Amount ($)"]
    ).sort_values("Amount ($)", ascending=False)
    st.bar_chart(cat_df.set_index("Category"))
    st.dataframe(
        cat_df.style.format({"Amount ($)": "${:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No expenses recorded yet – add one above.")

# ── All expenses table ────────────────────────────────────────────────────────
st.subheader("All Expenses")
if plan.expenses:
    rows = [e.to_dict() for e in reversed(plan.expenses)]
    df = pd.DataFrame(rows, columns=["date", "amount", "category", "description"])
    df.rename(
        columns={
            "date": "Date",
            "amount": "Amount ($)",
            "category": "Category",
            "description": "Description",
        },
        inplace=True,
    )
    st.dataframe(
        df.style.format({"Amount ($)": "${:.2f}"}),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No expenses yet.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.caption(f"📁 Expenses are stored in `{DATA_PATH.resolve()}`")
