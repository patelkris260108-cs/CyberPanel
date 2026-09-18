# AI Cybersecurity & Budget Tools

A **multi-page Streamlit workspace** containing two tools:

| Page | Description |
|------|-------------|
| 💰 **Personal Budget Planner** | Set a monthly budget, record categorised expenses, view totals and charts. Data persisted to `data/expenses.csv`. |
| 🛡️ **CyberGuard** | AI-powered cybersecurity awareness assistant with Phishing Analyzer, Security Explainer, Password Advisor, and Behavior Coach. Powered by Anthropic Claude (optional). |

---

## Project Structure

```
.
├── budget_planner/          # Pure-Python business logic (no Streamlit)
│   ├── __init__.py
│   ├── calculations.py      # total_expenses, remaining_budget, category_totals
│   ├── exceptions.py        # InvalidBudgetError, InvalidExpenseError, StorageError
│   ├── models.py            # Expense, BudgetPlan data classes
│   ├── storage.py           # load_expenses, save_expenses (CSV)
│   └── validators.py        # Input validation helpers + ALLOWED_CATEGORIES
├── cyberguard/              # CyberGuard business logic (no Streamlit)
│   ├── __init__.py
│   ├── analyzer.py          # analyze_phishing, explain_concept, advise_password, behavior_nudge
│   ├── chat_history.py      # In-memory ChatHistory class
│   ├── config.py            # Env-var configuration
│   ├── llm_client.py        # Anthropic Claude wrapper with graceful stub fallback
│   └── prompts.py           # SYSTEM_PROMPT, FEW_SHOTS, COT_TRIGGER
├── pages/
│   ├── 1_Budget_Planner.py  # Budget Planner Streamlit page
│   └── 2_CyberGuard.py      # CyberGuard Streamlit page
├── tests/
│   ├── __init__.py
│   ├── test_calculations.py
│   ├── test_cyberguard_history.py
│   ├── test_cyberguard_prompts.py
│   ├── test_models.py
│   ├── test_storage.py
│   └── test_validators.py
├── streamlit_app.py         # Home / landing page
├── requirements.txt
├── .env.example
└── README.md
```

---

## Prerequisites

- Python 3.11 or newer
- `pip`

---

## Setup

### 1. Clone / extract the repository

```bash
git clone <repo-url>
cd <repo-folder>
```

### 2. (Recommended) Create a virtual environment

```bash
python -m venv venv
# Activate:
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows PowerShell
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install pytest              # to run the test suite
```

### 4. (Optional) Enable CyberGuard AI responses

CyberGuard works in **demo / stub mode** without an API key — it will display an
informational message instead of real AI output.

To enable real Anthropic Claude responses:

```bash
pip install anthropic            # install the SDK
cp .env.example .env             # copy the example env file
# Edit .env and set:  ANTHROPIC_API_KEY=your_key_here
```

Obtain a free API key at <https://console.anthropic.com/>.

> **Privacy note:** The app loads the key from the environment variable
> `ANTHROPIC_API_KEY`. It is never logged or stored anywhere.

---

## Run the Test Suite

```bash
pytest -q
```

All tests should pass. The test suite covers:

- `budget_planner` models, validators, storage round-trips, and calculations.
- `cyberguard` prompt structure and `ChatHistory` logic.
- No Streamlit imports; no network calls.

---

## Run the Application

```bash
streamlit run streamlit_app.py
```

The app opens in your default browser at <http://localhost:8501>.

Use the **sidebar** to navigate between the two pages.

---

## Using the Budget Planner

1. Open **💰 Budget Planner** from the sidebar.
2. Enter your **Monthly Budget** in the sidebar and click **Save Budget**.
3. Fill in the expense form (category, amount, description, date) and click **Add Expense**.
4. The **metrics**, **bar chart**, and **expense table** update instantly.
5. Expenses are saved to `data/expenses.csv` and reload automatically on the next run.

---

## Using CyberGuard

1. Open **🛡️ CyberGuard** from the sidebar.
2. The sidebar shows whether the AI is connected (green ✅) or in demo mode (amber ⚠️).
3. Choose a tab:
   - **💬 Chat** – ask any cybersecurity question in free-form.
   - **🎣 Phishing Analyzer** – paste a suspicious email or SMS and click **Analyze**.
   - **🔑 Password Advisor** – enter a password to evaluate its strength.
   - **📖 Security Explainer** – ask about any security term or concept.
   - **💡 Security Nudge** – get a quick, actionable security tip.
4. Use **👍 / 👎** buttons to rate responses (stored in session state only).
5. Click **🗑️ Clear Chat History** to start fresh.

---

## Data Persistence

| Data | Where stored | Lifetime |
|------|-------------|---------|
| Expenses | `data/expenses.csv` | Permanent (survives restarts) |
| Monthly budget | `st.session_state` | Session only (reset on restart) |
| CyberGuard chat history | `st.session_state` | Session only |
| Feedback ratings | `st.session_state` | Session only |

Deleting `data/expenses.csv` clears all expense history (the app recreates it on the
next expense addition).

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | *(empty)* | Anthropic API key – required for real AI responses |
| `LLM_PROVIDER` | `anthropic` | LLM provider (currently only `anthropic` is supported) |
| `CYBERGUARD_MODEL` | `claude-3-5-haiku-20241022` | Claude model to use |
| `CYBERGUARD_MAX_TOKENS` | `1024` | Maximum tokens per response |

Copy `.env.example` to `.env` and fill in values; then run:

```bash
# macOS / Linux
export $(grep -v '^#' .env | xargs)
streamlit run streamlit_app.py

# Windows PowerShell
Get-Content .env | ForEach-Object { $k,$v=$_.split('=',2); [System.Environment]::SetEnvironmentVariable($k,$v) }
streamlit run streamlit_app.py
```

---

## Known Limitations

- **Single-user only** – no authentication or multi-user support.
- **No expense editing or deletion** – append-only ledger.
- **Concurrent writes** – simultaneous writes to `data/expenses.csv` from multiple
  browser tabs are not safe (last write wins).
- **Monthly budget resets** on app restart (not persisted to disk).
- **CyberGuard chat history** is session-scoped and lost on page refresh.
