"""AI Cybersecurity Guide & Analyzer — professional Streamlit application."""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="CyberGuard AI — Security Guide & Analyzer",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

import datetime
import html as html_lib

import pandas as pd

from cybersec.analyzer import (
    advise_password,
    analyze_message,
    chat,
    generate_strong_password,
    stream_analysis_explanation,
    stream_chat,
    stream_password_advice,
)
from cybersec.chat_history import ChatHistory
from cybersec.knowledge_base import (
    get_all_glossary_terms,
    get_all_threat_cards,
    get_all_tips,
    get_daily_tip,
    get_glossary_entry,
    search_knowledge_base,
)
from cybersec.llm_client import LLMClient
from cybersec.sanitizer import is_valid_input

# ─────────────────────────────────────────────────────────────────────────────
# Professional Dark UI — Global CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ─── Root palette ─────────────────────────────────────────────── */
:root {
  --bg:        #060b14;
  --bg2:       #0d1526;
  --surface:   #111d2e;
  --surface2:  #162035;
  --border:    #1e3050;
  --border2:   #254060;
  --neon:      #00c8ff;
  --neon2:     #6c63ff;
  --neon3:     #00ff9d;
  --text:      #dce8f8;
  --text2:     #8da8c8;
  --safe:      #00c97a;
  --low:       #f0c040;
  --medium:    #f07830;
  --high:      #f03040;
  --critical:  #c00020;
  --font:      'Inter', sans-serif;
  --mono:      'JetBrains Mono', monospace;
}

/* ─── Base ─────────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: var(--font) !important;
  color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
section[data-testid="stSidebar"] {
  background: var(--bg2) !important;
  border-right: 1px solid var(--border) !important;
}

/* ─── Hide default Streamlit chrome ─────────────────────────────── */
#MainMenu, footer, header { visibility: hidden !important; }
.block-container { padding-top: 1.2rem !important; max-width: 1280px !important; }

/* ─── Typography ────────────────────────────────────────────────── */
h1, h2, h3, h4, h5 { font-family: var(--font) !important; letter-spacing: -0.3px; }
p, li, label, span  { font-family: var(--font) !important; }
code, pre { font-family: var(--mono) !important; }

/* ─── Streamlit widgets ─────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea  > div > div > textarea,
.stNumberInput > div > div > input,
.stSelectbox  > div > div {
  background:  var(--surface) !important;
  border:      1px solid var(--border2) !important;
  color:       var(--text) !important;
  border-radius: 8px !important;
  font-family: var(--font) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea  > div > div > textarea:focus {
  border-color: var(--neon) !important;
  box-shadow: 0 0 0 2px rgba(0,200,255,0.15) !important;
}
.stButton > button {
  background: linear-gradient(135deg, #0a2a4a, #0e3860) !important;
  border: 1px solid var(--neon) !important;
  color: var(--neon) !important;
  border-radius: 8px !important;
  font-family: var(--font) !important;
  font-weight: 600 !important;
  letter-spacing: 0.3px !important;
  transition: all 0.2s ease !important;
  padding: 0.45rem 1.1rem !important;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #0e3860, #1448a0) !important;
  box-shadow: 0 0 16px rgba(0,200,255,0.35) !important;
  transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #0055cc, #0080ff) !important;
  border-color: #0090ff !important;
  color: #ffffff !important;
}
.stButton > button[kind="primary"]:hover {
  background: linear-gradient(135deg, #0066ee, #20a0ff) !important;
  box-shadow: 0 0 20px rgba(0,144,255,0.5) !important;
}

/* ─── Tabs ──────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--surface) !important;
  border-radius: 10px !important;
  padding: 4px !important;
  border: 1px solid var(--border) !important;
  gap: 4px !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--text2) !important;
  border-radius: 7px !important;
  font-weight: 500 !important;
  font-family: var(--font) !important;
  padding: 0.4rem 1.2rem !important;
  border: none !important;
  transition: all 0.2s ease !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--neon) !important; }
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, #0a2a4a, #0e3860) !important;
  color: var(--neon) !important;
  box-shadow: 0 0 12px rgba(0,200,255,0.2) !important;
}
.stTabs [data-baseweb="tab-panel"] {
  padding-top: 1.2rem !important;
}

/* ─── Metrics ───────────────────────────────────────────────────── */
[data-testid="metric-container"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 16px 20px !important;
  transition: border-color 0.2s ease !important;
}
[data-testid="metric-container"]:hover { border-color: var(--border2) !important; }
[data-testid="stMetricLabel"]  { color: var(--text2) !important; font-size: 0.78rem !important; text-transform: uppercase !important; letter-spacing: 0.8px !important; }
[data-testid="stMetricValue"]  { color: var(--text)  !important; font-size: 1.6rem !important; font-weight: 700 !important; }
[data-testid="stMetricDelta"]  { font-size: 0.82rem !important; }

/* ─── Expanders ─────────────────────────────────────────────────── */
.streamlit-expanderHeader {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text) !important;
  font-weight: 500 !important;
}
.streamlit-expanderContent {
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-top: none !important;
  border-radius: 0 0 8px 8px !important;
}

/* ─── Alerts / info boxes ───────────────────────────────────────── */
.stAlert { border-radius: 8px !important; font-family: var(--font) !important; }
div[data-testid="stNotification"] { border-radius: 8px !important; }

/* ─── DataFrames ────────────────────────────────────────────────── */
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; }
[data-testid="stDataFrameResizable"] th {
  background: var(--surface2) !important;
  color: var(--text2) !important;
  font-size: 0.75rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.6px !important;
}

/* ─── Sidebar ───────────────────────────────────────────────────── */
.sidebar-logo {
  display: flex; align-items: center; gap: 10px;
  padding: 6px 0 16px 0; border-bottom: 1px solid var(--border);
  margin-bottom: 16px;
}
.sidebar-logo-text { font-size: 1.15rem; font-weight: 700; color: var(--neon); letter-spacing: 0.5px; }
.sidebar-logo-sub  { font-size: 0.72rem; color: var(--text2); margin-top: 2px; letter-spacing: 0.3px; }

/* ─── Status badges ─────────────────────────────────────────────── */
.badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px; border-radius: 20px;
  font-size: 0.75rem; font-weight: 600; letter-spacing: 0.3px;
}
.badge-online  { background: rgba(0,201,122,0.12); border: 1px solid var(--safe);   color: var(--safe);   }
.badge-offline { background: rgba(240,192, 64,0.12); border: 1px solid var(--low);  color: var(--low);   }
.badge-safe     { background: rgba(0,201,122,0.12); border: 1px solid var(--safe);   color: var(--safe);   }
.badge-low      { background: rgba(240,192, 64,0.12); border: 1px solid var(--low);  color: var(--low);   }
.badge-medium   { background: rgba(240,120, 48,0.12); border: 1px solid var(--medium);color: var(--medium);}
.badge-high     { background: rgba(240, 48, 64,0.12); border: 1px solid var(--high); color: var(--high);  }
.badge-critical { background: rgba(192,  0, 32,0.2);  border: 1px solid var(--critical);color: var(--critical);}

/* ─── Cards ─────────────────────────────────────────────────────── */
.cyber-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px; padding: 20px 22px; margin-bottom: 14px;
}
.cyber-card-accent {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--neon);
  border-radius: 0 12px 12px 0; padding: 18px 22px; margin-bottom: 14px;
}
.section-header {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 0 14px 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 18px;
}
.section-title { font-size: 1.05rem; font-weight: 600; color: var(--text); }
.section-icon  { font-size: 1.2rem; }

/* ─── Risk progress bar ─────────────────────────────────────────── */
.risk-bar-wrap  { margin: 14px 0; }
.risk-bar-label { display: flex; justify-content: space-between; margin-bottom: 7px; }
.risk-bar-track { background: #0a1828; border-radius: 8px; height: 16px; overflow: hidden; border: 1px solid var(--border); position: relative; }
.risk-bar-fill  { height: 100%; border-radius: 8px; transition: width 0.7s cubic-bezier(0.4,0,0.2,1); }
.risk-bar-glow  { position: absolute; top: 0; left: 0; height: 100%; border-radius: 8px; filter: blur(6px); opacity: 0.4; }

/* ─── Indicator pills ───────────────────────────────────────────── */
.indicator-pill {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(240,48,64,0.08);
  border: 1px solid rgba(240,48,64,0.35);
  color: #ff7080; border-radius: 20px;
  padding: 5px 12px; margin: 3px; font-size: 0.78rem;
}

/* ─── Chat bubbles ──────────────────────────────────────────────── */
.chat-wrap      { display: flex; flex-direction: column; gap: 10px; padding: 4px 0; }
.chat-row-user  { display: flex; justify-content: flex-end; }
.chat-row-bot   { display: flex; justify-content: flex-start; }
.chat-avatar    { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1rem; flex-shrink: 0; }
.chat-av-user   { background: linear-gradient(135deg,#4040a0,#6040c0); }
.chat-av-bot    { background: linear-gradient(135deg,#004060,#0060a0); }
.chat-bubble-user {
  background: linear-gradient(135deg,#0d2040,#142850);
  border: 1px solid #1e3060; border-radius: 16px 4px 16px 16px;
  padding: 12px 16px; max-width: 78%; margin-right: 10px;
  color: var(--text); font-size: 0.9rem; line-height: 1.55;
}
.chat-bubble-bot {
  background: linear-gradient(135deg,#071828,#0a2035);
  border: 1px solid var(--border); border-left: 2px solid var(--neon);
  border-radius: 4px 16px 16px 16px;
  padding: 12px 16px; max-width: 82%; margin-left: 10px;
  color: var(--text); font-size: 0.9rem; line-height: 1.55;
}
.chat-meta { font-size: 0.68rem; color: var(--text2); margin-top: 4px; }
.chat-empty {
  text-align: center; padding: 52px 20px;
  color: var(--text2); font-size: 0.92rem;
}
.chat-empty-icon { font-size: 3rem; margin-bottom: 12px; }

/* ─── Stat row ──────────────────────────────────────────────────── */
.stat-row { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 18px; }
.stat-box {
  flex: 1; min-width: 120px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; padding: 14px 16px; text-align: center;
}
.stat-val  { font-size: 1.5rem; font-weight: 700; color: var(--text); }
.stat-lbl  { font-size: 0.7rem; color: var(--text2); text-transform: uppercase; letter-spacing: 0.6px; margin-top: 3px; }

/* ─── Tip card ──────────────────────────────────────────────────── */
.tip-card {
  background: linear-gradient(135deg, #061420, #0a1e30);
  border: 1px solid var(--border); border-left: 3px solid var(--neon3);
  border-radius: 0 10px 10px 0; padding: 14px 16px;
  font-size: 0.86rem; color: var(--text); line-height: 1.5;
}

/* ─── Threat card ───────────────────────────────────────────────── */
.threat-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; padding: 18px 20px; height: 100%;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}
.threat-card:hover {
  border-color: var(--neon); box-shadow: 0 0 20px rgba(0,200,255,0.08);
}
.threat-icon { font-size: 1.8rem; margin-bottom: 8px; }
.threat-title { font-size: 0.98rem; font-weight: 600; color: var(--neon); margin-bottom: 6px; }
.threat-desc  { font-size: 0.82rem; color: var(--text2); line-height: 1.5; }

/* ─── Password strength bar ─────────────────────────────────────── */
.pwd-bar-wrap  { margin: 14px 0; }
.pwd-bar-track { background: #0a1828; border-radius: 8px; height: 14px; overflow: hidden; border: 1px solid var(--border); }
.pwd-bar-fill  { height: 100%; border-radius: 8px; transition: width 0.6s ease; }

/* ─── Glossary entry ────────────────────────────────────────────── */
.gloss-term { font-size: 0.88rem; font-weight: 600; color: var(--neon); }
.gloss-def  { font-size: 0.83rem; color: var(--text); line-height: 1.5; margin-top: 4px; }
.gloss-sev  { display: inline-block; font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; padding: 2px 8px; border-radius: 10px; margin-top: 6px; }

/* ─── Divider ───────────────────────────────────────────────────── */
.neon-line {
  border: none; height: 1px;
  background: linear-gradient(90deg, transparent, var(--neon), transparent);
  margin: 20px 0; opacity: 0.4;
}

/* ─── Generated password box ────────────────────────────────────── */
.gen-pwd-box {
  background: var(--surface2); border: 1px solid var(--border);
  border-radius: 10px; padding: 14px 18px;
  font-family: var(--mono); font-size: 1.05rem;
  color: var(--neon3); letter-spacing: 1px; word-break: break-all;
}

/* ─── Resource link ─────────────────────────────────────────────── */
.res-link {
  display: block; background: var(--surface);
  border: 1px solid var(--border); border-radius: 8px;
  padding: 10px 14px; text-decoration: none !important;
  color: var(--text) !important; font-size: 0.85rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  margin-bottom: 6px;
}
.res-link:hover { border-color: var(--neon); box-shadow: 0 0 10px rgba(0,200,255,0.1); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Session-state init
# ─────────────────────────────────────────────────────────────────────────────
def _init() -> None:
    defaults = {
        "cs_client": None,
        "cs_history": None,
        "cs_feedback": [],
        "analysis_result": None,
        "analysis_llm": "",
        "pwd_result": None,
        "pwd_llm": "",
        "generated_pwd": "",
        "chat_messages": [],   # list of dicts {role, content, ts}
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    if st.session_state.cs_client is None:
        st.session_state.cs_client = LLMClient()
    if st.session_state.cs_history is None:
        st.session_state.cs_history = ChatHistory()

_init()
client: LLMClient      = st.session_state.cs_client
history: ChatHistory   = st.session_state.cs_history


# ─────────────────────────────────────────────────────────────────────────────
# Utility renderers
# ─────────────────────────────────────────────────────────────────────────────
_SEV_COLOUR = {
    "safe": "#00c97a", "low": "#f0c040",
    "medium": "#f07830", "high": "#f03040", "critical": "#c00020",
}
_SEV_EMOJI  = {
    "safe": "✅", "low": "🟡", "medium": "🟠", "high": "🔴", "critical": "💀",
}
_PWD_COLOUR = {
    "Weak": "#c00020", "Fair": "#f07830",
    "Good": "#f0c040", "Strong": "#3090ff", "Very Strong": "#00c97a",
}


def _risk_bar(score: int, severity: str) -> None:
    c = _SEV_COLOUR.get(severity, "#888")
    e = _SEV_EMOJI.get(severity, "⚪")
    st.markdown(f"""
<div class="risk-bar-wrap">
  <div class="risk-bar-label">
    <span style="color:var(--text2);font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.6px;">Risk Score</span>
    <span style="color:{c};font-weight:700;font-size:0.92rem;">{e}&nbsp;{severity.upper()}&nbsp;&mdash;&nbsp;{score}/100</span>
  </div>
  <div class="risk-bar-track">
    <div class="risk-bar-fill" style="width:{score}%;background:{c};"></div>
  </div>
</div>""", unsafe_allow_html=True)


def _pwd_bar(score: int, label: str) -> None:
    c = _PWD_COLOUR.get(label, "#888")
    st.markdown(f"""
<div class="pwd-bar-wrap">
  <div class="risk-bar-label">
    <span style="color:var(--text2);font-size:0.78rem;font-weight:600;text-transform:uppercase;letter-spacing:0.6px;">Password Strength</span>
    <span style="color:{c};font-weight:700;font-size:0.92rem;">{label}&nbsp;&mdash;&nbsp;{score}/100</span>
  </div>
  <div class="pwd-bar-track">
    <div class="pwd-bar-fill" style="width:{score}%;background:{c};"></div>
  </div>
</div>""", unsafe_allow_html=True)


def _badge(severity: str, label: str | None = None) -> None:
    cls = f"badge badge-{severity}"
    text = label or severity.upper()
    e = _SEV_EMOJI.get(severity, "")
    st.markdown(f'<span class="{cls}">{e} {text}</span>', unsafe_allow_html=True)


def _feedback(key: str) -> None:
    c1, c2, _ = st.columns([1, 1, 12])
    if c1.button("👍", key=f"up_{key}", help="Helpful"):
        st.session_state.cs_feedback.append({"k": key, "v": "+1"})
        st.toast("Thanks! 👍", icon="✅")
    if c2.button("👎", key=f"dn_{key}", help="Not helpful"):
        st.session_state.cs_feedback.append({"k": key, "v": "-1"})
        st.toast("Got it — will improve 👎", icon="🔧")


def _neon_line() -> None:
    st.markdown('<hr class="neon-line">', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div class="sidebar-logo">
  <span style="font-size:1.6rem;">🛡️</span>
  <div>
    <div class="sidebar-logo-text">CyberGuard AI</div>
    <div class="sidebar-logo-sub">Security Guide &amp; Analyzer</div>
  </div>
</div>""", unsafe_allow_html=True)

    # API status
    if client.available:
        st.markdown('<span class="badge badge-online">● AI Online — NVIDIA NIM</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-offline">⚠ Demo Mode — No API Key</span>', unsafe_allow_html=True)
        st.caption("Set `NVIDIA_API_KEY` env var for full AI features.")

    _neon_line()

    # Daily tip
    st.markdown("**💡 Security Tip of the Day**")
    tip = get_daily_tip()
    st.markdown(f'<div class="tip-card">{html_lib.escape(tip)}</div>', unsafe_allow_html=True)

    _neon_line()

    # Session stats
    pos = sum(1 for f in st.session_state.cs_feedback if f.get("v") == "+1")
    neg = len(st.session_state.cs_feedback) - pos
    msgs = len(st.session_state.chat_messages)
    st.markdown(f"""
<div class="stat-row">
  <div class="stat-box">
    <div class="stat-val">{msgs}</div>
    <div class="stat-lbl">Chat msgs</div>
  </div>
  <div class="stat-box">
    <div class="stat-val" style="color:var(--safe);">{pos}</div>
    <div class="stat-lbl">👍 Ratings</div>
  </div>
  <div class="stat-box">
    <div class="stat-val" style="color:var(--high);">{neg}</div>
    <div class="stat-lbl">👎 Ratings</div>
  </div>
</div>""", unsafe_allow_html=True)

    if st.button("🗑️  Clear Session", use_container_width=True):
        for k in ("analysis_result","analysis_llm","pwd_result","pwd_llm",
                  "generated_pwd","chat_messages","cs_feedback"):
            st.session_state[k] = [] if k in ("cs_feedback","chat_messages") else (None if "result" in k else "")
        history.clear()
        st.success("Session cleared.")
        st.rerun()

    _neon_line()
    st.caption("🔒 No personal data stored beyond this session.")
    st.caption("IBM AI for Cybersecurity Project")


# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding: 8px 0 20px 0;">
  <div style="display:flex; align-items:center; gap:14px; flex-wrap:wrap;">
    <div>
      <h1 style="margin:0; font-size:1.9rem; font-weight:700; color:#dce8f8; letter-spacing:-0.5px;">
        🛡️ CyberGuard <span style="color:#00c8ff;">AI</span>
      </h1>
      <p style="margin:4px 0 0 0; color:#8da8c8; font-size:0.88rem; letter-spacing:0.2px;">
        Identify threats &nbsp;·&nbsp; Analyse risks &nbsp;·&nbsp; Build safer habits &nbsp;·&nbsp; Powered by NVIDIA NIM
      </p>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

_neon_line()

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab_analyze, tab_password, tab_chat, tab_learn = st.tabs([
    "🔍  Is This Safe?",
    "🔑  Password Advisor",
    "💬  Cyber Chatbot",
    "📚  Learn & Reference",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — IS THIS SAFE? Analyzer
# ══════════════════════════════════════════════════════════════════════════════
with tab_analyze:
    left_a, right_a = st.columns([3, 2], gap="large")

    with left_a:
        st.markdown("""
<div class="section-header">
  <span class="section-icon">🔍</span>
  <span class="section-title">Paste Suspicious Content</span>
</div>""", unsafe_allow_html=True)

        st.markdown('<p style="color:var(--text2);font-size:0.85rem;margin-bottom:10px;">Paste any suspicious email, SMS, URL, or message to check for phishing and security risks.</p>', unsafe_allow_html=True)

        user_input = st.text_area(
            "Content to analyze",
            height=200,
            max_chars=10_000,
            placeholder='Example:\n"URGENT: Your account is suspended.\nVerify now at http://amaz0n-secure.net/login"',
            label_visibility="collapsed",
        )

        c1, c2 = st.columns([3, 1])
        analyze_clicked = c1.button("🔍  Analyze Now", type="primary", use_container_width=True, key="btn_analyze")
        clear_a = c2.button("✕  Clear", use_container_width=True, key="btn_a_clear")

        if clear_a:
            st.session_state.analysis_result = None
            st.session_state.analysis_llm = ""
            st.rerun()

        if analyze_clicked:
            valid, err = is_valid_input(user_input)
            if not valid:
                st.error(err)
            else:
                with st.spinner("Scanning for threats…"):
                    result, _ = analyze_message(user_input, client)
                st.session_state.analysis_result = result
                # Stream the LLM deep-analysis separately so we get word-by-word output
                if client.available:
                    _stream_placeholder = st.empty()
                    _stream_buf = ""
                    for _chunk in stream_analysis_explanation(user_input, client):
                        _stream_buf += _chunk
                        _stream_placeholder.markdown(
                            f'<div class="cyber-card-accent" style="font-size:0.85rem;line-height:1.7;">'
                            f'{_stream_buf}▌</div>',
                            unsafe_allow_html=True,
                        )
                    _stream_placeholder.empty()
                    st.session_state.analysis_llm = _stream_buf
                else:
                    st.session_state.analysis_llm = ""

        # Results
        res = st.session_state.analysis_result
        if res:
            _neon_line()
            _risk_bar(res.risk_score, res.severity)
            m1, m2, m3 = st.columns(3)
            m1.metric("Risk Score",    f"{res.risk_score}/100")
            m2.metric("Severity",      f"{_SEV_EMOJI.get(res.severity,'')} {res.severity.upper()}")
            m3.metric("Red Flags",     str(len(res.indicators)))

            _neon_line()
            st.markdown(f"""
<div class="cyber-card-accent">
  <div style="font-size:0.72rem;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:0.7px;margin-bottom:8px;">Analysis</div>
  <div style="font-size:0.88rem;color:var(--text);line-height:1.6;">{html_lib.escape(res.explanation)}</div>
</div>""", unsafe_allow_html=True)

            col_adv_c = _SEV_COLOUR.get(res.severity, "#888")
            st.markdown(f"""
<div style="background:rgba(0,0,0,0.2);border:1px solid {col_adv_c}40;border-left:3px solid {col_adv_c};
            border-radius:0 10px 10px 0;padding:14px 18px;margin-bottom:14px;">
  <div style="font-size:0.72rem;font-weight:600;color:{col_adv_c};text-transform:uppercase;letter-spacing:0.7px;margin-bottom:6px;">Recommended Action</div>
  <div style="font-size:0.88rem;color:var(--text);line-height:1.6;">{html_lib.escape(res.advice)}</div>
</div>""", unsafe_allow_html=True)

            if st.session_state.analysis_llm:
                with st.expander("🤖  Show AI Deep Analysis & Reasoning"):
                    st.markdown(st.session_state.analysis_llm)
                    _feedback("analyze_ai")

    with right_a:
        st.markdown("""
<div class="section-header">
  <span class="section-icon">🚩</span>
  <span class="section-title">Red-Flag Indicators</span>
</div>""", unsafe_allow_html=True)

        res = st.session_state.analysis_result
        if res and res.indicators:
            for ind in res.indicators:
                st.markdown(f'<div class="indicator-pill">⚠ {html_lib.escape(ind)}</div>', unsafe_allow_html=True)
            _neon_line()
        elif res:
            st.markdown(f'<span class="badge badge-safe">✅ No suspicious indicators found</span>', unsafe_allow_html=True)
        else:
            st.markdown("""
<div style="text-align:center;padding:40px 10px;color:var(--text2);">
  <div style="font-size:2.5rem;margin-bottom:12px;">🔍</div>
  <div style="font-size:0.86rem;">Paste a message on the left<br>and click Analyze Now</div>
</div>""", unsafe_allow_html=True)

        # Quick-reference guide
        _neon_line()
        st.markdown("""
<div style="font-size:0.72rem;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:0.7px;margin-bottom:12px;">Phishing Red Flags to Look For</div>""", unsafe_allow_html=True)
        flags = [
            ("🔗", "Misspelled domains", "amaz0n.com vs amazon.com"),
            ("⚡", "Urgency language",   "Act now / Account suspended"),
            ("🔑", "Credential requests","Asks for password or card"),
            ("📎", "Suspicious files",   ".exe .zip .docm attachments"),
            ("🌐", "HTTP links",         "No HTTPS padlock"),
            ("👤", "Generic greetings",  "Dear Customer / Dear User"),
        ]
        for icon, title, desc in flags:
            st.markdown(f"""
<div style="display:flex;gap:10px;align-items:flex-start;padding:7px 0;border-bottom:1px solid var(--border);">
  <span style="font-size:1rem;">{icon}</span>
  <div>
    <div style="font-size:0.82rem;font-weight:600;color:var(--text);">{title}</div>
    <div style="font-size:0.75rem;color:var(--text2);">{desc}</div>
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PASSWORD ADVISOR
# ══════════════════════════════════════════════════════════════════════════════
with tab_password:
    left_p, right_p = st.columns([3, 2], gap="large")

    with left_p:
        st.markdown("""
<div class="section-header">
  <span class="section-icon">🔑</span>
  <span class="section-title">Password Strength Advisor</span>
</div>""", unsafe_allow_html=True)

        st.markdown('<p style="color:var(--text2);font-size:0.85rem;margin-bottom:10px;">Enter any password to evaluate its strength. Your password is <strong style="color:var(--neon3);">analysed locally — never sent anywhere.</strong></p>', unsafe_allow_html=True)

        pwd_input = st.text_input(
            "Password",
            type="password",
            max_chars=512,
            placeholder="Enter a password to evaluate…",
            label_visibility="collapsed",
        )

        c1, c2, c3 = st.columns(3)
        check_p   = c1.button("🔍  Evaluate", type="primary", use_container_width=True, key="btn_pwd_eval")
        gen_p     = c2.button("✨  Generate Strong", use_container_width=True, key="btn_pwd_gen")
        clear_p   = c3.button("✕  Clear", use_container_width=True, key="btn_pwd_clear")

        if clear_p:
            st.session_state.pwd_result = None
            st.session_state.pwd_llm = ""
            st.session_state.generated_pwd = ""
            st.rerun()

        if check_p:
            if not pwd_input.strip():
                st.warning("Please enter a password to evaluate.")
            else:
                with st.spinner("Analysing password locally…"):
                    pr, _ = advise_password(pwd_input, client)
                st.session_state.pwd_result = pr
                st.session_state.generated_pwd = ""
                # Stream the LLM coaching separately
                if client.available:
                    _pwd_stream_ph = st.empty()
                    _pwd_stream_buf = ""
                    for _chunk in stream_password_advice(pwd_input, pr, client):
                        _pwd_stream_buf += _chunk
                        _pwd_stream_ph.markdown(
                            f'<div class="cyber-card-accent" style="font-size:0.85rem;line-height:1.7;">'
                            f'{_pwd_stream_buf}▌</div>',
                            unsafe_allow_html=True,
                        )
                    _pwd_stream_ph.empty()
                    st.session_state.pwd_llm = _pwd_stream_buf
                else:
                    st.session_state.pwd_llm = ""

        if gen_p:
            with st.spinner("Generating a strong password…"):
                gpwd, pr = generate_strong_password()
            st.session_state.pwd_result = pr
            st.session_state.generated_pwd = gpwd
            st.session_state.pwd_llm = ""

        pr = st.session_state.pwd_result
        if pr:
            _neon_line()
            if st.session_state.generated_pwd:
                st.markdown("**✨ Generated Password**")
                st.markdown(f'<div class="gen-pwd-box">{html_lib.escape(st.session_state.generated_pwd)}</div>', unsafe_allow_html=True)
                st.caption("💡 Copy this and store it in a password manager.")
                _neon_line()

            _pwd_bar(pr.score, pr.label)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Score",         f"{pr.score}/100")
            m2.metric("Strength",      pr.label)
            m3.metric("Entropy",       f"{pr.entropy_bits} bits")
            m4.metric("Crack Time",    pr.crack_time)

            _neon_line()
            if pr.weaknesses:
                st.markdown("**⚠️ Weaknesses**")
                for w in pr.weaknesses:
                    st.markdown(f'<div style="color:var(--high);font-size:0.84rem;padding:3px 0;">🔴 {html_lib.escape(w)}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge badge-safe">✅ No significant weaknesses</span>', unsafe_allow_html=True)

            if st.session_state.pwd_llm:
                _neon_line()
                with st.expander("🤖  AI Password Coaching", expanded=True):
                    st.markdown(st.session_state.pwd_llm)
                    _feedback("pwd_ai")

    with right_p:
        st.markdown("""
<div class="section-header">
  <span class="section-icon">💡</span>
  <span class="section-title">Improvement Tips</span>
</div>""", unsafe_allow_html=True)

        pr = st.session_state.pwd_result
        if pr and pr.suggestions:
            for s in pr.suggestions:
                st.markdown(f'<div style="color:var(--neon3);font-size:0.84rem;padding:5px 0;border-bottom:1px solid var(--border);">✅ {html_lib.escape(s)}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:var(--text2);font-size:0.84rem;">Enter a password on the left to get personalised suggestions.</div>', unsafe_allow_html=True)

        _neon_line()
        st.markdown("""
<div style="font-size:0.72rem;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:0.7px;margin-bottom:12px;">Password Best Practices</div>""", unsafe_allow_html=True)
        practices = [
            ("📏", "16+ characters",        "Length is the #1 factor"),
            ("🔤", "Mix character types",   "Upper, lower, digits, symbols"),
            ("🔀", "Avoid patterns",         "No 123, abc, qwerty"),
            ("🔁", "Unique per site",        "Never reuse passwords"),
            ("🗄️", "Use a manager",         "Bitwarden is free & secure"),
            ("📱", "Enable MFA",            "Second layer of protection"),
        ]
        for icon, title, desc in practices:
            st.markdown(f"""
<div style="display:flex;gap:10px;align-items:flex-start;padding:7px 0;border-bottom:1px solid var(--border);">
  <span style="font-size:1rem;">{icon}</span>
  <div>
    <div style="font-size:0.82rem;font-weight:600;color:var(--text);">{title}</div>
    <div style="font-size:0.75rem;color:var(--text2);">{desc}</div>
  </div>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CYBER CHATBOT
# ══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown("""
<div class="section-header">
  <span class="section-icon">💬</span>
  <span class="section-title">Cyber Awareness Chatbot</span>
</div>""", unsafe_allow_html=True)

    # Suggested prompts row
    st.markdown('<div style="color:var(--text2);font-size:0.78rem;text-transform:uppercase;letter-spacing:0.6px;font-weight:600;margin-bottom:8px;">Quick Start</div>', unsafe_allow_html=True)
    sugg_cols = st.columns(4)
    suggestions = [
        "What is ransomware?",
        "How does 2FA work?",
        "How do I spot phishing?",
        "Give me a security tip",
    ]
    triggered_sugg = None
    for i, s in enumerate(suggestions):
        if sugg_cols[i].button(s, key=f"sugg_{i}", use_container_width=True):
            triggered_sugg = s

    _neon_line()

    # Chat display area
    msgs = st.session_state.chat_messages
    if not msgs:
        st.markdown("""
<div class="chat-empty">
  <div class="chat-empty-icon">🛡️</div>
  <div style="font-weight:600;color:var(--text);margin-bottom:6px;">CyberGuard is ready</div>
  <div>Ask me anything about cybersecurity.<br>I can explain threats, analyse messages, and guide you toward safer habits.</div>
</div>""", unsafe_allow_html=True)
    else:
        chat_html = '<div class="chat-wrap">'
        for msg in msgs:
            ts = msg.get("ts", "")
            if msg["role"] == "user":
                chat_html += f"""
<div class="chat-row-user">
  <div>
    <div class="chat-bubble-user">{html_lib.escape(msg["content"])}</div>
    <div class="chat-meta" style="text-align:right;">{ts}</div>
  </div>
  <div class="chat-avatar chat-av-user">👤</div>
</div>"""
            else:
                # bot — allow markdown (content is AI-generated, no user html)
                safe_content = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
                chat_html += f"""
<div class="chat-row-bot">
  <div class="chat-avatar chat-av-bot">🛡️</div>
  <div>
    <div class="chat-bubble-bot">{safe_content}</div>
    <div class="chat-meta">{ts}</div>
  </div>
</div>"""
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)

        # Feedback on last bot message
        if msgs and msgs[-1]["role"] == "assistant":
            _feedback(f"chat_{len(msgs)}")

    _neon_line()

    # Input row
    chat_input_col, send_col = st.columns([9, 1])
    with chat_input_col:
        user_msg = st.text_input(
            "Message",
            placeholder="Ask anything about cybersecurity…",
            label_visibility="collapsed",
            key="chat_input_box",
        )
    with send_col:
        send_clicked = st.button("Send ➤", type="primary", use_container_width=True)

    # Handle input
    final_msg = triggered_sugg or (user_msg.strip() if send_clicked and user_msg.strip() else None)
    if final_msg:
        ts_now = datetime.datetime.now().strftime("%H:%M")
        st.session_state.chat_messages.append({"role": "user", "content": final_msg, "ts": ts_now})

        # ── Streaming reply ─────────────────────────────────────────────
        _reply_buf = ""
        _reply_ph = st.empty()
        for _chunk in stream_chat(final_msg, history, client):
            _reply_buf += _chunk
            _reply_ph.markdown(
                f'<div class="chat-bubble-bot" style="'
                f'background:var(--surface2);border:1px solid var(--border);'
                f'border-radius:4px 18px 18px 18px;padding:12px 16px;'
                f'font-size:0.9rem;line-height:1.6;color:var(--text);'
                f'max-width:80%;white-space:pre-wrap;">'
                f'{_reply_buf}▌</div>',
                unsafe_allow_html=True,
            )
        _reply_ph.empty()  # clear streaming placeholder — final message shown in chat_html on rerun
        # Persist both turns to ChatHistory (stream_chat does NOT mutate history)
        history.add("user", final_msg)
        history.add("assistant", _reply_buf)
        st.session_state.chat_messages.append({"role": "assistant", "content": _reply_buf, "ts": ts_now})
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — LEARN & REFERENCE
# ══════════════════════════════════════════════════════════════════════════════
with tab_learn:
    lt1, lt2, lt3 = st.tabs(["📖  Glossary", "🃏  Threat Cards", "💡  Security Tips"])

    # ── Glossary ─────────────────────────────────────────────────────────────
    with lt1:
        st.markdown("""<div class="section-header"><span class="section-icon">📖</span><span class="section-title">Security Glossary</span></div>""", unsafe_allow_html=True)

        q = st.text_input("Search glossary", placeholder="e.g. phishing, ransomware, 2FA…", key="gloss_q")
        results = search_knowledge_base(q.strip()) if q.strip() else [get_glossary_entry(t) for t in get_all_glossary_terms()]
        results = [r for r in results if r]

        sev_colours = {"low":"var(--safe)","medium":"var(--low)","high":"var(--high)","critical":"var(--critical)"}

        for entry in results:
            sev   = entry.get("severity", "low")
            sc    = sev_colours.get(sev, "var(--text2)")
            with st.expander(f"**{entry.get('term','')}**  —  {entry.get('definition','')[:72]}…"):
                st.markdown(f'<span style="color:{sc};font-size:0.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">● {sev}</span>', unsafe_allow_html=True)
                st.markdown(f'<div style="font-size:0.87rem;color:var(--text);margin:8px 0;">{entry.get("definition","")}</div>', unsafe_allow_html=True)
                if entry.get("analogy"):
                    st.markdown(f'<div class="cyber-card-accent" style="font-size:0.84rem;"><strong>💡 Analogy:</strong> {entry["analogy"]}</div>', unsafe_allow_html=True)
                if entry.get("examples"):
                    st.markdown("**Examples:**")
                    for ex in entry["examples"]:
                        st.markdown(f'<div style="font-size:0.83rem;color:var(--text2);">• {ex}</div>', unsafe_allow_html=True)
                if entry.get("related"):
                    tags = "".join(f'<span style="background:var(--surface2);border:1px solid var(--border);border-radius:5px;padding:2px 9px;font-size:0.75rem;color:var(--neon);margin:2px;">{r}</span>' for r in entry["related"])
                    st.markdown(f'<div style="margin-top:8px;">{tags}</div>', unsafe_allow_html=True)

    # ── Threat Cards ──────────────────────────────────────────────────────────
    with lt2:
        st.markdown("""<div class="section-header"><span class="section-icon">🃏</span><span class="section-title">Quick-Reference Threat Cards</span></div>""", unsafe_allow_html=True)

        cards = get_all_threat_cards()
        for i in range(0, len(cards), 2):
            cols = st.columns(2, gap="medium")
            for j in range(2):
                if i + j < len(cards):
                    card = cards[i + j]
                    with cols[j]:
                        st.markdown(f"""
<div class="threat-card">
  <div class="threat-icon">{card.get("icon","🔒")}</div>
  <div class="threat-title">{card.get("title","")}</div>
  <div class="threat-desc">{card.get("description","")}</div>
</div>""", unsafe_allow_html=True)
                        with st.expander("View details →"):
                            if card.get("warning_signs"):
                                st.markdown("**⚠️ Warning Signs**")
                                for w in card["warning_signs"]:
                                    st.markdown(f'<div style="font-size:0.82rem;color:var(--low);padding:2px 0;">• {w}</div>', unsafe_allow_html=True)
                            if card.get("prevention"):
                                st.markdown("**🛡️ Prevention**")
                                for p in card["prevention"]:
                                    st.markdown(f'<div style="font-size:0.82rem;color:var(--neon3);padding:2px 0;">• {p}</div>', unsafe_allow_html=True)
                            if card.get("if_infected"):
                                st.markdown("**🚨 If Affected**")
                                for a in card["if_infected"]:
                                    st.markdown(f'<div style="font-size:0.82rem;color:var(--high);padding:2px 0;">• {a}</div>', unsafe_allow_html=True)

    # ── Tips ──────────────────────────────────────────────────────────────────
    with lt3:
        st.markdown("""<div class="section-header"><span class="section-icon">💡</span><span class="section-title">Security Best-Practice Tips</span></div>""", unsafe_allow_html=True)
        all_tips = get_all_tips()
        for i, tip_text in enumerate(all_tips, 1):
            st.markdown(f"""
<div style="display:flex;gap:12px;align-items:flex-start;padding:12px 0;border-bottom:1px solid var(--border);">
  <span style="background:var(--surface2);border:1px solid var(--border);border-radius:6px;
               padding:3px 9px;font-size:0.72rem;font-weight:600;color:var(--neon);
               min-width:36px;text-align:center;flex-shrink:0;">#{i}</span>
  <span style="font-size:0.86rem;color:var(--text);line-height:1.55;">{html_lib.escape(tip_text)}</span>
</div>""", unsafe_allow_html=True)

        _neon_line()
        st.markdown("""<div style="font-size:0.72rem;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:0.7px;margin-bottom:12px;">Trusted External Resources</div>""", unsafe_allow_html=True)
        resources = [
            ("🇺🇸 CISA — Cybersecurity & Infrastructure",  "https://www.cisa.gov/topics/cyber-threats-and-advisories"),
            ("🇬🇧 NCSC — National Cyber Security Centre",  "https://www.ncsc.gov.uk/section/advice-guidance/all-topics"),
            ("🔑 Have I Been Pwned — Breach Check",        "https://haveibeenpwned.com"),
            ("🔐 Bitwarden — Free Password Manager",       "https://bitwarden.com"),
            ("📋 NIST Cybersecurity Framework",            "https://www.nist.gov/cyberframework"),
            ("📚 StaySafeOnline — Awareness Hub",          "https://staysafeonline.org"),
        ]
        rc = st.columns(2)
        for i, (name, url) in enumerate(resources):
            rc[i % 2].markdown(f'<a href="{url}" target="_blank" class="res-link">🔗 {name}</a>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
_neon_line()
st.markdown("""
<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;padding-bottom:12px;">
  <span style="color:var(--text2);font-size:0.78rem;">
    🛡️ <strong style="color:var(--text);">CyberGuard AI</strong>
    &nbsp;·&nbsp; IBM AI for Cybersecurity Project
    &nbsp;·&nbsp; Built with Python &amp; Streamlit
    &nbsp;·&nbsp; NVIDIA NIM LLM
  </span>
  <span style="color:var(--text2);font-size:0.78rem;">
    🔒 No personal data stored beyond this session
  </span>
</div>
""", unsafe_allow_html=True)
