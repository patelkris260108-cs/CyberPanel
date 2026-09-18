"""Orchestrator: wires heuristics + LLM into a unified analysis pipeline."""

from __future__ import annotations

from cybersec.chat_history import ChatHistory
from cybersec.heuristics import analyze_text as heuristic_analyze
from cybersec.llm_client import LLMClient
from cybersec.models import AnalysisResult, PasswordResult
from cybersec.password_engine import evaluate_password, generate_password
from cybersec.prompt_builder import (
    SYSTEM_PROMPT,
    build_analysis_prompt,
    build_chat_prompt,
    build_password_prompt,
)
from cybersec.sanitizer import sanitize_input, sanitize_password_input


def analyze_message(
    raw_text: str,
    client: LLMClient,
) -> tuple[AnalysisResult, str]:
    """Analyse *raw_text* for phishing/risk; returns (AnalysisResult, llm_explanation).

    The heuristic result is always computed.  If the LLM is available it adds
    a natural-language explanation and step-by-step reasoning.
    """
    text = sanitize_input(raw_text)
    heuristic_result = heuristic_analyze(text)

    llm_explanation = ""
    if client.available:
        messages = build_analysis_prompt(text, heuristic_result)
        llm_explanation = client.chat(messages, system=SYSTEM_PROMPT)
        heuristic_result.source = "combined"
        heuristic_result.reasoning = llm_explanation
    else:
        heuristic_result.source = "heuristic"

    return heuristic_result, llm_explanation


def advise_password(
    raw_password: str,
    client: LLMClient,
) -> tuple[PasswordResult, str]:
    """Evaluate *raw_password* strength; returns (PasswordResult, llm_advice).

    The local analysis always runs.  If the LLM is available it adds personalised
    natural-language coaching.  The real password is never sent to the LLM —
    only a masked version is included.
    """
    password = sanitize_password_input(raw_password)
    result = evaluate_password(password)

    llm_advice = ""
    if client.available:
        masked = "*" * min(len(password), 8) + f" ({len(password)} chars)"
        messages = build_password_prompt(masked, result)
        llm_advice = client.chat(messages, system=SYSTEM_PROMPT)

    return result, llm_advice


def generate_strong_password() -> tuple[str, PasswordResult]:
    """Generate a strong password and evaluate it; returns (password, result)."""
    pwd = generate_password()
    result = evaluate_password(pwd)
    return pwd, result


def chat(
    user_message: str,
    history: ChatHistory,
    client: LLMClient,
) -> str:
    """Send *user_message* to the chatbot; returns the assistant reply string."""
    text = sanitize_input(user_message)
    messages = build_chat_prompt(text, history.messages())
    reply = client.chat(messages, system=SYSTEM_PROMPT)
    history.add("user", text)
    history.add("assistant", reply)
    return reply


def stream_chat(
    user_message: str,
    history: ChatHistory,
    client: LLMClient,
):
    """Yield reply chunks for *user_message*; caller must add both turns to history.

    Yields str chunks as they arrive from the LLM stream.  ``build_chat_prompt``
    already appends the current user message internally, so this function does
    NOT mutate *history* — the caller must call ``history.add("user", ...)``
    and ``history.add("assistant", ...)`` after collecting all chunks.
    """
    text = sanitize_input(user_message)
    messages = build_chat_prompt(text, history.messages())
    yield from client.stream(messages, system=SYSTEM_PROMPT)


def stream_analysis_explanation(
    raw_text: str,
    client: LLMClient,
):
    """Yield LLM deep-analysis chunks for *raw_text* (phishing analysis).

    Yields str chunks.  The heuristic analysis must already have been run
    separately; this function only produces the streaming LLM narrative.
    """
    from cybersec.heuristics import analyze_text as heuristic_analyze  # local to avoid circular
    text = sanitize_input(raw_text)
    heuristic_result = heuristic_analyze(text)
    messages = build_analysis_prompt(text, heuristic_result)
    yield from client.stream(messages, system=SYSTEM_PROMPT)


def stream_password_advice(
    raw_password: str,
    result: "PasswordResult",  # type: ignore[name-defined]
    client: LLMClient,
):
    """Yield LLM password-advice chunks for the already-evaluated *result*.

    Yields str chunks.  The local evaluation (``advise_password``) must
    have already been called; this function only streams the LLM coaching.
    """
    from cybersec.sanitizer import sanitize_password_input  # local import to keep function slim
    password = sanitize_password_input(raw_password)
    masked = "*" * min(len(password), 8) + f" ({len(password)} chars)"
    messages = build_password_prompt(masked, result)
    yield from client.stream(messages, system=SYSTEM_PROMPT)
