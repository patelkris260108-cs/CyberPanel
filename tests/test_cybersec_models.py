"""Tests for cybersec.models (AnalysisResult, PasswordResult, ChatMessage)."""

from __future__ import annotations

import datetime

import pytest

from cybersec.models import AnalysisResult, ChatMessage, PasswordResult


class TestAnalysisResult:
    def test_construction_with_required_fields(self) -> None:
        r = AnalysisResult(
            risk_score=75,
            severity="high",
            indicators=["Urgency language detected"],
            explanation="This looks like a phishing attempt.",
            advice="Delete the message.",
        )
        assert r.risk_score == 75
        assert r.severity == "high"
        assert r.source == "heuristic"  # default

    def test_severity_emoji_mapping(self) -> None:
        for severity, expected_emoji in [
            ("safe", "✅"),
            ("low", "🟡"),
            ("medium", "🟠"),
            ("high", "🔴"),
            ("critical", "💀"),
        ]:
            r = AnalysisResult(
                risk_score=50, severity=severity, indicators=[],
                explanation="", advice="",
            )
            assert r.severity_emoji == expected_emoji

    def test_unknown_severity_emoji(self) -> None:
        r = AnalysisResult(
            risk_score=50, severity="unknown", indicators=[],
            explanation="", advice="",
        )
        assert r.severity_emoji == "⚪"

    def test_severity_color_property(self) -> None:
        r = AnalysisResult(
            risk_score=80, severity="critical", indicators=[],
            explanation="", advice="",
        )
        assert "red" in r.severity_color.lower()


class TestPasswordResult:
    def test_construction(self) -> None:
        r = PasswordResult(
            score=85,
            label="Very Strong",
            entropy_bits=64.0,
            crack_time="millions of years",
            weaknesses=[],
            suggestions=["Use a password manager"],
        )
        assert r.score == 85
        assert r.generated is None  # default

    def test_score_color_for_each_band(self) -> None:
        for score, expected_colour in [
            (85, "green"),
            (65, "blue"),
            (45, "orange"),
            (25, "darkorange"),
            (10, "red"),
        ]:
            r = PasswordResult(
                score=score, label="Test", entropy_bits=0.0,
                crack_time="", weaknesses=[], suggestions=[],
            )
            assert r.score_color == expected_colour


class TestChatMessage:
    def test_default_timestamp(self) -> None:
        before = datetime.datetime.now()
        msg = ChatMessage(role="user", content="Hello")
        after = datetime.datetime.now()
        assert before <= msg.timestamp <= after

    def test_feedback_default_is_none(self) -> None:
        msg = ChatMessage(role="assistant", content="Hi!")
        assert msg.feedback is None

    def test_custom_feedback(self) -> None:
        msg = ChatMessage(role="assistant", content="Hi!", feedback="positive")
        assert msg.feedback == "positive"
