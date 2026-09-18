"""Password strength evaluation and secure password generation engine."""

from __future__ import annotations

import math
import random
import re
import string

from cybersec.config import COMMON_PASSWORDS_PATH, PASSWORD_LABELS
from cybersec.models import PasswordResult

# ── Common password list (loaded once at import time) ──────────────────────────
_COMMON_PASSWORDS: set[str] = set()

try:
    import pathlib
    _cp_path = pathlib.Path(COMMON_PASSWORDS_PATH)
    if _cp_path.exists():
        with _cp_path.open(encoding="utf-8") as fh:
            _COMMON_PASSWORDS = {line.strip().lower() for line in fh if line.strip()}
except OSError:
    pass  # safe to continue without the file

# ── Word list for passphrase generation (built-in fallback) ───────────────────
_WORDLIST: list[str] = [
    "apple", "bridge", "cloud", "dragon", "eagle", "forest", "garden", "harbor",
    "island", "jungle", "kettle", "lantern", "mango", "nebula", "orange", "palace",
    "quartz", "rabbit", "silver", "temple", "umbrella", "violet", "walnut", "xenon",
    "yellow", "zephyr", "anchor", "basket", "castle", "dinner", "ember", "falcon",
    "glacier", "hollow", "impact", "jasper", "kayak", "lemon", "mirror", "night",
    "ocean", "planet", "quest", "river", "stone", "tower", "ultra", "vapor",
    "winter", "xylem", "yonder", "zenith", "amber", "brook", "coral", "dusk",
    "flame", "grain", "hover", "ivory", "jewel", "knoll", "lunar", "maple",
    "north", "orbit", "prism", "queen", "ridge", "spark", "thorn", "upper",
    "vortex", "marsh", "pixel", "forge", "bison", "cedar",
]


# ── Core evaluation functions ──────────────────────────────────────────────────

def evaluate_password(password: str) -> PasswordResult:
    """Run the full strength evaluation pipeline on *password*."""
    if not password:
        return PasswordResult(
            score=0, label="Weak", entropy_bits=0.0,
            crack_time="instant", weaknesses=["Password is empty."],
            suggestions=["Enter a password to evaluate."],
        )

    weaknesses: list[str] = []
    suggestions: list[str] = []
    score = 100  # start perfect, deduct for issues

    # Length checks
    length = len(password)
    if length < 8:
        score -= 40
        weaknesses.append(f"Too short ({length} chars) — minimum 8 recommended.")
        suggestions.append("Use at least 12 characters; 16+ is ideal.")
    elif length < 12:
        score -= 20
        weaknesses.append(f"Short ({length} chars) — 12+ recommended.")
        suggestions.append("Extend to at least 12 characters.")
    elif length < 16:
        score -= 5
    # 16+ chars gets no length deduction

    # Character class checks
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_symbol = bool(re.search(r"[^A-Za-z0-9]", password))

    if not has_upper:
        score -= 10
        weaknesses.append("No uppercase letters.")
        suggestions.append("Add at least one uppercase letter (A–Z).")
    if not has_lower:
        score -= 10
        weaknesses.append("No lowercase letters.")
        suggestions.append("Add at least one lowercase letter (a–z).")
    if not has_digit:
        score -= 10
        weaknesses.append("No numbers.")
        suggestions.append("Include at least one number (0–9).")
    if not has_symbol:
        score -= 15
        weaknesses.append("No special characters.")
        suggestions.append("Add symbols like !@#$%^&* to greatly increase strength.")

    # Common password check
    if password.lower() in _COMMON_PASSWORDS:
        score -= 50
        weaknesses.append("This is one of the most commonly used passwords.")
        suggestions.append(
            "This password is in attacker dictionaries — choose something unique."
        )

    # Pattern checks
    if re.search(r"(.)\1{2,}", password):
        score -= 10
        weaknesses.append("Contains repeated characters (e.g., 'aaa', '111').")
        suggestions.append("Avoid repeating the same character three or more times.")

    if re.search(r"(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|qwe|wer|ert|asd|sdf)", password, re.IGNORECASE):
        score -= 10
        weaknesses.append("Contains a sequential pattern (e.g., '123', 'abc', 'qwe').")
        suggestions.append("Avoid keyboard walks and sequential characters.")

    if re.search(r"\b(password|passwd|pass|login|admin|user|welcome|letmein|qwerty)\b", password, re.IGNORECASE):
        score -= 25
        weaknesses.append("Contains a common dictionary word attackers try first.")
        suggestions.append(
            "Replace dictionary words with a passphrase of 4+ unrelated words."
        )

    if re.search(r"\b(19|20)\d{2}\b", password):
        score -= 5
        weaknesses.append("Contains what looks like a year (e.g., 1990, 2024).")
        suggestions.append("Avoid using birth years or familiar dates.")

    # Bonus for long password with all classes
    if length >= 16 and has_upper and has_lower and has_digit and has_symbol:
        score += 5  # bonus

    score = max(0, min(100, score))
    entropy = _calculate_entropy(password)
    label = _score_to_label(score)
    crack_time = _estimate_crack_time(entropy)

    if not suggestions:
        suggestions.append("Great password! Consider using a password manager to store it safely.")

    return PasswordResult(
        score=score,
        label=label,
        entropy_bits=round(entropy, 1),
        crack_time=crack_time,
        weaknesses=weaknesses,
        suggestions=suggestions,
    )


def generate_password(length: int = 20) -> str:
    """Generate a strong random passphrase (4 words + numbers + symbols)."""
    words = random.sample(_WORDLIST, 4)
    # Capitalise first letter of each word
    words = [w.capitalize() for w in words]
    # Insert 2-digit number and a symbol between words
    symbols = "!@#$%^&*"
    parts: list[str] = []
    for i, word in enumerate(words):
        parts.append(word)
        if i < 3:
            parts.append(random.choice(symbols))
            parts.append(str(random.randint(1, 99)).zfill(2))
    return "".join(parts)


def _calculate_entropy(password: str) -> float:
    """Return Shannon entropy for *password* in bits."""
    pool = 0
    if re.search(r"[a-z]", password):
        pool += 26
    if re.search(r"[A-Z]", password):
        pool += 26
    if re.search(r"\d", password):
        pool += 10
    if re.search(r"[^A-Za-z0-9]", password):
        pool += 32
    if pool == 0:
        pool = 1
    return len(password) * math.log2(pool)


def _estimate_crack_time(entropy_bits: float) -> str:
    """Return a human-readable crack-time estimate at 10 billion guesses/second."""
    guesses_per_second = 10_000_000_000  # 10 billion (modern GPU)
    seconds = (2 ** entropy_bits) / guesses_per_second

    if seconds < 1:
        return "less than 1 second"
    if seconds < 60:
        return f"{int(seconds)} seconds"
    if seconds < 3_600:
        return f"{int(seconds / 60)} minutes"
    if seconds < 86_400:
        return f"{int(seconds / 3_600)} hours"
    if seconds < 86_400 * 365:
        return f"{int(seconds / 86_400)} days"
    if seconds < 86_400 * 365 * 1_000:
        return f"{int(seconds / (86_400 * 365))} years"
    if seconds < 86_400 * 365 * 1_000_000:
        return f"{int(seconds / (86_400 * 365 * 1_000))} thousand years"
    return "millions of years"


def _score_to_label(score: int) -> str:
    """Map a 0–100 score to a human-readable strength label."""
    for threshold, label in PASSWORD_LABELS:
        if score >= threshold:
            return label
    return "Weak"
