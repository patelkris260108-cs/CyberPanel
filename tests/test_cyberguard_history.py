"""Tests for cyberguard.chat_history.ChatHistory."""

from __future__ import annotations

from cyberguard.chat_history import ChatHistory


class TestChatHistory:
    def test_new_history_is_empty(self) -> None:
        h = ChatHistory()
        assert len(h) == 0
        assert h.messages() == []

    def test_add_user_message(self) -> None:
        h = ChatHistory()
        h.add("user", "Hello")
        assert len(h) == 1
        assert h.messages()[0]["role"] == "user"
        assert h.messages()[0]["content"] == "Hello"

    def test_add_assistant_message(self) -> None:
        h = ChatHistory()
        h.add("assistant", "Hi there!")
        msg = h.messages()[0]
        assert msg["role"] == "assistant"

    def test_messages_returns_copy(self) -> None:
        h = ChatHistory()
        h.add("user", "Test")
        copy = h.messages()
        copy.clear()
        assert len(h) == 1  # original unaffected

    def test_last_n_returns_correct_slice(self) -> None:
        h = ChatHistory()
        for i in range(5):
            h.add("user", f"msg {i}")
        last = h.last_n(3)
        assert len(last) == 3
        assert last[-1]["content"] == "msg 4"

    def test_last_n_larger_than_history_returns_all(self) -> None:
        h = ChatHistory()
        h.add("user", "only one")
        assert len(h.last_n(100)) == 1

    def test_last_n_zero_returns_empty(self) -> None:
        h = ChatHistory()
        h.add("user", "msg")
        assert h.last_n(0) == []

    def test_clear_empties_history(self) -> None:
        h = ChatHistory()
        h.add("user", "msg 1")
        h.add("assistant", "reply 1")
        h.clear()
        assert len(h) == 0
        assert h.messages() == []

    def test_messages_order_preserved(self) -> None:
        h = ChatHistory()
        turns = [("user", "hi"), ("assistant", "hello"), ("user", "bye")]
        for role, content in turns:
            h.add(role, content)
        msgs = h.messages()
        for i, (role, content) in enumerate(turns):
            assert msgs[i]["role"] == role
            assert msgs[i]["content"] == content

    def test_add_multiple_messages(self) -> None:
        h = ChatHistory()
        for i in range(20):
            h.add("user" if i % 2 == 0 else "assistant", f"msg {i}")
        assert len(h) == 20
