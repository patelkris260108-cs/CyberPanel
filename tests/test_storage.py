"""Tests for budget_planner.storage (load_expenses, save_expenses)."""

from __future__ import annotations

import datetime
from pathlib import Path

import pytest

from budget_planner.models import Expense
from budget_planner.storage import load_expenses, save_expenses

TODAY = datetime.date.today()


def _make_expense(
    amount: float = 10.0,
    category: str = "Food",
    description: str = "Test",
    date: datetime.date = TODAY,
) -> Expense:
    return Expense(date=date, amount=amount, category=category, description=description)


class TestLoadExpenses:
    def test_missing_file_returns_empty_list(self, tmp_path: Path) -> None:
        result = load_expenses(tmp_path / "nonexistent.csv")
        assert result == []

    def test_empty_csv_with_header_returns_empty_list(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "expenses.csv"
        csv_file.write_text("date,amount,category,description\n", encoding="utf-8")
        result = load_expenses(csv_file)
        assert result == []

    def test_load_single_expense(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "expenses.csv"
        csv_file.write_text(
            "date,amount,category,description\n"
            f"{TODAY.isoformat()},25.5,Food,Breakfast\n",
            encoding="utf-8",
        )
        expenses = load_expenses(csv_file)
        assert len(expenses) == 1
        assert expenses[0].amount == pytest.approx(25.5)
        assert expenses[0].category == "Food"
        assert expenses[0].description == "Breakfast"
        assert expenses[0].date == TODAY

    def test_malformed_row_is_skipped(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "expenses.csv"
        csv_file.write_text(
            "date,amount,category,description\n"
            "bad-date,not_a_number,Unknown,\n"  # invalid row
            f"{TODAY.isoformat()},5.0,Travel,Bus\n",  # valid row
            encoding="utf-8",
        )
        expenses = load_expenses(csv_file)
        # Only the valid row should be loaded.
        assert len(expenses) == 1
        assert expenses[0].category == "Travel"

    def test_unicode_description_loaded_correctly(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "expenses.csv"
        csv_file.write_text(
            "date,amount,category,description\n"
            f"{TODAY.isoformat()},10.0,Food,Café 🎉\n",
            encoding="utf-8",
        )
        expenses = load_expenses(csv_file)
        assert expenses[0].description == "Café 🎉"


class TestSaveExpenses:
    def test_save_creates_parent_directory(self, tmp_path: Path) -> None:
        nested = tmp_path / "deep" / "nested" / "expenses.csv"
        save_expenses([], nested)
        assert nested.exists()

    def test_save_writes_header(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "expenses.csv"
        save_expenses([], csv_file)
        content = csv_file.read_text(encoding="utf-8")
        assert "date" in content
        assert "amount" in content
        assert "category" in content
        assert "description" in content

    def test_save_and_load_round_trip(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "expenses.csv"
        original = [
            _make_expense(10.0, "Food", "Breakfast", TODAY),
            _make_expense(50.0, "Shopping", "Shirt", datetime.date(2024, 3, 15)),
            _make_expense(200.0, "Education", "Course 🎓", TODAY),
        ]
        save_expenses(original, csv_file)
        loaded = load_expenses(csv_file)

        assert len(loaded) == len(original)
        for orig, rest in zip(original, loaded):
            assert rest.date == orig.date
            assert rest.amount == pytest.approx(orig.amount)
            assert rest.category == orig.category
            assert rest.description == orig.description

    def test_save_overwrites_existing_file(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "expenses.csv"
        save_expenses([_make_expense(10.0)], csv_file)
        save_expenses([_make_expense(99.0, "Travel", "Taxi")], csv_file)
        loaded = load_expenses(csv_file)
        assert len(loaded) == 1
        assert loaded[0].amount == pytest.approx(99.0)

    def test_empty_list_saves_only_header(self, tmp_path: Path) -> None:
        csv_file = tmp_path / "expenses.csv"
        save_expenses([], csv_file)
        loaded = load_expenses(csv_file)
        assert loaded == []
