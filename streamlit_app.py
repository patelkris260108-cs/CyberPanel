"""Home / landing page for the AI Cybersecurity & Budget Tools workspace."""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="AI CyberGuard & Budget Tools — IBM",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero {
    background: linear-gradient(135deg, #0d1526 0%, #0a1628 50%, #060b14 100%);
    border: 1px solid #1e3050;
    border-radius: 18px;
    padding: 48px 40px 40px;
    text-align: center;
    margin-bottom: 32px;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 700;
    color: #e8f4fd;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
}
.hero-sub {
    font-size: 1.05rem;
    color: #7a9cc0;
    max-width: 620px;
    margin: 0 auto 28px;
    line-height: 1.65;
}
.badge-row {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 8px;
}
.badge {
    background: #162035;
    border: 1px solid #1e3050;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.78rem;
    color: #7ac0f4;
    font-weight: 500;
}
.card {
    background: #0d1526;
    border: 1px solid #1e3050;
    border-radius: 16px;
    padding: 28px 26px;
    height: 100%;
    transition: border-color 0.2s;
}
.card:hover { border-color: #3b82d4; }
.card-icon { font-size: 2.4rem; margin-bottom: 14px; }
.card-title { font-size: 1.2rem; font-weight: 700; color: #e8f4fd; margin-bottom: 8px; }
.card-desc  { font-size: 0.87rem; color: #7a9cc0; line-height: 1.65; margin-bottom: 18px; }
.feat-list  { list-style: none; padding: 0; margin: 0 0 20px; }
.feat-list li {
    font-size: 0.84rem;
    color: #b0cce8;
    padding: 5px 0;
    border-bottom: 1px solid #1a2d45;
    display: flex;
    gap: 8px;
    align-items: flex-start;
}
.feat-list li:last-child { border-bottom: none; }
.stat-row { display: flex; gap: 18px; justify-content: center; margin-top: 28px; }
.stat-box {
    background: #0d1526;
    border: 1px solid #1e3050;
    border-radius: 12px;
    padding: 18px 24px;
    text-align: center;
    min-width: 110px;
}
.stat-num { font-size: 1.7rem; font-weight: 700; color: #3b82d4; }
.stat-lbl { font-size: 0.75rem; color: #7a9cc0; margin-top: 2px; }
.footer {
    margin-top: 40px;
    padding-top: 18px;
    border-top: 1px solid #1e3050;
    text-align: center;
    font-size: 0.78rem;
    color: #4a6580;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">🛡️ AI CyberGuard & Budget Planner</div>
  <div class="hero-sub">
    An IBM-powered workspace combining real-time AI cybersecurity analysis
    with a personal finance tracker — built for learning, awareness, and action.
  </div>
  <div class="badge-row">
    <span class="badge">🤖 NVIDIA NIM · mistral-nemotron</span>
    <span class="badge">⚡ Streaming AI responses</span>
    <span class="badge">🔒 No data stored</span>
    <span class="badge">🐍 Python + Streamlit</span>
    <span class="badge">✅ 160 tests passing</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── App cards ──────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
<div class="card">
  <div class="card-icon">🛡️</div>
  <div class="card-title">CyberGuard AI</div>
  <div class="card-desc">
    AI-powered cybersecurity assistant with streaming responses —
    word-by-word output powered by NVIDIA NIM.
  </div>
  <ul class="feat-list">
    <li>🔍 <strong>Phishing Analyzer</strong> — paste any suspicious message for instant risk scoring + AI deep analysis</li>
    <li>🔑 <strong>Password Advisor</strong> — local entropy scoring + AI coaching streamed live</li>
    <li>💬 <strong>Cyber Chatbot</strong> — streaming chat about any security topic</li>
    <li>📖 <strong>Learn & Reference</strong> — glossary, threat cards, 18 daily tips</li>
    <li>🧠 <strong>Security Explainer & Nudge Coach</strong> — in CyberGuard page</li>
  </ul>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/2_CyberGuard.py", label="🛡️  Open CyberGuard AI →", use_container_width=True)

with col2:
    st.markdown("""
<div class="card">
  <div class="card-icon">💰</div>
  <div class="card-title">Personal Budget Planner</div>
  <div class="card-desc">
    Track your monthly spending with a clean, data-driven dashboard.
    All data persisted locally to CSV — no cloud, no signup.
  </div>
  <ul class="feat-list">
    <li>💵 <strong>Set monthly budget</strong> — saves to session state</li>
    <li>➕ <strong>Add expenses</strong> — category, amount, description, date</li>
    <li>📊 <strong>Live metrics</strong> — total spent, remaining budget, delta indicator</li>
    <li>📈 <strong>Category bar chart</strong> — visual breakdown by Food / Travel / Shopping / Education</li>
    <li>📁 <strong>CSV persistence</strong> — survives app restarts via <code>data/expenses.csv</code></li>
  </ul>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/1_Budget_Planner.py", label="💰  Open Budget Planner →", use_container_width=True)

# ── Stats bar ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="stat-row">
  <div class="stat-box"><div class="stat-num">160</div><div class="stat-lbl">Tests Passing</div></div>
  <div class="stat-box"><div class="stat-num">2</div><div class="stat-lbl">Apps</div></div>
  <div class="stat-box"><div class="stat-num">5</div><div class="stat-lbl">AI Features</div></div>
  <div class="stat-box"><div class="stat-num">17</div><div class="stat-lbl">Phishing Rules</div></div>
  <div class="stat-box"><div class="stat-num">20</div><div class="stat-lbl">Glossary Terms</div></div>
  <div class="stat-box"><div class="stat-num">18</div><div class="stat-lbl">Security Tips</div></div>
</div>
""", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  Built with Python · Streamlit · NVIDIA NIM · OpenAI SDK &nbsp;|&nbsp;
  IBM AI Cybersecurity Project &nbsp;|&nbsp;
  No personal data is stored beyond your browser session.
</div>
""", unsafe_allow_html=True)
