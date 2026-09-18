"""Input validation helpers for the Personal Budget Planner."""

from __future__ import annotations

import datetime

from budget_planner.exceptions import InvalidBudgetError, InvalidExpenseError

ALLOWED_CATEGORIES: list[str] = ["Food", "Travel", "Shopping", "Education"]


def validate_positive_amount(value: float, name: str = "Amount") -> None:
    """Raise InvalidExpenseError if *value* is not greater than zero."""
    try:
        fval = float(value)
    except (TypeError, ValueError):
        raise InvalidExpenseError(
            f"Expense amount must be greater than zero."
        )
    if fval <= 0:
        raise InvalidExpenseError("Expense amount must be greater than zero.")


def validate_budget(value: float) -> None:
    """Raise InvalidBudgetError if *value* is negative or non-numeric."""
    try:
        fval = float(value)
    except (TypeError, ValueError):
        raise InvalidBudgetError("Budget must be a non-negative number.")
    if fval < 0:
        raise InvalidBudgetError("Budget must be a non-negative number.")


def validate_date(value: object) -> None:
    """Raise InvalidExpenseError if *value* is not a valid datetime.date."""
    if not isinstance(value, datetime.date):
        raise InvalidExpenseError("Please pick a valid date.")


def validate_category(value: str) -> None:
    """Raise InvalidExpenseError if *value* is not in ALLOWED_CATEGORIES."""
    if value not in ALLOWED_CATEGORIES:
        raise InvalidExpenseError(
            f"Please select a valid category. "
            f"Allowed: {', '.join(ALLOWED_CATEGORIES)}."
        )


def validate_description(value: str) -> None:
    """Raise InvalidExpenseError if *value* exceeds 200 characters."""
    if len(value) > 200:
        raise InvalidExpenseError(
            "Description too long (max 200 characters)."
        )
