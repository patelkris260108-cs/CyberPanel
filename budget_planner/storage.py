"""CSV persistence layer for the Personal Budget Planner."""

from __future__ import annotations

import csv
import logging
import os
from pathlib import Path
from typing import Union

from budget_planner.exceptions import StorageError
from budget_planner.models import Expense

logger = logging.getLogger(__name__)

_FIELDNAMES = ["date", "amount", "category", "description"]


def load_expenses(path: Union[str, Path]) -> list[Expense]:
    """Load expenses from *path*; return an empty list if the file is missing."""
    p = Path(path)
    if not p.exists():
        return []
    expenses: list[Expense] = []
    try:
        with p.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                try:
                    expenses.append(Expense.from_dict(row))
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Skipping malformed CSV row %s: %s", row, exc)
    except OSError as exc:
        raise StorageError(f"Could not read expenses file: {exc}") from exc
    return expenses


def save_expenses(expenses: list[Expense], path: Union[str, Path]) -> None:
    """Write *expenses* to *path* as UTF-8 CSV, creating parent directories as needed."""
    p = Path(path)
    try:
        os.makedirs(p.parent, exist_ok=True)
        with p.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=_FIELDNAMES)
            writer.writeheader()
            for expense in expenses:
                writer.writerow(expense.to_dict())
    except OSError as exc:
        raise StorageError(f"Could not write expenses file: {exc}") from exc
