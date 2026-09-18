"""Configuration and constants for the AI Cybersecurity Guide & Analyzer."""

from __future__ import annotations

import os

# ── LLM settings (NVIDIA NIM — OpenAI-compatible endpoint) ────────────────────
NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL: str = os.getenv(
    "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
)
LLM_MODEL: str = os.getenv("CYBERSEC_MODEL", "mistralai/mistral-nemotron")
LLM_MAX_TOKENS: int = int(os.getenv("CYBERSEC_MAX_TOKENS", "1024"))

# ── Input limits ───────────────────────────────────────────────────────────────
MAX_INPUT_LENGTH: int = 10_000   # characters
MAX_PASSWORD_LENGTH: int = 512   # characters

# ── Risk severity thresholds ───────────────────────────────────────────────────
SEVERITY_THRESHOLDS: dict[str, int] = {
    "safe": 0,
    "low": 20,
    "medium": 40,
    "high": 65,
    "critical": 85,
}

# ── Password score thresholds ──────────────────────────────────────────────────
PASSWORD_LABELS: list[tuple[int, str]] = [
    (80, "Very Strong"),
    (60, "Strong"),
    (40, "Good"),
    (20, "Fair"),
    (0,  "Weak"),
]

# ── Data file paths ────────────────────────────────────────────────────────────
import pathlib
_HERE = pathlib.Path(__file__).parent.parent  # project root
KNOWLEDGE_BASE_PATH: str = str(_HERE / "data" / "knowledge_base.json")
COMMON_PASSWORDS_PATH: str = str(_HERE / "data" / "common_passwords.txt")
