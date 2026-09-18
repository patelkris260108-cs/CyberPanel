"""Tests for budget_planner.models (Expense and BudgetPlan)."""

from __future__ import annotations

import datetime

import pytest

from budget_planner.exceptions import InvalidBudgetError, InvalidExpenseError
from budget_planner.models import BudgetPlan, Expense

TODAY = datetime.date.today()


# ── Expense construction ───────────────────────────────────────────────────────

class TestExpenseConstruction:
    def test_valid_expense_stores_fields(self) -> None:
        e = Expense(date=TODAY, amount=10.50, category="Food", description="Lunch")
        assert e.date == TODAY
        assert e.amount == 10.50
        assert e.category == "Food"
        assert e.description == "Lunch"

    def test_default_description_is_empty(self) -> None:
        e = Expense(date=TODAY, amount=5.0, category="Travel")
        assert e.description == ""

    def test_zero_amount_raises(self) -> None:
        with pytest.raises(InvalidExpenseError):
            Expense(date=TODAY, amount=0.0, category="Food")

    def test_negative_amount_raises(self) -> None:
        with pytest.raises(InvalidExpenseError):
            Expense(date=TODAY, amount=-1.0, category="Food")

    def test_invalid_category_raises(self) -> None:
        with pytest.raises(InvalidExpenseError):
            Expense(date=TODAY, amount=5.0, category="Gambling")

    def test_description_too_long_raises(self) -> None:
        with pytest.raises(InvalidExpenseError):
            Expense(date=TODAY, amount=5.0, category="Food", description="x" * 201)

    def test_invalid_date_type_raises(self) -> None:
        with pytest.raises(InvalidExpenseError):
            Expense(date="not-a-date", amount=5.0, category="Food")  # type: ignore[arg-type]


# ── Expense serialisation ──────────────────────────────────────────────────────

class TestExpenseSerialization:
    def test_to_dict_returns_expected_keys(self) -> None:
        e = Expense(date=TODAY, amount=20.0, category="Shopping", description="Shoes")
        d = e.to_dict()
        assert set(d.keys()) == {"date", "amount", "category", "description"}

    def test_to_dict_date_is_iso_string(self) -> None:
        e = Expense(date=TODAY, amount=5.0, category="Food")
        assert e.to_dict()["date"] == TODAY.isoformat()

    def test_from_dict_round_trip(self) -> None:
        original = Expense(
            date=datetime.date(2024, 6, 15),
            amount=99.99,
            category="Education",
            description="Online course",
        )
        restored = Expense.from_dict(original.to_dict())
        assert restored.date == original.date
        assert restored.amount == pytest.approx(original.amount)
        assert restored.category == original.category
        assert restored.description == original.description

    def test_from_dict_no_description_key(self) -> None:
        data = {"date": TODAY.isoformat(), "amount": "10.0", "category": "Travel"}
        e = Expense.from_dict(data)
        assert e.description == ""


# ── BudgetPlan ─────────────────────────────────────────────────────────────────

class TestBudgetPlan:
    def test_default_budget_is_zero(self) -> None:
        plan = BudgetPlan()
        assert plan.monthly_budget == 0.0

    def test_negative_budget_raises(self) -> None:
        with pytest.raises(InvalidBudgetError):
            BudgetPlan(monthly_budget=-100.0)

    def test_add_expense_increments_list(self) -> None:
        plan = BudgetPlan(monthly_budget=500.0)
        e = Expense(date=TODAY, amount=25.0, category="Food")
        plan.add_expense(e)
        assert len(plan.expenses) == 1

    def test_total_expenses_sums_correctly(self) -> None:
        plan = BudgetPlan(monthly_budget=200.0)
        plan.add_expense(Expense(date=TODAY, amount=50.0, category="Food"))
        plan.add_expense(Expense(date=TODAY, amount=30.0, category="Travel"))
        assert plan.total_expenses() == pytest.approx(80.0)

    def test_remaining_budget(self) -> None:
        plan = BudgetPlan(monthly_budget=200.0)
        plan.add_expense(Expense(date=TODAY, amount=80.0, category="Shopping"))
        assert plan.remaining_budget() == pytest.approx(120.0)

    def test_remaining_budget_can_be_negative(self) -> None:
        plan = BudgetPlan(monthly_budget=10.0)
        plan.add_expense(Expense(date=TODAY, amount=50.0, category="Food"))
        assert plan.remaining_budget() < 0

    def test_category_totals(self) -> None:
        plan = BudgetPlan(monthly_budget=300.0)
        plan.add_expense(Expense(date=TODAY, amount=20.0, category="Food"))
        plan.add_expense(Expense(date=TODAY, amount=30.0, category="Food"))
        plan.add_expense(Expense(date=TODAY, amount=15.0, category="Travel"))
        totals = plan.category_totals()
        assert totals["Food"] == pytest.approx(50.0)
        assert totals["Travel"] == pytest.approx(15.0)

    def test_empty_plan_totals_are_zero(self) -> None:
        plan = BudgetPlan(monthly_budget=100.0)
        assert plan.total_expenses() == 0.0
        assert plan.remaining_budget() == pytest.approx(100.0)
        assert plan.category_totals() == {}
