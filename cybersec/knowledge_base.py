"""Offline knowledge base — glossary, tips, and threat cards."""

from __future__ import annotations

import datetime
import json
import pathlib
from typing import Any

from cybersec.config import KNOWLEDGE_BASE_PATH
from cybersec.exceptions import KnowledgeBaseError

_kb: dict[str, Any] = {}


def _load() -> dict[str, Any]:
    """Load and cache the knowledge base from disk."""
    global _kb
    if _kb:
        return _kb
    path = pathlib.Path(KNOWLEDGE_BASE_PATH)
    if not path.exists():
        return {}
    try:
        with path.open(encoding="utf-8") as fh:
            _kb = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        raise KnowledgeBaseError(f"Could not load knowledge base: {exc}") from exc
    return _kb


def get_glossary_entry(term: str) -> dict[str, Any] | None:
    """Return the glossary entry for *term* (case-insensitive); None if not found."""
    kb = _load()
    for entry in kb.get("glossary", []):
        if entry.get("term", "").lower() == term.lower():
            return entry
    return None


def get_all_glossary_terms() -> list[str]:
    """Return a sorted list of all glossary term names."""
    kb = _load()
    return sorted(e.get("term", "") for e in kb.get("glossary", []))


def search_knowledge_base(query: str) -> list[dict[str, Any]]:
    """Return glossary entries whose term or definition contains *query* (case-insensitive)."""
    kb = _load()
    q = query.lower()
    results = []
    for entry in kb.get("glossary", []):
        if (q in entry.get("term", "").lower() or
                q in entry.get("definition", "").lower()):
            results.append(entry)
    return results


def get_daily_tip() -> str:
    """Return a deterministic daily tip based on today's date."""
    kb = _load()
    tips = kb.get("behavior_nudges", [])
    if not tips:
        return "Stay safe online — always verify before you click!"
    day_of_year = datetime.date.today().timetuple().tm_yday
    return tips[day_of_year % len(tips)]


def get_all_tips() -> list[str]:
    """Return all behavior nudge tips."""
    kb = _load()
    return kb.get("behavior_nudges", [])


def get_threat_card(threat_type: str) -> dict[str, Any] | None:
    """Return the threat card for *threat_type*; None if not found."""
    kb = _load()
    for card in kb.get("threat_cards", []):
        if card.get("type", "").lower() == threat_type.lower():
            return card
    return None


def get_all_threat_cards() -> list[dict[str, Any]]:
    """Return all threat reference cards."""
    kb = _load()
    return kb.get("threat_cards", [])
