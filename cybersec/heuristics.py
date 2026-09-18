"""Rule-based heuristic phishing and risk detection engine.

Runs entirely offline in < 200 ms with no API key required.
"""

from __future__ import annotations

import re

from cybersec.config import SEVERITY_THRESHOLDS
from cybersec.models import AnalysisResult

# ── Compiled regex patterns ────────────────────────────────────────────────────

_URGENCY_PATTERNS = re.compile(
    r"\b(act\s+now|urgent|immediately|account\s+(suspended|locked|blocked|disabled)|"
    r"verify\s+(your|account|now|immediately)|limited\s+time|expires?\s+(in|today|soon)|"
    r"final\s+notice|last\s+chance|respond\s+(now|immediately)|action\s+required|"
    r"security\s+alert|unusual\s+(activity|sign[-\s]?in)|click\s+(here|now|immediately)|"
    r"confirm\s+(your|identity|account|now))\b",
    re.IGNORECASE,
)

_CREDENTIAL_REQUEST_PATTERNS = re.compile(
    r"\b(enter\s+(your\s+)?(password|pin|ssn|social\s+security|credit\s+card|"
    r"bank\s+account|cvv|otp|one[-\s]time\s+pass)|"
    r"provide\s+(your\s+)?(credentials|login|password|username)|"
    r"submit\s+(your\s+)?(?:personal\s+)?information|"
    r"update\s+(your\s+)?(payment|billing|card)\s+(info|details|method))\b",
    re.IGNORECASE,
)

_SUSPICIOUS_URL_PATTERNS = re.compile(
    r"(https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|"  # IP address URL
    r"bit\.ly|tinyurl\.com|goo\.gl|t\.co/|ow\.ly|"     # URL shorteners
    r"http://(?!localhost)[^\s]+|"                       # plain HTTP (not HTTPS)
    r"[a-z0-9]+-secure\.[a-z]+|"                        # fake "secure" domains
    r"(?:amazon|paypal|google|microsoft|apple|netflix|facebook|instagram)"
    r"[0-9\-\.][a-z0-9\-\.]*\.[a-z]+)",                # brand misspellings
    re.IGNORECASE,
)

_IMPERSONATION_PATTERNS = re.compile(
    r"\b(dear\s+(customer|user|member|client|valued)|"
    r"from\s+(amazon|paypal|apple|google|microsoft|netflix|facebook|"
    r"instagram|your\s+bank|irs|hmrc|tax\s+authority|social\s+security)|"
    r"your\s+(amazon|paypal|apple|google|microsoft)\s+account)\b",
    re.IGNORECASE,
)

_ATTACHMENT_THREAT_PATTERNS = re.compile(
    r"\b(open\s+(?:the\s+)?attached?|attachment|\.exe|\.zip|\.docm|"
    r"\.xlsm|\.scr|\.bat|\.vbs|\.js\b|download\s+(?:and\s+)?(?:run|open|install))\b",
    re.IGNORECASE,
)

_GENERIC_GREETING_PATTERNS = re.compile(
    r"^(dear\s+(customer|user|member|client|account\s+holder)|"
    r"hello\s+(there|friend)|greetings|dear\s+sir[,/]?madam)",
    re.IGNORECASE | re.MULTILINE,
)

_DOMAIN_SPOOFING_PATTERNS = re.compile(
    r"(amaz[o0]n|payp[a@1][a@1]l|paypa[1l]|g[o0][o0]gle|micr[o0]s[o0]ft|app1e|"
    r"faceb[o0][o0]k|netfl[i1]x|inst[a@]gr[a@]m|tw[i1]tter|"
    r"b[a@]nk[o0]f[a@]mer[i1]c[a@]|ch[a@]se|w[e3]lls?f[a@]rg[o0])",
    re.IGNORECASE,
)

# ── Indicator weights (each tuple: description, score) ────────────────────────
_WEIGHTS: dict[str, int] = {
    "credential_request": 35,
    "domain_spoofing": 30,
    "impersonation": 25,
    "suspicious_url": 20,
    "urgency_language": 20,
    "attachment_threat": 25,
    "http_not_https": 10,
    "generic_greeting": 5,
}


def analyze_text(text: str) -> AnalysisResult:
    """Run all heuristic checks on *text* and return a scored AnalysisResult."""
    raw_text = text  # keep original for display
    indicators: list[str] = []
    score_sum = 0

    # Run each check
    checks: list[tuple[str, re.Pattern[str], str]] = [
        ("credential_request", _CREDENTIAL_REQUEST_PATTERNS,
         "Requests sensitive credentials or personal information"),
        ("domain_spoofing", _DOMAIN_SPOOFING_PATTERNS,
         "Contains a misspelled or spoofed brand domain"),
        ("impersonation", _IMPERSONATION_PATTERNS,
         "Impersonates a trusted brand or authority"),
        ("suspicious_url", _SUSPICIOUS_URL_PATTERNS,
         "Contains a suspicious URL (IP address, shortener, or plain HTTP)"),
        ("urgency_language", _URGENCY_PATTERNS,
         "Uses urgency tactics to pressure immediate action"),
        ("attachment_threat", _ATTACHMENT_THREAT_PATTERNS,
         "References a potentially dangerous file or attachment"),
        ("generic_greeting", _GENERIC_GREETING_PATTERNS,
         "Uses a generic greeting — legitimate services address you by name"),
    ]

    for key, pattern, description in checks:
        matches = pattern.findall(raw_text)
        if matches:
            score_sum += _WEIGHTS[key]
            sample = matches[0] if isinstance(matches[0], str) else matches[0][0]
            indicators.append(f"{description} (e.g. '{sample[:60]}')")

    # HTTP check (separate from URL pattern, different message)
    if re.search(r"http://(?!localhost)", raw_text, re.IGNORECASE):
        if "Contains a suspicious URL" not in " ".join(indicators):
            score_sum += _WEIGHTS["http_not_https"]
            indicators.append("Link uses insecure HTTP instead of HTTPS")

    # Clamp score to 0–100
    risk_score = min(score_sum, 100)
    severity = _score_to_severity(risk_score)
    explanation, advice = _generate_explanation(severity, indicators)

    return AnalysisResult(
        risk_score=risk_score,
        severity=severity,
        indicators=indicators,
        explanation=explanation,
        advice=advice,
        source="heuristic",
    )


def _score_to_severity(score: int) -> str:
    """Map a numeric score to a severity label."""
    for label in ("critical", "high", "medium", "low", "safe"):
        if score >= SEVERITY_THRESHOLDS[label]:
            return label
    return "safe"


def _generate_explanation(severity: str, indicators: list[str]) -> tuple[str, str]:
    """Return a plain-language (explanation, advice) pair based on severity."""
    if severity == "safe":
        return (
            "This message does not contain obvious phishing indicators. "
            "It appears to be low-risk based on automated checks.",
            "No immediate action required. Always verify unexpected requests through "
            "official channels.",
        )
    if severity == "low":
        return (
            f"This message has {len(indicators)} minor warning sign(s). "
            "It may be legitimate but warrants caution.",
            "Do not click links or download attachments unless you were expecting this "
            "message. Verify by contacting the sender through a known, official channel.",
        )
    if severity == "medium":
        return (
            f"This message shows {len(indicators)} suspicious pattern(s) commonly "
            "found in phishing attempts. Treat with significant caution.",
            "Do not click any links or provide any information. If it claims to be from "
            "a company, go directly to their official website by typing it manually.",
        )
    if severity == "high":
        return (
            f"This message has {len(indicators)} strong phishing indicator(s). "
            "It is very likely a fraudulent attempt to steal your information.",
            "Delete this message immediately. Do NOT click any links or download "
            "attachments. Report it to your email/SMS provider as phishing.",
        )
    # critical
    return (
        f"CRITICAL: This message exhibits {len(indicators)} hallmarks of a dangerous "
        "phishing or scam attempt. Do not interact with it under any circumstances.",
        "DELETE this message immediately. Report it to your provider, your organisation's "
        "IT/security team, and relevant authorities (e.g., Action Fraud, IC3). "
        "If you have already clicked a link, change your passwords immediately.",
    )
