"""Tests for cybersec.knowledge_base."""

from __future__ import annotations

import pytest

from cybersec.knowledge_base import (
    get_all_glossary_terms,
    get_all_threat_cards,
    get_all_tips,
    get_daily_tip,
    get_glossary_entry,
    get_threat_card,
    search_knowledge_base,
)


class TestGlossary:
    def test_all_terms_returns_list(self) -> None:
        terms = get_all_glossary_terms()
        assert isinstance(terms, list)
        assert len(terms) > 0

    def test_known_term_found(self) -> None:
        entry = get_glossary_entry("Phishing")
        assert entry is not None
        assert entry["term"] == "Phishing"

    def test_case_insensitive_lookup(self) -> None:
        entry = get_glossary_entry("phishing")
        assert entry is not None

    def test_unknown_term_returns_none(self) -> None:
        entry = get_glossary_entry("NotARealTerm_XYZ")
        assert entry is None

    def test_entry_has_required_keys(self) -> None:
        entry = get_glossary_entry("Ransomware")
        assert entry is not None
        for key in ("term", "definition", "related"):
            assert key in entry

    def test_terms_list_is_sorted(self) -> None:
        terms = get_all_glossary_terms()
        assert terms == sorted(terms)


class TestSearch:
    def test_search_returns_list(self) -> None:
        results = search_knowledge_base("phishing")
        assert isinstance(results, list)

    def test_search_finds_phishing(self) -> None:
        results = search_knowledge_base("phishing")
        assert len(results) > 0
        assert any("Phishing" in r.get("term", "") for r in results)

    def test_empty_search_returns_empty(self) -> None:
        # Nothing should match a completely nonsense query
        results = search_knowledge_base("zzzzznomatch99999")
        assert results == []


class TestThreatCards:
    def test_all_cards_returns_list(self) -> None:
        cards = get_all_threat_cards()
        assert isinstance(cards, list)
        assert len(cards) > 0

    def test_known_card_found(self) -> None:
        card = get_threat_card("ransomware")
        assert card is not None
        assert card["type"] == "ransomware"

    def test_unknown_card_returns_none(self) -> None:
        assert get_threat_card("not_a_real_threat") is None

    def test_card_has_prevention_field(self) -> None:
        card = get_threat_card("phishing")
        assert card is not None
        assert "prevention" in card
        assert isinstance(card["prevention"], list)


class TestTips:
    def test_daily_tip_is_string(self) -> None:
        tip = get_daily_tip()
        assert isinstance(tip, str)
        assert len(tip) > 0

    def test_daily_tip_is_deterministic(self) -> None:
        # Same day should always return the same tip
        tip1 = get_daily_tip()
        tip2 = get_daily_tip()
        assert tip1 == tip2

    def test_all_tips_returns_list(self) -> None:
        tips = get_all_tips()
        assert isinstance(tips, list)
        assert len(tips) > 0
