# Workflow Document
## AI Cybersecurity Guide & Analyzer
**Version:** 1.0

---

## 1. Overview

This document describes the end-to-end user and system workflows for all three core features of the AI Cybersecurity Guide & Analyzer application.

---

## 2. User Journey Map

```
User arrives at app
        │
        ▼
┌───────────────────────────────┐
│        Home Dashboard         │
│  • Daily security tip         │
│  • 3 feature cards            │
│  • Suggested starter prompts  │
└───────┬───────┬───────────────┘
        │       │       │
        ▼       ▼       ▼
   Analyzer  Password  Chatbot
   Feature   Feature   Feature
```

---

## 3. Feature Workflow 1 — "Is This Safe?" Analyzer

### 3.1 Happy Path (Phishing Detected)

```
User pastes suspicious message
           │
           ▼
   [Input Validation]
   • Not empty
   • Length ≤ 10,000 chars
   • Strip leading/trailing whitespace
           │
           ▼
   [Heuristic Pre-scan] ──────────────── runs synchronously < 200 ms
   • Regex: URL pattern matching
   • Keyword scan: urgency words, impersonation phrases
   • Domain spoofing detection (e.g. amaz0n, paypa1)
   • Excessive capitalisation check
   • Threat-language detection
           │
           ▼
   [Risk Score Assembly]
   • Base score from heuristic hits
   • Weight by indicator severity
   • Clamp to 0–100
           │
     ┌─────┴──────────────────────────────┐
     │ If ANTHROPIC_API_KEY set            │  If no key
     ▼                                    ▼
  [LLM Deep Analysis]            [Heuristic-only result]
  • Build prompt with             • Show rule-based findings
    system + fewshots +           • "Connect AI for deeper
    user input + CoT                analysis" nudge
  • Parse response
     │
     ▼
  [Result Display]
  • Risk meter (colour: green/amber/red)
  • Severity badge: Safe / Low / Medium / High / Critical
  • Red-flag indicator list
  • Plain-language explanation
  • Actionable advice
  • Expandable "Show Reasoning" accordion
  • 👍/👎 feedback buttons
```

### 3.2 Edge Cases

| Scenario | Handling |
|----------|----------|
| Empty input | Show validation error, focus input |
| Input > 10,000 chars | Truncate at 10,000 with warning |
| Only a URL | Detect as URL, run URL-specific checks |
| Benign message | Score = 0–25, green badge, "Looks Safe" |
| LLM timeout | Fall back to heuristic result, show notice |
| LLM returns malformed JSON | Parse text response, show as-is |

---

## 4. Feature Workflow 2 — Password Strength + Behavior Advisor

### 4.1 Password Evaluation Flow

```
User types password in masked field
           │
           ▼
   [Real-time local analysis] ─── triggers on every keystroke (debounced 300ms)
   • Length check
   • Character class presence (upper, lower, digit, symbol)
   • Common password list check (top-1000)
   • Dictionary word detection
   • Sequential/repeated character detection
   • Personal info pattern detection (dates, names)
           │
           ▼
   [Entropy Calculation]
   • Character pool size × log2(pool)
   • Adjusted for detected patterns
   • Map to time-to-crack estimate
           │
           ▼
   [Score + Label]
   0-19:  Weak        (red)
   20-39: Fair        (orange)
   40-59: Good        (yellow)
   60-79: Strong      (blue)
   80+:   Very Strong (green)
           │
           ▼
   [Suggestions Generation]
   • Rule-based improvement tips
   • If ANTHROPIC_API_KEY set: AI-personalised advice
           │
           ▼
   [Display]
   • Animated strength bar
   • Score + label
   • Time-to-crack estimate
   • Weakness list with icons
   • Improvement suggestions
   • "Generate Password" button
```

### 4.2 Password Generation Flow

```
User clicks "Generate Strong Password"
           │
           ▼
   [Generation engine]
   • Select 4 unrelated words from curated wordlist
   • Insert random numbers and symbols between words
   • Ensure: length ≥ 16, all character classes present
   • Evaluate generated password through same scorer
           │
           ▼
   [Display]
   • Show generated password (revealed)
   • Show its strength score (should be Very Strong)
   • "Copy to clipboard" button
```

### 4.3 Behavior Coach Flow

```
After password analysis
           │
           ▼
   [Context-aware nudge selection]
   • If weak password → "Use a password manager" tip
   • If short password → "Longer is stronger" tip
   • If no symbols → "Add special characters" tip
   • Always → Show 3 rotating behavior tips
```

---

## 5. Feature Workflow 3 — Cyber Awareness Chatbot

### 5.1 Message Flow

```
User types question / pastes content
           │
           ▼
   [Intent Classification] ─── local keyword/regex, < 10 ms
   • "phishing" / "safe" / "suspicious" → route to analyzer
   • "password" / "strong" / "weak"    → route to password advisor
   • everything else                   → general Q&A
           │
           ▼
   [Prompt Assembly]
   system_prompt
   + few_shot_examples[intent]
   + last_10_history_messages
   + user_message
   + cot_trigger (for analysis tasks)
           │
     ┌─────┴────────────────────────┐
     │ LLM available                │ No LLM
     ▼                              ▼
  [LLM API call]           [Knowledge base lookup]
  • Stream tokens if        • Search glossary
    possible                • Return definition +
  • Show typing indicator     related tips
     │
     ▼
  [Response Display]
  • Render markdown in chat bubble
  • Append to history
  • Show 👍/👎 feedback
  • Show "Related topics" chips (optional)
```

### 5.2 Conversation State Machine

```
[IDLE]
   │  user sends message
   ▼
[PROCESSING] ── timeout 30s ──▶ [ERROR: show friendly message]
   │  response received
   ▼
[RESPONSE DISPLAYED]
   │  user sends follow-up
   ▼
[PROCESSING with history context]
   │  user clicks Clear
   ▼
[IDLE]
```

---

## 6. System Startup Workflow

```
streamlit run cybersecurity_app.py
           │
           ▼
   [Session state init]
   • Check ANTHROPIC_API_KEY → set llm_available flag
   • Load knowledge base (JSON) from disk
   • Load common password list
   • Initialise ChatHistory
   • Select daily tip
           │
           ▼
   [Render home dashboard]
   • Show API status badge
   • Show daily tip
   • Show feature cards
```

---

## 7. Data Flow Diagram

```
User Input (text)
       │
       ├──▶ Sanitizer (strip, length-limit, HTML-escape)
       │
       ├──▶ HeuristicEngine ──▶ RiskScore + Indicators
       │         │
       │         └──▶ PromptBuilder
       │                   │
       │                   └──▶ LLMClient ──▶ Anthropic API
       │                              │            │
       │                              └────────────┘
       │                                    │
       │                             NaturalLanguageResponse
       │
       └──▶ KnowledgeBase ──▶ GlossaryLookup
                                    │
                              RelevantDefinitions

All streams → ResultAggregator → Streamlit UI Renderer
```

---

## 8. Prompt Engineering Workflow

```
1. System message (role, tone, privacy constraints, CoT instruction)
       +
2. Few-shot examples (intent-specific)
       +
3. [Optional] Retrieved knowledge-base passages
       +
4. Conversation history (last 10 turns)
       +
5. User message
       +
6. CoT trigger: "Think step by step before answering."
       │
       ▼
   Assembled prompt → LLM API → Parse response → Display
```
