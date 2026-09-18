"""LLM client wrapper — NVIDIA NIM (OpenAI-compatible) with graceful offline stub fallback."""

from __future__ import annotations

import logging

from cybersec.config import LLM_MAX_TOKENS, LLM_MODEL, NVIDIA_API_KEY, NVIDIA_BASE_URL

logger = logging.getLogger(__name__)

_STUB_MESSAGE = (
    "🤖 **CyberGuard AI is running in offline / demo mode.**\n\n"
    "The heuristic analysis above is based on built-in security rules and "
    "runs entirely on your device without any API key.\n\n"
    "To unlock AI-powered natural-language explanations and deeper analysis, "
    "set the `NVIDIA_API_KEY` environment variable before launching the app.\n\n"
    "👉 Get a free API key at **https://build.nvidia.com/**"
)


class LLMClient:
    """NVIDIA NIM wrapper (OpenAI-compatible SDK) with a graceful offline stub mode."""

    def __init__(self) -> None:
        """Initialise; detects whether the openai SDK and NVIDIA API key are available."""
        self._available = False
        if not NVIDIA_API_KEY:
            logger.info("NVIDIA_API_KEY not set — running in offline/stub mode.")
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
            logger.info(
                "NVIDIA NIM client initialised (model: %s, base_url: %s).",
                LLM_MODEL,
                NVIDIA_BASE_URL,
            )
        except ImportError:
            logger.warning(
                "openai package not installed. Running in offline mode. "
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
        """Send *messages* to NVIDIA NIM; returns a stub string if unavailable."""
        if not self._available:
            return _STUB_MESSAGE

        full_messages: list[dict[str, str]] = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        try:
            response = self._client.chat.completions.create(
                model=LLM_MODEL,
                messages=full_messages,  # type: ignore[arg-type]
                max_tokens=LLM_MAX_TOKENS,
                temperature=0.6,
                top_p=0.7,
                stream=False,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:  # noqa: BLE001
            logger.error("NVIDIA NIM call failed: %s", exc)
            return (
                "⚠️ I couldn't reach the AI service right now. "
                "The heuristic analysis is still available above. "
                "Please try again in a moment."
            )

    def stream(
        self,
        messages: list[dict[str, str]],
        system: str = "",
    ):
        """Yield text chunks as they arrive — word-by-word streaming for instant feel."""
        if not self._available:
            yield _STUB_MESSAGE
            return

        full_messages: list[dict[str, str]] = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)

        try:
            with self._client.chat.completions.create(
                model=LLM_MODEL,
                messages=full_messages,  # type: ignore[arg-type]
                max_tokens=LLM_MAX_TOKENS,
                temperature=0.6,
                top_p=0.7,
                stream=True,
            ) as resp:
                for chunk in resp:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        yield delta
        except Exception as exc:  # noqa: BLE001
            logger.error("NVIDIA NIM stream failed: %s", exc)
            yield "\n\n⚠️ Stream interrupted. Please try again."
