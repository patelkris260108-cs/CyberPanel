"""In-memory chat history for the CyberGuard session."""

from __future__ import annotations


class ChatHistory:
    """Stores a list of chat messages for the current session (not persisted)."""

    def __init__(self) -> None:
        """Initialise an empty message list."""
        self._messages: list[dict[str, str]] = []

    def add(self, role: str, content: str) -> None:
        """Append a message with the given *role* ('user' or 'assistant') and *content*."""
        self._messages.append({"role": role, "content": content})

    def messages(self) -> list[dict[str, str]]:
        """Return a copy of all messages in chronological order."""
        return list(self._messages)

    def last_n(self, n: int) -> list[dict[str, str]]:
        """Return the last *n* messages; returns empty list when n is 0."""
        if n <= 0:
            return []
        return list(self._messages[-n:])

    def clear(self) -> None:
        """Remove all messages from history."""
        self._messages.clear()

    def __len__(self) -> int:
        """Return the number of messages stored."""
        return len(self._messages)
