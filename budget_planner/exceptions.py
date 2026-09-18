"""Custom exceptions for the Personal Budget Planner application."""

from __future__ import annotations


class InvalidBudgetError(ValueError):
    """Raised when a monthly budget value fails validation."""


class InvalidExpenseError(ValueError):
    """Raised when any expense field fails validation."""


class StorageError(Exception):
    """Raised when a CSV read or write operation fails."""
