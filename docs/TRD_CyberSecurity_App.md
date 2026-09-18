# Technical Requirements Document (TRD)
## AI Cybersecurity Guide & Analyzer
**Version:** 1.0

---

## 1. Technology Stack

| Layer | Technology | Version | Rationale |
|-------|-----------|---------|-----------|
| Frontend/UI | Streamlit | ≥ 1.35 | Rapid Python UI, zero JS required |
| Data display | Pandas | ≥ 2.2 | DataFrames for tables and charts |
| AI/LLM | Anthropic Claude | ≥ 0.25 (optional) | State-of-the-art reasoning, safe |
| Language | Python | 3.11+ | Type hints, modern stdlib |
| Testing | Pytest | ≥ 8.0 | Standard Python test framework |

---

## 2. Module Architecture

```
cybersecurity_app.py              ← Streamlit entry point (UI only)
│
├── cybersec/
│   ├── __init__.py
│   ├── config.py                 ← Constants, env-var loading
│   ├── exceptions.py             ← Custom exception hierarchy
│   ├── models.py                 ← AnalysisResult, PasswordResult, ChatMessage
│   ├── heuristics.py             ← Rule-based phishing/risk detection engine
│   ├── password_engine.py        ← Entropy calc, strength scoring, generation
│   ├── knowledge_base.py         ← Glossary loader, tip selector, threat cards
│   ├── prompt_builder.py         ← Assembles LLM prompts from parts
│   ├── llm_client.py             ← Anthropic wrapper + stub fallback
│   ├── chat_history.py           ← In-memory session chat state
│   ├── analyzer.py               ← Orchestrates heuristics + LLM for analysis
│   └── sanitizer.py              ← Input cleaning and validation
│
├── data/
│   ├── knowledge_base.json       ← 50+ glossary entries + tips + threat cards
│   └── common_passwords.txt      ← Top-1000 most common passwords
│
└── tests/
    ├── test_heuristics.py
    ├── test_password_engine.py
    ├── test_knowledge_base.py
    ├── test_prompt_builder.py
    ├── test_sanitizer.py
    └── test_models.py
```

---

## 3. Data Models

### 3.1 AnalysisResult

```python
@dataclass
class AnalysisResult:
    risk_score: int          # 0–100
    severity: str            # "safe" | "low" | "medium" | "high" | "critical"
    indicators: list[str]    # specific red flags found
    explanation: str         # plain-language explanation
    advice: str              # actionable recommendation
    reasoning: str           # step-by-step CoT trace (may be empty)
    source: str              # "heuristic" | "llm" | "combined"
```

### 3.2 PasswordResult

```python
@dataclass
class PasswordResult:
    score: int               # 0–100
    label: str               # "Weak" | "Fair" | "Good" | "Strong" | "Very Strong"
    entropy_bits: float      # calculated entropy
    crack_time: str          # human-readable estimate
    weaknesses: list[str]    # specific problems found
    suggestions: list[str]   # improvement tips
    generated: str | None    # generated alternative (if requested)
```

### 3.3 ChatMessage

```python
@dataclass
class ChatMessage:
    role: str       # "user" | "assistant" | "system"
    content: str
    timestamp: datetime
    feedback: str | None   # "positive" | "negative" | None
```

---

## 4. Module Specifications

### 4.1 `cybersec/heuristics.py`

**Purpose:** Rule-based risk analysis engine. Runs entirely offline, no API required.

**Key functions:**
```python
def analyze_text(text: str) -> AnalysisResult
    """Run all heuristic checks and return a scored result."""

def _check_urgency_language(text: str) -> list[str]
    """Detect urgency phrases: 'act now', 'account suspended', 'verify immediately'."""

def _check_url_patterns(text: str) -> list[str]
    """Detect: IP addresses as URLs, misspelled domains, URL shorteners, HTTP (not HTTPS)."""

def _check_impersonation(text: str) -> list[str]
    """Detect impersonation of banks, social platforms, e-commerce brands."""

def _check_credential_requests(text: str) -> list[str]
    """Detect requests for passwords, SSNs, credit card numbers, OTPs."""

def _check_suspicious_attachments(text: str) -> list[str]
    """Detect references to .exe, .zip, .docm attachments."""

def _score_indicators(indicators: list[tuple[str, int]]) -> int
    """Weight and clamp indicator scores to 0–100."""
```

**Scoring weights:**
| Indicator Category | Weight |
|-------------------|--------|
| Credential request | +35 |
| Domain spoofing | +30 |
| Urgency language | +20 |
| Suspicious URL | +20 |
| Impersonation | +25 |
| Attachment threat | +25 |
| HTTP (not HTTPS) link | +10 |
| Generic greeting | +5 |

### 4.2 `cybersec/password_engine.py`

**Purpose:** Local password strength analysis and generation.

**Key functions:**
```python
def evaluate_password(password: str) -> PasswordResult
    """Run full strength evaluation pipeline."""

def _calculate_entropy(password: str) -> float
    """Compute Shannon entropy: len × log2(pool_size)."""

def _estimate_crack_time(entropy_bits: float) -> str
    """Map entropy to human-readable crack time at 1B guesses/sec."""

def _check_common_passwords(password: str) -> bool
    """Check against top-1000 common password list."""

def _check_patterns(password: str) -> list[str]
    """Detect keyboard walks, repeated chars, sequential numbers."""

def generate_password(length: int = 20) -> str
    """Generate a strong passphrase: 4 words + numbers + symbols."""

def _score_to_label(score: int) -> str
    """Map 0-19→Weak, 20-39→Fair, 40-59→Good, 60-79→Strong, 80+→Very Strong."""
```

### 4.3 `cybersec/knowledge_base.py`

**Purpose:** Offline knowledge store for glossary, tips, and threat cards.

**Key functions:**
```python
def load_knowledge_base(path: str) -> dict
    """Load and parse knowledge_base.json."""

def get_glossary_entry(term: str) -> dict | None
    """Return definition, examples, and related terms for a security term."""

def get_daily_tip(session_id: str) -> str
    """Return a deterministic daily tip (based on date hash)."""

def get_threat_card(threat_type: str) -> dict | None
    """Return a quick-reference card for a threat category."""

def search_knowledge_base(query: str) -> list[dict]
    """Fuzzy-search glossary by keyword."""
```

### 4.4 `cybersec/prompt_builder.py`

**Purpose:** Assemble structured LLM prompts from components.

**Key functions:**
```python
SYSTEM_PROMPT: str   # Core CyberGuard persona, safety rules, CoT instruction

FEW_SHOTS: dict[str, str]   # Per-intent examples (phishing, explain, password, behavior)

def build_analysis_prompt(text: str, heuristic_result: AnalysisResult) -> list[dict]
    """Build phishing-analysis prompt, injecting heuristic pre-findings."""

def build_chat_prompt(user_message: str, history: list[ChatMessage]) -> list[dict]
    """Build conversational prompt with history context."""

def build_password_prompt(password_masked: str, result: PasswordResult) -> list[dict]
    """Build password-advice prompt with local analysis pre-loaded."""
```

### 4.5 `cybersec/sanitizer.py`

**Purpose:** Prevent injection attacks and enforce input limits.

**Key functions:**
```python
def sanitize_input(text: str, max_length: int = 10_000) -> str
    """Strip dangerous characters, truncate, normalise whitespace."""

def is_valid_input(text: str) -> tuple[bool, str]
    """Return (is_valid, error_message)."""

def mask_sensitive_data(text: str) -> str
    """Replace password-like patterns with [REDACTED] before logging."""
```

---

## 5. API Contract

### 5.1 `LLMClient.chat(messages, system) -> str`
- Input: `messages: list[dict[str, str]]`, `system: str`
- Output: response text string
- Raises: never (all errors caught internally, stub response returned)
- Side effects: none (stateless)

### 5.2 `HeuristicEngine.analyze_text(text) -> AnalysisResult`
- Input: sanitised text string
- Output: `AnalysisResult` dataclass
- Performance: < 200 ms guaranteed
- Side effects: none

### 5.3 `PasswordEngine.evaluate_password(password) -> PasswordResult`
- Input: raw password string
- Output: `PasswordResult` dataclass
- Performance: < 50 ms
- Side effects: none (password never logged or stored)

---

## 6. Security Requirements (Implementation Level)

| Requirement | Implementation |
|-------------|---------------|
| No password storage | Password only in local variable; never in session_state, never in log |
| Input sanitisation | `sanitizer.sanitize_input()` called on ALL user inputs before processing |
| Prompt injection prevention | System prompt includes explicit anti-injection instructions; input treated as data not instruction |
| XSS prevention | Streamlit auto-escapes; no `unsafe_allow_html=True` anywhere |
| API key protection | Read from env var; never displayed; never logged |
| Output length limits | Max 1024 tokens from LLM; truncate if exceeded |

---

## 7. Knowledge Base Schema (`data/knowledge_base.json`)

```json
{
  "version": "1.0",
  "glossary": [
    {
      "term": "Phishing",
      "definition": "A fraudulent attempt to obtain sensitive information...",
      "analogy": "Like a fisherman casting bait...",
      "examples": ["Fake bank emails", "SMS OTP scams"],
      "related": ["Spear Phishing", "Smishing", "Vishing"],
      "severity": "high"
    }
  ],
  "tips": [
    {
      "id": "tip_001",
      "category": "passwords",
      "text": "Use a unique password for every account...",
      "action": "Enable your password manager today"
    }
  ],
  "threat_cards": [
    {
      "type": "ransomware",
      "title": "Ransomware",
      "description": "Malware that encrypts your files...",
      "warning_signs": ["Slow computer", "Unusual file extensions"],
      "prevention": ["Regular backups", "Avoid suspicious attachments"],
      "if_infected": ["Disconnect from internet", "Do not pay ransom"]
    }
  ],
  "behavior_nudges": [
    "Enable 2FA on your most important accounts today — it takes under 2 minutes.",
    "Check if your email has been in a data breach at haveibeenpwned.com",
    "Lock your screen every time you walk away from your computer."
  ]
}
```

---

## 8. Test Requirements

| Test File | Coverage Target | Key Scenarios |
|-----------|----------------|---------------|
| `test_heuristics.py` | ≥ 90% | Known phishing samples → correct score; benign text → score < 25 |
| `test_password_engine.py` | ≥ 90% | Common password → Weak; 20-char random → Very Strong; entropy math |
| `test_knowledge_base.py` | ≥ 85% | Term lookup hit/miss; tip rotation; search |
| `test_prompt_builder.py` | ≥ 85% | Prompt structure, history injection, fewshot presence |
| `test_sanitizer.py` | ≥ 95% | Length truncation, injection patterns, empty input |
| `test_models.py` | ≥ 90% | Dataclass construction, invalid field rejection |

---

## 9. Performance Targets

| Operation | Target | Measured |
|-----------|--------|---------|
| App startup (cold) | < 3 s | TBD |
| Heuristic analysis | < 200 ms | < 50 ms expected |
| Password scoring | < 50 ms | < 10 ms expected |
| LLM response (Claude Haiku) | < 5 s | ~2 s average |
| Knowledge base lookup | < 10 ms | < 1 ms expected |

---

## 10. Deployment

```bash
# Minimum viable run
pip install streamlit pandas
streamlit run cybersecurity_app.py

# Full AI features
pip install streamlit pandas anthropic
export ANTHROPIC_API_KEY=your_key_here
streamlit run cybersecurity_app.py

# Run tests
pip install pytest
pytest tests/ -q
```
