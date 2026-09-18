"""Pure calculation functions for the Personal Budget Planner."""

from __future__ import annotations

from budget_planner.models import Expense


def total_expenses(expenses: list[Expense]) -> float:
    """Return the sum of all expense amounts."""
    return sum(e.amount for e in expenses)


def remaining_budget(budget: float, expenses: list[Expense]) -> float:
    """Return *budget* minus the total of all *expenses*."""
    return budget - total_expenses(expenses)


def category_totals(expenses: list[Expense]) -> dict[str, float]:
    """Return a mapping of category name to total amount spent in that category."""
    totals: dict[str, float] = {}
    for exp in expenses:
        totals[exp.category] = totals.get(exp.category, 0.0) + exp.amount
    return totals
