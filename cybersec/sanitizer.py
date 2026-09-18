"""Input sanitiser — strip dangerous content and enforce length limits."""

from __future__ import annotations

import html
import re

from cybersec.config import MAX_INPUT_LENGTH, MAX_PASSWORD_LENGTH
from cybersec.exceptions import InvalidInputError

# Patterns that could indicate prompt-injection attempts.
_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(?:previous|all|above)\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(?:a|an|the)", re.IGNORECASE),
    re.compile(r"forget\s+(?:everything|all)\s+(?:you|about)", re.IGNORECASE),
    re.compile(r"system\s*:\s*", re.IGNORECASE),
    re.compile(r"<\s*/?(?:script|iframe|object|embed|form)", re.IGNORECASE),
]


def sanitize_input(text: str, max_length: int = MAX_INPUT_LENGTH) -> str:
    """Strip whitespace, HTML-escape, and truncate *text* to *max_length* characters."""
    if not isinstance(text, str):
        raise InvalidInputError("Input must be a string.")
    text = text.strip()
    # HTML-escape to prevent XSS if ever rendered outside Streamlit.
    text = html.escape(text, quote=True)
    if len(text) > max_length:
        text = text[:max_length]
    return text


def is_valid_input(text: str, min_length: int = 1) -> tuple[bool, str]:
    """Return (True, '') if input is valid, else (False, error_message)."""
    if not text or not text.strip():
        return False, "Please enter some text to analyse."
    if len(text.strip()) < min_length:
        return False, f"Input must be at least {min_length} character(s)."
    if len(text) > MAX_INPUT_LENGTH:
        return False, f"Input too long (max {MAX_INPUT_LENGTH:,} characters)."
    return True, ""


def has_injection_attempt(text: str) -> bool:
    """Return True if the text contains a likely prompt-injection pattern."""
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            return True
    return False


def sanitize_password_input(password: str) -> str:
    """Return *password* stripped of leading/trailing whitespace; enforce max length."""
    if not isinstance(password, str):
        raise InvalidInputError("Password must be a string.")
    password = password.strip()
    if len(password) > MAX_PASSWORD_LENGTH:
        password = password[:MAX_PASSWORD_LENGTH]
    return password
