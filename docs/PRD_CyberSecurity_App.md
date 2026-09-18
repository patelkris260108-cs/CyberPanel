# Product Requirements Document (PRD)
## AI Cybersecurity Guide & Analyzer
**Version:** 1.0  
**Status:** Approved  
**Owner:** IBM Bob AI Project  

---

## 1. Executive Summary

The AI Cybersecurity Guide & Analyzer is a standalone, AI-powered web application that empowers individuals — especially non-technical beginners — to protect themselves online. It provides three core capabilities in a unified interface:

1. **"Is This Safe?" Analyzer** — paste any suspicious message, URL, or email and receive an instant AI-driven risk assessment.
2. **Password Strength + Behavior Advisor** — evaluate password quality and receive personalised safe-habit coaching.
3. **Cyber Awareness Chatbot** — an always-on conversational guide that explains threats, answers questions, and teaches safer online habits.

---

## 2. Vision

> *Empower every individual — regardless of technical background — to recognise cyber threats, understand security risks, and build safer online habits through an accessible, AI-powered security education platform.*

---

## 3. Problem Statement

| Problem | Impact |
|---------|--------|
| Phishing attacks increased 61% year-over-year (APWG 2023) | Users cannot distinguish real from fake messages |
| 80% of breaches involve weak or stolen passwords | Users reuse simple passwords across multiple accounts |
| Security awareness training is expensive and inaccessible | Individuals lack affordable, on-demand cyber education |
| Existing tools are too technical for beginners | Low adoption among the most vulnerable users |

---

## 4. Target Users

### Primary: Individual / Home User
- Age: 16–65, any technical level
- Goal: Know if a suspicious message/link is safe
- Pain points: Confused by jargon, no one to ask

### Secondary: Student / Early Professional
- Goal: Learn cybersecurity basics interactively
- Pain points: Existing resources are boring or too advanced

### Tertiary: Small Business Owner
- Goal: Quick security checks without a dedicated IT team
- Pain points: No budget for enterprise security tools

---

## 5. Goals & Success Metrics

| Goal | Metric | Target |
|------|--------|--------|
| Accurate phishing detection | Precision/Recall on test set | ≥ 90% |
| User satisfaction | Post-session rating (1–5) | ≥ 4.2 / 5 |
| Engagement | Users who ask 3+ questions per session | ≥ 40% |
| Education | Quiz completion rate | ≥ 35% per weekly active user |
| Adoption | Month-over-month user growth | ≥ 15% |

---

## 6. Functional Requirements

### FR1 — "Is This Safe?" Analyzer
| ID | Requirement |
|----|-------------|
| FR1.1 | Accept free-text input: email body, SMS text, URL, or any suspicious content |
| FR1.2 | Perform heuristic analysis (regex patterns, keyword detection) without LLM |
| FR1.3 | Optionally call LLM for deep reasoning and natural-language explanation |
| FR1.4 | Return a numeric risk score (0–100) with colour-coded severity |
| FR1.5 | List specific red-flag indicators found in the input |
| FR1.6 | Provide plain-language explanation of why the content is risky or safe |
| FR1.7 | Give actionable advice (delete, report, verify via official site) |
| FR1.8 | Show a "Show Reasoning" expandable section with step-by-step analysis |

### FR2 — Password Strength + Behavior Advisor
| ID | Requirement |
|----|-------------|
| FR2.1 | Accept a user-supplied password in a masked input field |
| FR2.2 | Run local entropy/pattern analysis (length, complexity, common patterns, dictionary words) |
| FR2.3 | Assign a strength score (0–100) and label: Weak / Fair / Good / Strong / Very Strong |
| FR2.4 | List specific weaknesses found (e.g., "contains dictionary word", "too short") |
| FR2.5 | Generate improvement suggestions (e.g., add special character, use passphrase) |
| FR2.6 | Offer a "Generate Strong Password" button that creates a secure alternative |
| FR2.7 | Display a visual strength meter (progress bar) |
| FR2.8 | Show time-to-crack estimate based on entropy |
| FR2.9 | Provide a Behavior Coach section with personalised safe-habit tips |

### FR3 — Cyber Awareness Chatbot
| ID | Requirement |
|----|-------------|
| FR3.1 | Provide a conversational chat interface with message history |
| FR3.2 | Answer questions about any cybersecurity topic in plain language |
| FR3.3 | Use analogies and everyday examples to explain concepts |
| FR3.4 | Maintain session context for multi-turn conversations |
| FR3.5 | Route phishing/password analysis requests to the appropriate engine |
| FR3.6 | Offer suggested starter questions to guide new users |
| FR3.7 | Show a typing indicator while generating a response |
| FR3.8 | Allow clearing chat history |

### FR4 — Security Knowledge Base
| ID | Requirement |
|----|-------------|
| FR4.1 | Maintain an offline glossary of 50+ security terms |
| FR4.2 | Display a searchable "Learn" section with threat categories |
| FR4.3 | Show daily/session security tip from curated knowledge base |
| FR4.4 | Provide quick-reference cards for common threats |

### FR5 — User Feedback Loop
| ID | Requirement |
|----|-------------|
| FR5.1 | Show 👍 / 👎 after every AI response |
| FR5.2 | Log anonymised feedback ratings to session state |
| FR5.3 | Display feedback summary in session |

---

## 7. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR1 | Performance | Heuristic analysis < 200 ms; LLM response < 5 s |
| NFR2 | Privacy | Passwords never stored, logged, or transmitted; all local |
| NFR3 | Accessibility | WCAG 2.1 AA: keyboard nav, ARIA labels, sufficient contrast |
| NFR4 | Reliability | App usable fully offline (heuristic mode) without API key |
| NFR5 | Security | Input sanitised; no XSS; no prompt injection |
| NFR6 | Usability | Zero-configuration start; works without API key in demo mode |
| NFR7 | Portability | Runs on Python 3.11+, any OS, single `streamlit run` command |

---

## 8. Out of Scope (v1.0)

- Real-time network traffic monitoring
- Endpoint protection or antivirus
- Enterprise SIEM/SOC integration
- Voice or image input (OCR)
- User accounts or persistent cross-session data
- Multi-language support
- Mobile native app

---

## 9. Assumptions & Dependencies

- Python 3.11+ runtime available
- `streamlit >= 1.35`, `pandas >= 2.2` installed
- `anthropic` package optional — app fully functional without it
- `ANTHROPIC_API_KEY` environment variable for LLM features

---

## 10. Risks

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| LLM API unavailable | Medium | Full offline heuristic fallback |
| False negatives in phishing detection | Medium | Conservative heuristics + user education |
| User enters real password | Low | Explicit warning + local-only processing |
| Prompt injection attacks | Low | Input sanitisation + system prompt guardrails |
