"""Analyzer functions that assemble prompts and call the LLM for CyberGuard capabilities."""

from __future__ import annotations

from cyberguard.chat_history import ChatHistory
from cyberguard.llm_client import LLMClient
from cyberguard.prompts import COT_TRIGGER, FEW_SHOTS, SYSTEM_PROMPT


def _build_messages(
    intent: str,
    user_input: str,
    history: ChatHistory,
    *,
    use_cot: bool = False,
) -> list[dict[str, str]]:
    """Assemble the messages list: few-shot preamble + conversation history + new user turn."""
    few_shot_text = FEW_SHOTS.get(intent, "")
    user_turn = user_input
    if few_shot_text:
        # Prepend the few-shot block as the first user message if history is empty.
        if len(history) == 0:
            user_turn = f"{few_shot_text}\n\nNow answer the following:\n{user_input}"
    if use_cot:
        user_turn += COT_TRIGGER
    messages = history.last_n(10)  # keep context window manageable
    messages.append({"role": "user", "content": user_turn})
    return messages


def analyze_phishing(
    text: str,
    client: LLMClient,
    history: ChatHistory,
) -> str:
    """Analyse *text* for phishing indicators and return a risk assessment."""
    messages = _build_messages("phishing", text, history, use_cot=True)
    response = client.chat(messages, system=SYSTEM_PROMPT)
    history.add("user", text)
    history.add("assistant", response)
    return response


def explain_concept(
    term: str,
    client: LLMClient,
    history: ChatHistory,
) -> str:
    """Return a plain-language explanation of the security *term* or scenario."""
    messages = _build_messages("explainer", term, history)
    response = client.chat(messages, system=SYSTEM_PROMPT)
    history.add("user", term)
    history.add("assistant", response)
    return response


def advise_password(
    password: str,
    client: LLMClient,
    history: ChatHistory,
) -> str:
    """Evaluate *password* strength and return improvement suggestions."""
    # Mask the password in the history so it is never stored in plain text.
    display_text = f"Please evaluate this password: {'*' * len(password)}"
    prompt = (
        f"Please evaluate the following password and give detailed feedback on length, "
        f"complexity, common patterns, and suggest improvements. "
        f"Password: {password}"
    )
    messages = _build_messages("password", prompt, history, use_cot=True)
    response = client.chat(messages, system=SYSTEM_PROMPT)
    # Store masked version – never log the real password.
    history.add("user", display_text)
    history.add("assistant", response)
    return response


def behavior_nudge(
    client: LLMClient,
    history: ChatHistory,
) -> str:
    """Generate a short, friendly security behaviour nudge."""
    prompt = (
        "Give me one short, friendly, and actionable cybersecurity tip I can act on "
        "right now. Keep it under three sentences."
    )
    messages = _build_messages("behavior", prompt, history)
    response = client.chat(messages, system=SYSTEM_PROMPT)
    history.add("user", "[Requested a security nudge]")
    history.add("assistant", response)
    return response
