"""Tests for cyberguard.prompts – structural checks (no LLM calls)."""

from __future__ import annotations

from cyberguard.prompts import COT_TRIGGER, FEW_SHOTS, SYSTEM_PROMPT


class TestSystemPrompt:
    def test_system_prompt_is_non_empty(self) -> None:
        assert SYSTEM_PROMPT.strip() != ""

    def test_system_prompt_mentions_cyberguard(self) -> None:
        assert "CyberGuard" in SYSTEM_PROMPT

    def test_system_prompt_has_safety_rules(self) -> None:
        assert "NOT" in SYSTEM_PROMPT or "never" in SYSTEM_PROMPT.lower()

    def test_system_prompt_requests_step_by_step(self) -> None:
        assert "step" in SYSTEM_PROMPT.lower()


class TestFewShots:
    def test_all_required_keys_present(self) -> None:
        required = {"phishing", "explainer", "password", "behavior"}
        assert required.issubset(set(FEW_SHOTS.keys()))

    def test_each_few_shot_is_non_empty(self) -> None:
        for key, text in FEW_SHOTS.items():
            assert text.strip() != "", f"Few-shot '{key}' is empty"

    def test_phishing_example_contains_url_reference(self) -> None:
        assert "amaz0n" in FEW_SHOTS["phishing"] or "phishing" in FEW_SHOTS["phishing"].lower()

    def test_password_example_mentions_password(self) -> None:
        assert "password" in FEW_SHOTS["password"].lower()

    def test_explainer_example_mentions_ransomware(self) -> None:
        assert "ransomware" in FEW_SHOTS["explainer"].lower()


class TestCotTrigger:
    def test_cot_trigger_is_non_empty(self) -> None:
        assert COT_TRIGGER.strip() != ""

    def test_cot_trigger_contains_step_by_step(self) -> None:
        assert "step" in COT_TRIGGER.lower()
