"""Configuration for CyberGuard — now powered by NVIDIA NIM."""

from __future__ import annotations

import os

# ── NVIDIA NIM settings (OpenAI-compatible) ────────────────────────────────
NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL: str = os.getenv(
    "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
)
MODEL_NAME: str = os.getenv("CYBERGUARD_MODEL", "mistralai/mistral-nemotron")
MAX_TOKENS: int = int(os.getenv("CYBERGUARD_MAX_TOKENS", "1024"))

# Maximum input length accepted from users (characters).
MAX_INPUT_LEN: int = 4000
