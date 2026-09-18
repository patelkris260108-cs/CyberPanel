# Personal Budget Planner + CyberGuard — Implementation Plan

## Top-Level Overview

**Goal:** Generate a single, ready-to-run multi-page Streamlit workspace containing:
1. **Personal Budget Planner** — set a monthly budget, record expenses, view totals/charts.
2. **CyberGuard** — AI-powered cybersecurity awareness assistant (phishing analysis,
   security explainer, password advisor, behavior coach).

**Streamlit Multi-Page Layout:**
```
streamlit_app.py          ← landing / home page
pages/
  1_Budget_Planner.py     ← Budget Planner full UI
  2_CyberGuard.py         ← CyberGuard chatbot UI
```

**Scope:**
- `budget_planner/` Python package — pure-Python business logic (models, storage,
  calculations, validators, exceptions).
- `cyberguard/` Python package — prompt engineering, chat history management,
  phishing/password/explainer/behavior modules, optional RAG stub.
- `pages/` — Streamlit page files wired to the two packages.
- `tests/` — pytest suites for both packages (no Streamlit imports).
- Supporting files: `requirements.txt`, `README.md`, `.gitignore`.

**Key Constraints:**
- Budget Planner: no external deps beyond `streamlit`, `pandas`, `pytest`.
- CyberGuard: uses an LLM API (configurable via environment variable `ANTHROPIC_API_KEY`
  or `OPENAI_API_KEY`); falls back to a mock/stub if no key is set (for offline testing).
- All business-logic modules carry type hints and one-sentence docstrings.
- Business logic has zero Streamlit imports.

---

## Sub-Task 1 — `budget_planner/exceptions.py` + `__init__.py`

**Intent:** Define the Budget Planner custom exception hierarchy.

**Expected Outcomes:**
- `budget_planner/__init__.py` exists (empty package marker).
- `budget_planner/exceptions.py` with `InvalidBudgetError(ValueError)`,
  `InvalidExpenseError(ValueError)`, `StorageError(Exception)`.

**Todo List:**
1. Create `budget_planner/__init__.py` (empty).
2. Create `budget_planner/exceptions.py` with the three exception classes,
   each with a one-sentence docstring.

**Relevant Context:**
- PRD section 2.8 specifies class names and base types.
- Imported by every other `budget_planner` module.

**Status:** [ ] pending

---

## Sub-Task 2 — `budget_planner/validators.py`

**Intent:** Centralise all Budget Planner input validation.

**Expected Outcomes:**
- `ALLOWED_CATEGORIES: list[str] = ["Food", "Travel", "Shopping", "Education"]` exported.
- Four validator functions with type hints, docstrings, and exact error messages from PRD 2.7.

**Todo List:**
1. Create `budget_planner/validators.py`.
2. Define `ALLOWED_CATEGORIES`.
3. Implement `validate_positive_amount`, `validate_date`, `validate_category`,
   `validate_description`.

**Relevant Context:**
- Error messages verbatim from PRD 2.7.
- `ALLOWED_CATEGORIES` is also imported by `pages/1_Budget_Planner.py`.

**Status:** [ ] pending

---

## Sub-Task 3 — `budget_planner/models.py`

**Intent:** Define `Expense` and `BudgetPlan` data classes.

**Expected Outcomes:**
- `Expense` with `__init__`, `to_dict`, `from_dict` (classmethod).
- `BudgetPlan` with `__init__`, `add_expense`, `total_expenses`, `remaining_budget`,
  `category_totals`.

**Todo List:**
1. Create `budget_planner/models.py`.
2. Implement `Expense` — delegates validation to `validators.py`; `to_dict` uses ISO date.
3. Implement `BudgetPlan` — validates `monthly_budget >= 0`.

**Relevant Context:**
- PRD 2.5 / 2.6 specifies all fields and method signatures.
- `to_dict` key names must match CSV header (`date,amount,category,description`).

**Status:** [ ] pending

---

## Sub-Task 4 — `budget_planner/storage.py`

**Intent:** Isolate all CSV I/O for the Budget Planner.

**Expected Outcomes:**
- `load_expenses(path) -> list[Expense]` — missing file returns `[]`; malformed rows skipped.
- `save_expenses(expenses, path) -> None` — creates parent dir, writes UTF-8 CSV with header.

**Todo List:**
1. Create `budget_planner/storage.py`.
2. Implement `load_expenses` using `csv.DictReader`; wrap row parse in try/except.
3. Implement `save_expenses` using `csv.DictWriter`; call `os.makedirs`.

**Relevant Context:**
- PRD 4.8 describes exact behavior.
- BR6: ISO 8601 dates; BR7: create file if missing on first save.

**Status:** [ ] pending

---

## Sub-Task 5 — `budget_planner/calculations.py`

**Intent:** Thin pure-function aggregation layer for the Budget Planner.

**Expected Outcomes:**
- `total_expenses`, `remaining_budget`, `category_totals` — all pure functions, typed, docstrings.

**Todo List:**
1. Create `budget_planner/calculations.py`.
2. Implement the three functions.

**Relevant Context:**
- `category_totals` output feeds `st.bar_chart` — keys are category strings.

**Status:** [ ] pending

---

## Sub-Task 6 — `cyberguard/` package

**Intent:** Build the CyberGuard business-logic package — prompt templates, chat history,
LLM client wrapper, and the four capability modules — all with zero Streamlit imports.

**Expected Outcomes:**
- `cyberguard/__init__.py` (empty).
- `cyberguard/config.py` — `LLM_PROVIDER`, `API_KEY`, `MODEL_NAME` read from env vars;
  `MAX_DESCRIPTION_LEN`, `SYSTEM_PROMPT` constant.
- `cyberguard/prompts.py` — `SYSTEM_PROMPT` string and `FEW_SHOTS` dict
  (`phishing`, `explainer`, `password`, `behavior`) containing the few-shot example strings
  from the Prompt Engineering Guide.
- `cyberguard/llm_client.py` — `LLMClient` class:
  - `__init__` reads `API_KEY` from env; sets `_available: bool`.
  - `chat(messages: list[dict]) -> str` — calls LLM API if available,
    returns a stub "LLM not configured" message otherwise.
  - Supports Anthropic Claude via `anthropic` SDK (optional dep) or falls back gracefully.
- `cyberguard/chat_history.py` — `ChatHistory` class:
  - `add(role, content)`, `messages() -> list[dict]`, `clear()`, `last_n(n) -> list[dict]`.
  - Stored as a plain list in memory (session-scoped; no persistence for privacy — NFR2).
- `cyberguard/analyzer.py` — `analyze_phishing(text, client, history) -> str`,
  `explain_concept(term, client, history) -> str`,
  `advise_password(password, client, history) -> str`,
  `behavior_nudge(client, history) -> str`.
  Each function assembles `system + few-shots + history + user turn`, calls `client.chat()`,
  appends response to history, returns response string.

**Todo List:**
1. Create `cyberguard/__init__.py`.
2. Create `cyberguard/config.py` with env-var reading and constants.
3. Create `cyberguard/prompts.py` with `SYSTEM_PROMPT` and `FEW_SHOTS` dict
   (populate with the verbatim examples from the Prompt Engineering Guide).
4. Create `cyberguard/llm_client.py` with `LLMClient`.
5. Create `cyberguard/chat_history.py` with `ChatHistory`.
6. Create `cyberguard/analyzer.py` with the four analyzer functions.

**Relevant Context:**
- PRD (CyberGuard) FR1-FR5 map to the four analyzer functions + chat history.
- Prompt Engineering Guide sections 2-6 provide system message, few-shots, CoT triggers,
  and safety guardrails verbatim.
- NFR2: no personal data stored beyond session — `ChatHistory` is in-memory only.
- If `anthropic` package not installed, `LLMClient.chat()` returns a graceful stub message
  so the UI still renders without crashing.

**Status:** [ ] pending

---

## Sub-Task 7 — `streamlit_app.py` (home page) + `pages/1_Budget_Planner.py`

**Intent:** Build the home/landing page and the Budget Planner Streamlit page.

**Expected Outcomes:**
- `streamlit_app.py` — simple landing page with app title, brief description of both tools,
  and navigation hints.
- `pages/1_Budget_Planner.py` — full Budget Planner UI matching PRD 4.6 layout:
  - Sidebar: monthly budget input + Save Budget button.
  - Main: expense entry form (category, amount, description, date).
  - Summary: Total Spent metric, Remaining Budget metric, category bar chart, expenses dataframe.
  - Footer: CSV location note.

**Todo List:**
1. Create `streamlit_app.py` with title and two-column intro cards for Budget Planner
   and CyberGuard.
2. Create `pages/` directory.
3. Create `pages/1_Budget_Planner.py`:
   - Session state init (load CSV, init BudgetPlan).
   - Sidebar budget section.
   - Expense form with try/except error handling per PRD 4.7.
   - Summary section using `calculations.*`.
   - Footer note.

**Relevant Context:**
- Streamlit multi-page: pages listed alphabetically by filename in the sidebar;
  prefix number ensures correct order.
- `DATA_PATH = Path("data/expenses.csv")` defined at module level.
- `ALLOWED_CATEGORIES` imported from `budget_planner.validators`.

**Status:** [ ] pending

---

## Sub-Task 8 — `pages/2_CyberGuard.py`

**Intent:** Build the CyberGuard Streamlit page — a chat interface with tab-based
capability switcher and session-scoped chat history.

**Expected Outcomes:**
- `pages/2_CyberGuard.py` with:
  - API key status banner (sidebar): green if key found, amber warning if missing
    (stub mode note).
  - Four tabs: "💬 Chat", "🎣 Phishing Analyzer", "🔑 Password Advisor",
    "🛡️ Security Explainer".
  - **Chat tab:** scrolling chat history display, text input, Send button;
    routes free-form queries to `analyzer.explain_concept` by default.
  - **Phishing Analyzer tab:** text area for pasting suspicious message,
    "Analyze" button → calls `analyze_phishing`; displays risk assessment with CoT.
  - **Password Advisor tab:** text input (masked) for password,
    "Evaluate" button → calls `advise_password`; shows strength feedback + suggestions.
  - **Security Explainer tab:** text input for term/scenario,
    "Explain" button → calls `explain_concept`; shows jargon-free explanation.
  - 👍/👎 feedback buttons after each response (FR6) — logged to session state.
  - "Clear Chat" button to reset history.

**Todo List:**
1. Create `pages/2_CyberGuard.py`.
2. Implement session state init: `ChatHistory`, `LLMClient`, feedback log list.
3. Implement sidebar API key status.
4. Implement four-tab layout using `st.tabs`.
5. Implement Chat tab with chat bubble display and input.
6. Implement Phishing Analyzer tab.
7. Implement Password Advisor tab.
8. Implement Security Explainer tab.
9. Add thumbs-up/thumbs-down feedback buttons per response.
10. Add Clear Chat button.

**Relevant Context:**
- PRD CyberGuard FR1-FR6 map to tabs + feedback.
- NFR4: WCAG 2.1 AA — use descriptive labels, sufficient contrast; avoid color-only indicators.
- NFR5: CoT reasoning — analyzer functions include "think step by step" trigger;
  response will contain reasoning before conclusion.
- Safety guardrails included in `SYSTEM_PROMPT` from `cyberguard/prompts.py`.
- `ChatHistory` stored in `st.session_state` — cleared on "Clear Chat"; not persisted.

**Status:** [ ] pending

---

## Sub-Task 9 — `tests/` suite

**Intent:** pytest coverage for all business-logic modules in both packages.

**Expected Outcomes:**
- `tests/__init__.py` (empty).
- `tests/test_models.py` — Expense/BudgetPlan construction, validation, round-trip.
- `tests/test_validators.py` — all four validators, valid + invalid inputs.
- `tests/test_storage.py` — missing file, save/load round-trip (tmp_path).
- `tests/test_calculations.py` — known sample data, correct sums.
- `tests/test_cyberguard_prompts.py` — `SYSTEM_PROMPT` non-empty, `FEW_SHOTS` has all keys.
- `tests/test_cyberguard_history.py` — add/clear/last_n on `ChatHistory`.
- All tests pass with `pytest -q` and no Streamlit imports.

**Todo List:**
1. Create `tests/__init__.py`.
2. Create `tests/test_models.py`.
3. Create `tests/test_validators.py`.
4. Create `tests/test_storage.py` (uses `tmp_path`).
5. Create `tests/test_calculations.py`.
6. Create `tests/test_cyberguard_prompts.py`.
7. Create `tests/test_cyberguard_history.py`.

**Relevant Context:**
- Budget Planner test requirements: PRD 4.9.
- CyberGuard tests are lightweight (no real LLM call needed); test structure/logic only.
- `LLMClient` in stub mode (no API key) can be tested without network.

**Status:** [ ] pending

---

## Sub-Task 10 — Supporting files

**Intent:** Documentation and configuration to make the project self-contained.

**Expected Outcomes:**
- `requirements.txt` — `streamlit>=1.35`, `pandas>=2.2`, `anthropic>=0.25` (optional, noted).
- `README.md` — full setup, run, test, and usage instructions for both apps.
- `.gitignore` — standard Python + `data/`, `*.csv`, `.env`.
- `.env.example` — shows `ANTHROPIC_API_KEY=your_key_here`.

**Todo List:**
1. Create `requirements.txt`.
2. Create `README.md` with:
   - Project overview (both apps).
   - Project structure tree.
   - Setup instructions (venv, pip install).
   - Run tests (`pytest -q`).
   - Run app (`streamlit run streamlit_app.py`).
   - CyberGuard API key setup (env var).
   - Usage guide for both pages.
   - Known limitations.
3. Create `.gitignore`.
4. Create `.env.example`.

**Relevant Context:**
- PRD Budget Planner section 5 provides verbatim CLI steps for README.
- CyberGuard NFR2: note that no personal data is stored beyond session.

**Status:** [ ] pending

---

## Implementation Order

```
Sub-Task 1   budget_planner/exceptions.py       no deps
Sub-Task 2   budget_planner/validators.py       deps: exceptions
Sub-Task 3   budget_planner/models.py           deps: exceptions, validators
Sub-Task 4   budget_planner/storage.py          deps: exceptions, models
Sub-Task 5   budget_planner/calculations.py     deps: models
Sub-Task 6   cyberguard/ package                no budget_planner deps
Sub-Task 7   streamlit_app.py + pages/1_*       deps: budget_planner all
Sub-Task 8   pages/2_CyberGuard.py             deps: cyberguard all
Sub-Task 9   tests/                             deps: all packages
Sub-Task 10  supporting files                   independent
```
