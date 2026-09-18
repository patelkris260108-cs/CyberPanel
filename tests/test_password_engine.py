"""Tests for cybersec.password_engine."""

from __future__ import annotations

import pytest

from cybersec.password_engine import (
    _calculate_entropy,
    _estimate_crack_time,
    _score_to_label,
    evaluate_password,
    generate_password,
)
from cybersec.models import PasswordResult


class TestEvaluatePassword:
    def test_empty_password_is_weak(self) -> None:
        result = evaluate_password("")
        assert result.label == "Weak"
        assert result.score == 0

    def test_common_password_is_weak(self) -> None:
        result = evaluate_password("password")
        assert result.score < 40
        assert any("common" in w.lower() or "dictionary" in w.lower() for w in result.weaknesses)

    def test_short_password_flagged(self) -> None:
        result = evaluate_password("abc")
        assert any("short" in w.lower() or "Too short" in w for w in result.weaknesses)

    def test_no_uppercase_flagged(self) -> None:
        result = evaluate_password("abcdefgh123!")
        assert any("uppercase" in w.lower() for w in result.weaknesses)

    def test_no_symbols_flagged(self) -> None:
        result = evaluate_password("Abcdefgh123")
        assert any("special" in w.lower() or "symbol" in w.lower() for w in result.weaknesses)

    def test_strong_password_high_score(self) -> None:
        result = evaluate_password("Maple!Rocket42Cloud$Zenith99")
        assert result.score >= 60
        assert result.label in ("Strong", "Very Strong")

    def test_sequential_pattern_flagged(self) -> None:
        result = evaluate_password("Password123abc")
        # 'abc' or '123' should trigger sequential warning
        assert result.score < 80

    def test_result_has_crack_time(self) -> None:
        result = evaluate_password("SomePassword!")
        assert isinstance(result.crack_time, str)
        assert len(result.crack_time) > 0

    def test_suggestions_always_present(self) -> None:
        result = evaluate_password("anything")
        assert len(result.suggestions) > 0

    def test_result_type(self) -> None:
        result = evaluate_password("Test123!")
        assert isinstance(result, PasswordResult)
        assert isinstance(result.score, int)
        assert 0 <= result.score <= 100


class TestGeneratePassword:
    def test_generated_password_is_string(self) -> None:
        pwd = generate_password()
        assert isinstance(pwd, str)

    def test_generated_password_meets_min_length(self) -> None:
        pwd = generate_password()
        assert len(pwd) >= 16

    def test_generated_password_is_strong(self) -> None:
        for _ in range(5):  # test multiple generations
            pwd = generate_password()
            result = evaluate_password(pwd)
            assert result.score >= 60, f"Generated password '{pwd}' scored only {result.score}"


class TestEntropyAndCrackTime:
    def test_entropy_increases_with_length(self) -> None:
        e1 = _calculate_entropy("abc")
        e2 = _calculate_entropy("abcdefgh")
        assert e2 > e1

    def test_entropy_increases_with_complexity(self) -> None:
        e_simple = _calculate_entropy("aaaaaaaa")
        e_complex = _calculate_entropy("aA1!aA1!")
        assert e_complex > e_simple

    def test_crack_time_instant_for_empty(self) -> None:
        assert _estimate_crack_time(0) == "less than 1 second"

    def test_crack_time_years_for_high_entropy(self) -> None:
        time_str = _estimate_crack_time(80)
        assert "year" in time_str or "million" in time_str


class TestScoreToLabel:
    def test_zero_is_weak(self) -> None:
        assert _score_to_label(0) == "Weak"

    def test_100_is_very_strong(self) -> None:
        assert _score_to_label(100) == "Very Strong"

    def test_midpoints(self) -> None:
        assert _score_to_label(20) == "Fair"
        assert _score_to_label(40) == "Good"
        assert _score_to_label(60) == "Strong"
        assert _score_to_label(80) == "Very Strong"
