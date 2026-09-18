"""Tests for cybersec.heuristics — rule-based phishing detection."""

from __future__ import annotations

import pytest

from cybersec.heuristics import analyze_text
from cybersec.models import AnalysisResult


class TestKnownPhishingSamples:
    def test_fake_amazon_link_is_high_risk(self) -> None:
        text = (
            "Dear customer, your account has been locked. "
            "Click here to verify: http://amaz0n-secure.com/login"
        )
        result = analyze_text(text)
        assert result.risk_score >= 40
        assert result.severity in ("medium", "high", "critical")
        assert len(result.indicators) > 0

    def test_credential_request_raises_score(self) -> None:
        text = "Please enter your password and credit card details to continue."
        result = analyze_text(text)
        assert result.risk_score >= 35

    def test_urgency_language_contributes_to_score(self) -> None:
        text = "URGENT: Your account will be suspended. Act now immediately!"
        result = analyze_text(text)
        assert result.risk_score >= 20

    def test_ip_address_url_flagged(self) -> None:
        text = "Please verify your account at http://192.168.1.1/verify"
        result = analyze_text(text)
        assert result.risk_score >= 20

    def test_domain_spoofing_detected(self) -> None:
        text = "Log in at http://paypa1.secure-login.com to fix your issue."
        result = analyze_text(text)
        assert result.risk_score >= 25

    def test_attachment_threat_flagged(self) -> None:
        text = "Please open the attached .exe file to install the required update."
        result = analyze_text(text)
        assert result.risk_score >= 25

    def test_generic_greeting_adds_points(self) -> None:
        text = "Dear Customer, please review your recent activity."
        result = analyze_text(text)
        assert result.risk_score >= 5


class TestBenignContent:
    def test_simple_greeting_is_safe(self) -> None:
        result = analyze_text("Hi John, hope you are well. Let's meet Tuesday.")
        assert result.severity == "safe"
        assert result.risk_score < 25

    def test_empty_indicators_for_clean_text(self) -> None:
        result = analyze_text("The weather is nice today.")
        assert result.indicators == []
        assert result.risk_score == 0

    def test_severity_label_safe_for_low_score(self) -> None:
        result = analyze_text("Thanks for your order!")
        assert result.severity == "safe"


class TestAnalysisResultFields:
    def test_result_has_all_required_fields(self) -> None:
        result = analyze_text("Test message")
        assert isinstance(result, AnalysisResult)
        assert isinstance(result.risk_score, int)
        assert isinstance(result.severity, str)
        assert isinstance(result.indicators, list)
        assert isinstance(result.explanation, str)
        assert isinstance(result.advice, str)

    def test_score_is_clamped_to_100(self) -> None:
        # Maximum possible input with many indicators
        text = (
            "Dear customer URGENT: your account is suspended! "
            "Enter your password and credit card. "
            "Click http://paypa1-secure.net/verify or open the attached .exe. "
            "amaz0n is asking you to confirm now immediately!"
        )
        result = analyze_text(text)
        assert 0 <= result.risk_score <= 100

    def test_severity_emoji_property(self) -> None:
        result = analyze_text("Test")
        assert result.severity_emoji in ("✅", "🟡", "🟠", "🔴", "💀", "⚪")
