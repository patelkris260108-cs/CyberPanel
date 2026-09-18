"""LLM client wrapper for CyberGuard — NVIDIA NIM with STREAMING for instant responses."""

from __future__ import annotations

import logging

from cyberguard.config import MAX_TOKENS, MODEL_NAME, NVIDIA_API_KEY, NVIDIA_BASE_URL

logger = logging.getLogger(__name__)

_STUB_RESPONSE = (
    "⚠️ **CyberGuard is running in demo mode** (no NVIDIA API key configured).\n\n"
    "To enable real AI responses, set the `NVIDIA_API_KEY` environment variable "
    "before launching the app.\n\n"
    "Get a free API key at https://build.nvidia.com/"
)


class LLMClient:
    """NVIDIA NIM wrapper with streaming support for fast word-by-word responses."""

    def __init__(self) -> None:
        """Initialise; detects whether the openai SDK and NVIDIA API key are available."""
        self._available = False
        if not NVIDIA_API_KEY:
            logger.info("NVIDIA_API_KEY not set — CyberGuard running in stub/demo mode.")
            return
        try:
            from openai import OpenAI  # type: ignore[import-untyped]
            import httpx

            self._client = OpenAI(
                base_url=NVIDIA_BASE_URL,
                api_key=NVIDIA_API_KEY,
                timeout=httpx.Timeout(120.0, connect=10.0),
            )
            self._available = True
            logger.info("NVIDIA NIM client ready (model: %s).", MODEL_NAME)
        except ImportError:
            logger.warning(
                "openai package not installed. Running in stub mode. "
                "Install with: pip install openai"
            )

    @property
    def available(self) -> bool:
        """Return True when connected to a live LLM API."""
        return self._available

    def chat(
        self,
        messages: list[dict[str, str]],
        system: str = "",
    ) -> str:
        """Send *messages* to NVIDIA NIM and return the full assistant reply as a string."""
        if not self._available:
            return _STUB_RESPONSE

        full_messages: list[dict[str, str]] = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        try:
            response = self._client.chat.completions.create(
                model=MODEL_NAME,
                messages=full_messages,  # type: ignore[arg-type]
                max_tokens=MAX_TOKENS,
                temperature=0.6,
                top_p=0.7,
                stream=False,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:  # noqa: BLE001
            logger.error("NVIDIA NIM call failed: %s", exc)
            return (
                "⚠️ I couldn't reach the AI service right now. "
                "Please try again in a moment."
            )

    def stream(
        self,
        messages: list[dict[str, str]],
        system: str = "",
    ):
        """Yield text chunks from the LLM as they arrive (generator).

        Usage in Streamlit:
            with st.empty():
                full = ""
                for chunk in client.stream(messages, system):
                    full += chunk
                    st.markdown(full + "▌")
                st.markdown(full)
        """
        if not self._available:
            yield _STUB_RESPONSE
            return

        full_messages: list[dict[str, str]] = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        try:
            with self._client.chat.completions.create(
                model=MODEL_NAME,
                messages=full_messages,  # type: ignore[arg-type]
                max_tokens=MAX_TOKENS,
                temperature=0.6,
                top_p=0.7,
                stream=True,
            ) as stream_response:
                for chunk in stream_response:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
        except Exception as exc:  # noqa: BLE001
            logger.error("NVIDIA NIM stream failed: %s", exc)
            yield (
                "\n\n⚠️ Stream interrupted. Please try again."
            )
