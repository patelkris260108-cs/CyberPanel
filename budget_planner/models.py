"""Domain model classes for the Personal Budget Planner."""

from __future__ import annotations

import datetime
from typing import Any

from budget_planner.validators import (
    validate_budget,
    validate_category,
    validate_date,
    validate_description,
    validate_positive_amount,
)


class Expense:
    """Represents a single expense entry with date, amount, category, and description."""

    def __init__(
        self,
        date: datetime.date,
        amount: float,
        category: str,
        description: str = "",
    ) -> None:
        """Validate and store all fields; raise InvalidExpenseError on bad input."""
        validate_date(date)
        validate_positive_amount(amount)
        validate_category(category)
        validate_description(description)
        self.date = date
        self.amount = float(amount)
        self.category = category
        self.description = description

    def to_dict(self) -> dict[str, Any]:
        """Return a CSV-serialisable dict with ISO-formatted date."""
        return {
            "date": self.date.isoformat(),
            "amount": self.amount,
            "category": self.category,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Expense:
        """Construct an Expense from a CSV row dict; raises on invalid data."""
        return cls(
            date=datetime.date.fromisoformat(data["date"]),
            amount=float(data["amount"]),
            category=data["category"],
            description=data.get("description", ""),
        )


class BudgetPlan:
    """Holds a monthly budget and a collection of expenses."""

    def __init__(self, monthly_budget: float = 0.0) -> None:
        """Initialise the plan; raise InvalidBudgetError if budget is negative."""
        validate_budget(monthly_budget)
        self.monthly_budget = float(monthly_budget)
        self.expenses: list[Expense] = []

    def add_expense(self, expense: Expense) -> None:
        """Append a validated Expense to the plan."""
        self.expenses.append(expense)

    def total_expenses(self) -> float:
        """Return the sum of all expense amounts."""
        return sum(e.amount for e in self.expenses)

    def remaining_budget(self) -> float:
        """Return the monthly budget minus total expenses."""
        return self.monthly_budget - self.total_expenses()

    def category_totals(self) -> dict[str, float]:
        """Return a mapping of category name to total amount spent in that category."""
        totals: dict[str, float] = {}
        for exp in self.expenses:
            totals[exp.category] = totals.get(exp.category, 0.0) + exp.amount
        return totals
