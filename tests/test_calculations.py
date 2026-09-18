"""Tests for budget_planner.calculations."""

from __future__ import annotations

import datetime

import pytest

from budget_planner.calculations import (
    category_totals,
    remaining_budget,
    total_expenses,
)
from budget_planner.models import Expense

TODAY = datetime.date.today()


def _expense(amount: float, category: str = "Food") -> Expense:
    return Expense(date=TODAY, amount=amount, category=category)


class TestTotalExpenses:
    def test_empty_list_returns_zero(self) -> None:
        assert total_expenses([]) == pytest.approx(0.0)

    def test_single_expense(self) -> None:
        assert total_expenses([_expense(25.0)]) == pytest.approx(25.0)

    def test_multiple_expenses(self) -> None:
        expenses = [_expense(10.0), _expense(20.0), _expense(5.50)]
        assert total_expenses(expenses) == pytest.approx(35.50)

    def test_floating_point_precision(self) -> None:
        expenses = [_expense(0.1), _expense(0.2)]
        assert total_expenses(expenses) == pytest.approx(0.3, rel=1e-6)


class TestRemainingBudget:
    def test_no_expenses_returns_budget(self) -> None:
        assert remaining_budget(500.0, []) == pytest.approx(500.0)

    def test_exact_spend_returns_zero(self) -> None:
        expenses = [_expense(200.0), _expense(300.0)]
        assert remaining_budget(500.0, expenses) == pytest.approx(0.0)

    def test_under_budget_positive_remaining(self) -> None:
        expenses = [_expense(100.0), _expense(50.0)]
        assert remaining_budget(300.0, expenses) == pytest.approx(150.0)

    def test_over_budget_negative_remaining(self) -> None:
        expenses = [_expense(600.0)]
        assert remaining_budget(500.0, expenses) == pytest.approx(-100.0)

    def test_zero_budget_is_negative_total(self) -> None:
        expenses = [_expense(75.0)]
        assert remaining_budget(0.0, expenses) == pytest.approx(-75.0)


class TestCategoryTotals:
    def test_empty_list_returns_empty_dict(self) -> None:
        assert category_totals([]) == {}

    def test_single_category(self) -> None:
        expenses = [_expense(10.0, "Food"), _expense(20.0, "Food")]
        totals = category_totals(expenses)
        assert totals == {"Food": pytest.approx(30.0)}

    def test_multiple_categories(self) -> None:
        expenses = [
            _expense(10.0, "Food"),
            _expense(20.0, "Travel"),
            _expense(15.0, "Food"),
            _expense(5.0, "Shopping"),
        ]
        totals = category_totals(expenses)
        assert totals["Food"] == pytest.approx(25.0)
        assert totals["Travel"] == pytest.approx(20.0)
        assert totals["Shopping"] == pytest.approx(5.0)
        assert "Education" not in totals

    def test_keys_are_strings(self) -> None:
        expenses = [_expense(1.0, "Education")]
        totals = category_totals(expenses)
        assert isinstance(list(totals.keys())[0], str)

    def test_all_four_categories(self) -> None:
        expenses = [
            _expense(100.0, "Food"),
            _expense(200.0, "Travel"),
            _expense(300.0, "Shopping"),
            _expense(400.0, "Education"),
        ]
        totals = category_totals(expenses)
        assert set(totals.keys()) == {"Food", "Travel", "Shopping", "Education"}
        assert sum(totals.values()) == pytest.approx(1000.0)
