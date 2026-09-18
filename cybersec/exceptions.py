"""Custom exceptions for the AI Cybersecurity Guide & Analyzer."""

from __future__ import annotations


class CyberSecError(Exception):
    """Base exception for all cybersec package errors."""


class InvalidInputError(CyberSecError, ValueError):
    """Raised when user input fails validation (empty, too long, etc.)."""


class AnalysisError(CyberSecError):
    """Raised when analysis fails unexpectedly."""


class KnowledgeBaseError(CyberSecError):
    """Raised when the knowledge base cannot be loaded or queried."""


class LLMError(CyberSecError):
    """Raised when an LLM API call fails after all retries."""
