"""Tests for budget_planner.validators."""

from __future__ import annotations

import datetime

import pytest

from budget_planner.exceptions import InvalidBudgetError, InvalidExpenseError
from budget_planner.validators import (
    ALLOWED_CATEGORIES,
    validate_budget,
    validate_category,
    validate_date,
    validate_description,
    validate_positive_amount,
)


class TestValidatePositiveAmount:
    def test_positive_value_passes(self) -> None:
        validate_positive_amount(0.01)  # should not raise

    def test_large_value_passes(self) -> None:
        validate_positive_amount(999_999.99)  # should not raise

    def test_zero_raises(self) -> None:
        with pytest.raises(InvalidExpenseError, match="greater than zero"):
            validate_positive_amount(0.0)

    def test_negative_raises(self) -> None:
        with pytest.raises(InvalidExpenseError):
            validate_positive_amount(-5.0)

    def test_non_numeric_raises(self) -> None:
        with pytest.raises(InvalidExpenseError):
            validate_positive_amount("abc")  # type: ignore[arg-type]


class TestValidateBudget:
    def test_zero_budget_passes(self) -> None:
        validate_budget(0.0)  # should not raise

    def test_positive_budget_passes(self) -> None:
        validate_budget(500.0)  # should not raise

    def test_negative_budget_raises(self) -> None:
        with pytest.raises(InvalidBudgetError, match="non-negative"):
            validate_budget(-1.0)

    def test_non_numeric_budget_raises(self) -> None:
        with pytest.raises(InvalidBudgetError):
            validate_budget("hello")  # type: ignore[arg-type]


class TestValidateDate:
    def test_valid_date_passes(self) -> None:
        validate_date(datetime.date.today())  # should not raise

    def test_past_date_passes(self) -> None:
        validate_date(datetime.date(2000, 1, 1))  # should not raise

    def test_string_raises(self) -> None:
        with pytest.raises(InvalidExpenseError, match="valid date"):
            validate_date("2024-01-01")

    def test_none_raises(self) -> None:
        with pytest.raises(InvalidExpenseError):
            validate_date(None)

    def test_integer_raises(self) -> None:
        with pytest.raises(InvalidExpenseError):
            validate_date(20240101)  # type: ignore[arg-type]


class TestValidateCategory:
    def test_all_allowed_categories_pass(self) -> None:
        for cat in ALLOWED_CATEGORIES:
            validate_category(cat)  # should not raise

    def test_invalid_category_raises(self) -> None:
        with pytest.raises(InvalidExpenseError, match="valid category"):
            validate_category("Gambling")

    def test_empty_string_raises(self) -> None:
        with pytest.raises(InvalidExpenseError):
            validate_category("")

    def test_case_sensitive(self) -> None:
        with pytest.raises(InvalidExpenseError):
            validate_category("food")  # lowercase should not match "Food"


class TestValidateDescription:
    def test_empty_string_passes(self) -> None:
        validate_description("")  # should not raise

    def test_exactly_200_chars_passes(self) -> None:
        validate_description("a" * 200)  # should not raise

    def test_201_chars_raises(self) -> None:
        with pytest.raises(InvalidExpenseError, match="200 characters"):
            validate_description("x" * 201)

    def test_unicode_within_limit_passes(self) -> None:
        validate_description("🎉" * 50)  # should not raise (50 chars)
