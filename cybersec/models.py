"""Data models (dataclasses) for the AI Cybersecurity Guide & Analyzer."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field


@dataclass
class AnalysisResult:
    """Result of a phishing / risk analysis operation."""

    risk_score: int                    # 0–100
    severity: str                      # safe | low | medium | high | critical
    indicators: list[str]              # specific red-flag strings found
    explanation: str                   # plain-language summary
    advice: str                        # actionable recommendation
    reasoning: str = ""               # step-by-step CoT trace
    source: str = "heuristic"         # heuristic | llm | combined

    @property
    def severity_emoji(self) -> str:
        """Return a visual emoji for the severity level."""
        return {
            "safe": "✅",
            "low": "🟡",
            "medium": "🟠",
            "high": "🔴",
            "critical": "💀",
        }.get(self.severity, "⚪")

    @property
    def severity_color(self) -> str:
        """Return a CSS-compatible colour name for the severity level."""
        return {
            "safe": "green",
            "low": "orange",
            "medium": "darkorange",
            "high": "red",
            "critical": "darkred",
        }.get(self.severity, "grey")


@dataclass
class PasswordResult:
    """Result of a password strength evaluation."""

    score: int                         # 0–100
    label: str                         # Weak | Fair | Good | Strong | Very Strong
    entropy_bits: float                # calculated entropy
    crack_time: str                    # human-readable time-to-crack estimate
    weaknesses: list[str]             # specific problems found
    suggestions: list[str]            # improvement tips
    generated: str | None = None      # generated strong alternative

    @property
    def score_color(self) -> str:
        """Return a colour name corresponding to the password strength."""
        if self.score >= 80:
            return "green"
        if self.score >= 60:
            return "blue"
        if self.score >= 40:
            return "orange"
        if self.score >= 20:
            return "darkorange"
        return "red"


@dataclass
class ChatMessage:
    """A single message in the cybersecurity chatbot conversation."""

    role: str                          # user | assistant
    content: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    feedback: str | None = None       # positive | negative | None
