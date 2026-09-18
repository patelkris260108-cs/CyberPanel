"""In-memory chat history for the cybersecurity chatbot session."""

from __future__ import annotations

import datetime

from cybersec.models import ChatMessage


class ChatHistory:
    """Stores ChatMessage objects for the current session (never persisted)."""

    def __init__(self) -> None:
        """Initialise an empty message list."""
        self._messages: list[ChatMessage] = []

    def add(self, role: str, content: str) -> None:
        """Append a new ChatMessage with the given *role* and *content*."""
        self._messages.append(
            ChatMessage(role=role, content=content, timestamp=datetime.datetime.now())
        )

    def messages(self) -> list[ChatMessage]:
        """Return a copy of all messages in chronological order."""
        return list(self._messages)

    def last_n(self, n: int) -> list[ChatMessage]:
        """Return the last *n* messages; returns empty list when n <= 0."""
        if n <= 0:
            return []
        return list(self._messages[-n:])

    def clear(self) -> None:
        """Remove all messages from history."""
        self._messages.clear()

    def set_feedback(self, index: int, feedback: str) -> None:
        """Set feedback on a message by index; silently ignores out-of-range index."""
        if 0 <= index < len(self._messages):
            self._messages[index].feedback = feedback

    def __len__(self) -> int:
        """Return the total number of messages stored."""
        return len(self._messages)
