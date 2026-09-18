"""CyberGuard – AI Cybersecurity Awareness Assistant – with STREAMING responses."""

from __future__ import annotations

import streamlit as st

from cyberguard.chat_history import ChatHistory
from cyberguard.config import NVIDIA_API_KEY
from cyberguard.llm_client import LLMClient
from cyberguard.prompts import SYSTEM_PROMPT, FEW_SHOTS, COT_TRIGGER
from cyberguard.analyzer import analyze_phishing, explain_concept, advise_password, behavior_nudge

st.set_page_config(
    page_title="🛡️ CyberGuard",
    page_icon="🛡️",
    layout="wide",
)

# ── Session-state initialisation ──────────────────────────────────────────────
if "cg_client" not in st.session_state:
    st.session_state.cg_client = LLMClient()
if "cg_history" not in st.session_state:
    st.session_state.cg_history = ChatHistory()
if "cg_feedback" not in st.session_state:
    st.session_state.cg_feedback: list[dict] = []
if "cg_messages" not in st.session_state:
    st.session_state.cg_messages: list[dict] = []
if "cg_phishing_result" not in st.session_state:
    st.session_state.cg_phishing_result: str = ""
if "cg_password_result" not in st.session_state:
    st.session_state.cg_password_result: str = ""
if "cg_explainer_result" not in st.session_state:
    st.session_state.cg_explainer_result: str = ""
if "cg_nudge_result" not in st.session_state:
    st.session_state.cg_nudge_result: str = ""

client: LLMClient = st.session_state.cg_client
history: ChatHistory = st.session_state.cg_history

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root {
  --bg:#060b14; --bg2:#0d1526; --surface:#111d2e; --border:#1e3050;
  --neon:#00c8ff; --neon3:#00ff9d; --text:#dce8f8; --text2:#8da8c8;
  --safe:#00c97a; --low:#f0c040; --high:#f03040;
}
html,body,[data-testid="stAppViewContainer"],.stApp{background:var(--bg)!important;font-family:'Inter',sans-serif!important;color:var(--text)!important;}
section[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border)!important;}
#MainMenu,footer,header{visibility:hidden!important;}
.block-container{padding-top:1rem!important;max-width:1280px!important;}
h1,h2,h3,h4,h5{font-family:'Inter',sans-serif!important;}
.stButton>button{background:linear-gradient(135deg,#0a2a4a,#0e3860)!important;border:1px solid var(--neon)!important;color:var(--neon)!important;border-radius:8px!important;font-weight:600!important;transition:all .2s!important;}
.stButton>button:hover{box-shadow:0 0 16px rgba(0,200,255,.35)!important;transform:translateY(-1px)!important;}
.stButton>button[kind="primary"]{background:linear-gradient(135deg,#0055cc,#0080ff)!important;border-color:#0090ff!important;color:#fff!important;}
.stTabs [data-baseweb="tab-list"]{background:var(--surface)!important;border-radius:10px!important;padding:4px!important;border:1px solid var(--border)!important;}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--text2)!important;border-radius:7px!important;font-weight:500!important;border:none!important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,#0a2a4a,#0e3860)!important;color:var(--neon)!important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea{background:var(--surface)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:8px!important;}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:var(--neon)!important;box-shadow:0 0 0 2px rgba(0,200,255,.15)!important;}
[data-testid="metric-container"]{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:12px!important;padding:16px 20px!important;}
[data-testid="stMetricLabel"]{color:var(--text2)!important;font-size:.75rem!important;text-transform:uppercase!important;letter-spacing:.7px!important;}
[data-testid="stMetricValue"]{color:var(--text)!important;font-size:1.5rem!important;font-weight:700!important;}
.chat-row-user{display:flex;justify-content:flex-end;margin:6px 0;}
.chat-row-bot{display:flex;justify-content:flex-start;margin:6px 0;}
.chat-av{width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:.9rem;flex-shrink:0;}
.av-user{background:linear-gradient(135deg,#4040a0,#6040c0);}
.av-bot{background:linear-gradient(135deg,#004060,#0060a0);}
.bubble-user{background:linear-gradient(135deg,#0d2040,#142850);border:1px solid #1e3060;border-radius:16px 4px 16px 16px;padding:10px 14px;max-width:78%;margin-right:8px;color:var(--text);font-size:.88rem;line-height:1.55;}
.bubble-bot{background:linear-gradient(135deg,#071828,#0a2035);border:1px solid var(--border);border-left:2px solid var(--neon);border-radius:4px 16px 16px 16px;padding:10px 14px;max-width:82%;margin-left:8px;color:var(--text);font-size:.88rem;line-height:1.55;}
.chat-ts{font-size:.65rem;color:var(--text2);margin-top:3px;}
.chat-empty{text-align:center;padding:48px 20px;color:var(--text2);}
.neon-line{border:none;height:1px;background:linear-gradient(90deg,transparent,var(--neon),transparent);margin:16px 0;opacity:.35;}
.pill-danger{display:inline-flex;align-items:center;gap:5px;background:rgba(240,48,64,.08);border:1px solid rgba(240,48,64,.35);color:#ff7080;border-radius:20px;padding:4px 11px;margin:3px;font-size:.76rem;}
.badge-online{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:20px;background:rgba(0,201,122,.12);border:1px solid var(--safe);color:var(--safe);font-size:.74rem;font-weight:600;}
.badge-offline{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:20px;background:rgba(240,192,64,.12);border:1px solid var(--low);color:var(--low);font-size:.74rem;font-weight:600;}
.tip-card{background:linear-gradient(135deg,#061420,#0a1e30);border:1px solid var(--border);border-left:3px solid var(--neon3);border-radius:0 8px 8px 0;padding:12px 14px;font-size:.84rem;color:var(--text);line-height:1.5;}
.gen-pwd{background:#111d2e;border:1px solid var(--border);border-radius:8px;padding:12px 16px;font-family:'JetBrains Mono',monospace;font-size:1rem;color:var(--neon3);word-break:break-all;letter-spacing:.8px;}
.risk-track{background:#0a1828;border-radius:8px;height:15px;overflow:hidden;border:1px solid var(--border);}
.risk-fill{height:100%;border-radius:8px;transition:width .7s cubic-bezier(.4,0,.2,1);}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
_SEV_C = {"safe":"#00c97a","low":"#f0c040","medium":"#f07830","high":"#f03040","critical":"#c00020"}
_SEV_E = {"safe":"✅","low":"🟡","medium":"🟠","high":"🔴","critical":"💀"}
_PWD_C = {"Weak":"#c00020","Fair":"#f07830","Good":"#f0c040","Strong":"#3090ff","Very Strong":"#00c97a"}

def _neon(): st.markdown('<hr class="neon-line">', unsafe_allow_html=True)

def _risk_bar(score, sev):
    c = _SEV_C.get(sev,"#888")
    st.markdown(f"""
<div style="margin:10px 0;">
  <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
    <span style="color:var(--text2);font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.6px;">Risk Score</span>
    <span style="color:{c};font-weight:700;font-size:.9rem;">{_SEV_E.get(sev,"⚪")} {sev.upper()} — {score}/100</span>
  </div>
  <div class="risk-track"><div class="risk-fill" style="width:{score}%;background:{c};"></div></div>
</div>""", unsafe_allow_html=True)

def _pwd_bar(score, label):
    c = _PWD_C.get(label,"#888")
    st.markdown(f"""
<div style="margin:10px 0;">
  <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
    <span style="color:var(--text2);font-size:.75rem;font-weight:600;text-transform:uppercase;letter-spacing:.6px;">Password Strength</span>
    <span style="color:{c};font-weight:700;font-size:.9rem;">{label} — {score}/100</span>
  </div>
  <div class="risk-track"><div class="risk-fill" style="width:{score}%;background:{c};"></div></div>
</div>""", unsafe_allow_html=True)

def _feedback(key):
    c1,c2,_ = st.columns([1,1,12])
    if c1.button("👍",key=f"up_{key}"):
        st.session_state.cg_feedback.append({"k":key,"v":"+1"}); st.toast("Thanks! 👍",icon="✅")
    if c2.button("👎",key=f"dn_{key}"):
        st.session_state.cg_feedback.append({"k":key,"v":"-1"}); st.toast("Got it 👎",icon="🔧")


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="display:flex;align-items:center;gap:10px;padding-bottom:14px;border-bottom:1px solid var(--border);margin-bottom:14px;">
  <span style="font-size:1.5rem;">🛡️</span>
  <div>
    <div style="font-size:1.05rem;font-weight:700;color:var(--neon);">CyberGuard</div>
    <div style="font-size:.7rem;color:var(--text2);">AI Security Assistant</div>
  </div>
</div>""", unsafe_allow_html=True)

    if client.available:
        st.markdown('<span class="badge-online">● AI Online — NVIDIA NIM</span>', unsafe_allow_html=True)
        st.caption(f"Model: `mistralai/mistral-nemotron`")
        st.caption("⚡ Streaming enabled — answers appear instantly")
    else:
        st.markdown('<span class="badge-offline">⚠ Demo Mode — No API Key</span>', unsafe_allow_html=True)
        st.caption("Set `NVIDIA_API_KEY` env var for AI features.")

    _neon()

    # Daily tip
    try:
        from cyberguard.prompts import FEW_SHOTS as _fs  # noqa: F401
        tips = [
            "Enable 2FA on your email today — it takes 2 minutes and stops most account hijacks.",
            "Lock your screen every time you step away (Win+L / Ctrl+Cmd+Q).",
            "Use a password manager — Bitwarden is free and stores all your passwords securely.",
            "Check haveibeenpwned.com to see if your email appeared in a data breach.",
            "Never click links in unexpected emails — go to the official site directly.",
        ]
        import datetime
        tip = tips[datetime.date.today().timetuple().tm_yday % len(tips)]
    except Exception:
        tip = "Stay safe — always verify before you click."

    st.markdown("**💡 Tip of the Day**")
    st.markdown(f'<div class="tip-card">{tip}</div>', unsafe_allow_html=True)

    _neon()

    pos = sum(1 for f in st.session_state.cg_feedback if f.get("v")=="+1")
    neg = len(st.session_state.cg_feedback)-pos
    st.markdown(f'<span style="color:var(--text2);font-size:.75rem;">Session: 👍 {pos} &nbsp; 👎 {neg}</span>', unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat History", use_container_width=True):
        history.clear()
        st.session_state.cg_messages = []
        for k in ("cg_phishing_result","cg_password_result","cg_explainer_result","cg_nudge_result"):
            st.session_state[k] = ""
        st.session_state.cg_feedback = []
        st.success("Cleared ✓")
        st.rerun()

    _neon()
    st.caption("🔒 No personal data stored beyond this session.")


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:6px 0 16px 0;">
  <h1 style="margin:0;font-size:1.8rem;font-weight:700;color:#dce8f8;">
    🛡️ CyberGuard <span style="color:#00c8ff;">AI</span>
  </h1>
  <p style="margin:4px 0 0 0;color:#8da8c8;font-size:.85rem;">
    Your AI-powered cybersecurity awareness assistant · Powered by NVIDIA NIM · ⚡ Streaming responses
  </p>
</div>""", unsafe_allow_html=True)
_neon()


# ── TABS ──────────────────────────────────────────────────────────────────────
tab_chat, tab_phish, tab_pass, tab_explain, tab_nudge = st.tabs([
    "💬 Chat", "🎣 Phishing Analyzer", "🔑 Password Advisor",
    "📖 Security Explainer", "💡 Security Nudge"
])


# ════════════════════════════════════════════════════════════════════
# TAB 1 — STREAMING CHAT
# ════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown("""
<div style="font-size:.72rem;font-weight:600;color:var(--text2);text-transform:uppercase;letter-spacing:.7px;margin-bottom:10px;">Quick Start</div>""", unsafe_allow_html=True)

    qs_cols = st.columns(4)
    quick = [
        "What is ransomware?",
        "How does 2FA work?",
        "How do I spot phishing?",
        "What is a VPN?",
    ]
    triggered = None
    for i, q in enumerate(quick):
        if qs_cols[i].button(q, key=f"qs_{i}", use_container_width=True):
            triggered = q

    _neon()

    # Chat history display
    msgs = st.session_state.cg_messages
    if not msgs:
        st.markdown("""
<div class="chat-empty">
  <div style="font-size:2.5rem;margin-bottom:10px;">🛡️</div>
  <div style="font-weight:600;color:var(--text);margin-bottom:6px;">CyberGuard is ready</div>
  <div style="font-size:.85rem;">Ask anything about cybersecurity.<br>
  Responses stream word-by-word — no more waiting!</div>
</div>""", unsafe_allow_html=True)
    else:
        import html as _h
        for i, msg in enumerate(msgs):
            if msg["role"] == "user":
                st.markdown(f"""
<div class="chat-row-user">
  <div>
    <div class="bubble-user">{_h.escape(msg["content"])}</div>
    <div class="chat-ts" style="text-align:right;">{msg.get("ts","")}</div>
  </div>
  <div class="chat-av av-user">👤</div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div class="chat-row-bot">
  <div class="chat-av av-bot">🛡️</div>
  <div>
    <div class="bubble-bot">{msg["content"]}</div>
    <div class="chat-ts">{msg.get("ts","")}</div>
  </div>
</div>""", unsafe_allow_html=True)
                if i == len(msgs)-1:
                    _feedback(f"chat_{i}")

    _neon()

    # Input + send
    in_col, btn_col = st.columns([9, 1])
    user_input = in_col.text_input(
        "msg", placeholder="Ask a cybersecurity question…",
        label_visibility="collapsed", key="cg_chat_input"
    )
    send = btn_col.button("Send ➤", type="primary", use_container_width=True)

    final_msg = triggered or (user_input.strip() if send and user_input.strip() else None)

    if final_msg:
        import datetime as _dt
        ts = _dt.datetime.now().strftime("%H:%M")

        # Add user message to display
        st.session_state.cg_messages.append({"role":"user","content":final_msg,"ts":ts})
        history.add("user", final_msg)

        # Build messages for LLM (cyberguard ChatHistory stores plain dicts)
        history_msgs = [{"role":m["role"],"content":m["content"]} for m in history.last_n(10) if m["role"] != "assistant"]
        history_msgs.append({"role":"user","content":final_msg})

        # ⚡ STREAMING — show words as they arrive
        with st.spinner(""):
            placeholder = st.empty()
            full_response = ""

            if client.available:
                for chunk in client.stream(history_msgs, system=SYSTEM_PROMPT):
                    full_response += chunk
                    placeholder.markdown(
                        f'<div class="chat-row-bot"><div class="chat-av av-bot">🛡️</div>'
                        f'<div><div class="bubble-bot">{full_response}▌</div></div></div>',
                        unsafe_allow_html=True
                    )
                placeholder.empty()
            else:
                full_response = client.chat(history_msgs, system=SYSTEM_PROMPT)

        history.add("assistant", full_response)
        st.session_state.cg_messages.append({"role":"assistant","content":full_response,"ts":ts})
        st.rerun()


# ════════════════════════════════════════════════════════════════════
# TAB 2 — STREAMING PHISHING ANALYZER
# ════════════════════════════════════════════════════════════════════
with tab_phish:
    st.markdown("### 🎣 Phishing & Message Analyzer")
    st.markdown('<p style="color:var(--text2);font-size:.85rem;">Paste any suspicious email, SMS, URL, or message. AI analyses it step-by-step in real-time.</p>', unsafe_allow_html=True)

    phish_text = st.text_area(
        "Suspicious message",
        height=180, max_chars=4000,
        placeholder='e.g. "URGENT: Your account is suspended. Verify at http://paypa1-secure.net/login"',
        label_visibility="collapsed",
        key="phish_input"
    )

    pc1, pc2 = st.columns([3,1])
    analyze_btn = pc1.button("🔍  Analyze Now", type="primary", use_container_width=True, key="btn_phish_analyze")
    if pc2.button("✕ Clear", use_container_width=True, key="btn_phish_clear"):
        st.session_state.cg_phishing_result = ""
        st.rerun()

    if analyze_btn:
        if not phish_text.strip():
            st.warning("Please paste a message to analyse.")
        else:
            # Run heuristic first (instant)
            from cybersec.heuristics import analyze_text as _heuristic
            from cybersec.sanitizer import sanitize_input as _sanitize
            clean = _sanitize(phish_text)
            h_result = _heuristic(clean)

            c_score = _SEV_C.get(h_result.severity,"#888")
            _risk_bar(h_result.risk_score, h_result.severity)
            m1,m2,m3 = st.columns(3)
            m1.metric("Risk Score", f"{h_result.risk_score}/100")
            m2.metric("Severity", f"{_SEV_E.get(h_result.severity,'')} {h_result.severity.upper()}")
            m3.metric("Red Flags", str(len(h_result.indicators)))

            if h_result.indicators:
                _neon()
                st.markdown("**🚩 Red-Flag Indicators Found:**")
                for ind in h_result.indicators:
                    st.markdown(f'<span class="pill-danger">⚠ {ind[:70]}</span>', unsafe_allow_html=True)

            _neon()
            st.markdown(f"""
<div style="background:#0a1828;border:1px solid {c_score}40;border-left:3px solid {c_score};border-radius:0 8px 8px 0;padding:12px 16px;margin-bottom:12px;">
  <div style="font-size:.7rem;font-weight:600;color:{c_score};text-transform:uppercase;letter-spacing:.6px;margin-bottom:5px;">Recommended Action</div>
  <div style="font-size:.86rem;color:var(--text);">{h_result.advice}</div>
</div>""", unsafe_allow_html=True)

            # ⚡ Stream AI deep analysis
            if client.available:
                st.markdown("**🤖 AI Deep Analysis** *(streaming)*")
                stream_placeholder = st.empty()
                full_ai = ""
                prompt_text = (
                    f"{FEW_SHOTS.get('phishing','')}\n\nAnalyse this message step by step:\n\n{clean}"
                    f"{COT_TRIGGER}"
                )
                for chunk in client.stream(
                    [{"role":"user","content":prompt_text}],
                    system=SYSTEM_PROMPT
                ):
                    full_ai += chunk
                    stream_placeholder.markdown(full_ai + "▌")
                stream_placeholder.markdown(full_ai)
                st.session_state.cg_phishing_result = full_ai
                _feedback("phish_ai")
            else:
                st.info("Add `NVIDIA_API_KEY` for AI-powered step-by-step analysis.")
                st.session_state.cg_phishing_result = h_result.explanation

    elif st.session_state.cg_phishing_result:
        st.markdown("**Previous Analysis:**")
        st.markdown(st.session_state.cg_phishing_result)


# ════════════════════════════════════════════════════════════════════
# TAB 3 — PASSWORD ADVISOR
# ════════════════════════════════════════════════════════════════════
with tab_pass:
    st.markdown("### 🔑 Password Strength Advisor")
    st.markdown('<p style="color:var(--text2);font-size:.85rem;">Your password is analysed <strong style="color:var(--neon3);">100% locally — never sent anywhere.</strong></p>', unsafe_allow_html=True)

    pwd_val = st.text_input("Password", type="password", max_chars=512,
                             placeholder="Enter a password to evaluate…",
                             label_visibility="collapsed", key="pwd_val_input")

    pw1,pw2,pw3 = st.columns(3)
    eval_btn = pw1.button("🔍  Evaluate", type="primary", use_container_width=True, key="btn_pw_eval")
    gen_btn  = pw2.button("✨  Generate Strong", use_container_width=True, key="btn_pw_gen")
    if pw3.button("✕ Clear", use_container_width=True, key="btn_pw_clear"):
        st.session_state.cg_password_result = ""
        st.rerun()

    if eval_btn and pwd_val.strip():
        from cybersec.password_engine import evaluate_password as _eval_pwd
        pr = _eval_pwd(pwd_val)
        _pwd_bar(pr.score, pr.label)
        pm1,pm2,pm3,pm4 = st.columns(4)
        pm1.metric("Score", f"{pr.score}/100")
        pm2.metric("Strength", pr.label)
        pm3.metric("Entropy", f"{pr.entropy_bits} bits")
        pm4.metric("Crack Time", pr.crack_time)

        if pr.weaknesses:
            _neon()
            st.markdown("**⚠️ Weaknesses:**")
            for w in pr.weaknesses:
                st.markdown(f'<div style="color:var(--high);font-size:.83rem;padding:2px 0;">🔴 {w}</div>', unsafe_allow_html=True)

        _neon()
        # ⚡ Stream AI coaching
        if client.available:
            st.markdown("**🤖 AI Password Coaching** *(streaming)*")
            stream_ph = st.empty()
            full_ai = ""
            masked = f"{'*' * min(len(pwd_val),8)} ({len(pwd_val)} chars)"
            prompt_text = (
                f"{FEW_SHOTS.get('password','')}\n\n"
                f"Give friendly password advice. Local analysis:\n"
                f"Score: {pr.score}/100 ({pr.label}), Entropy: {pr.entropy_bits} bits, "
                f"Crack time: {pr.crack_time}\n"
                f"Weaknesses: {'; '.join(pr.weaknesses) or 'None'}\n"
                f"Password (masked): {masked}"
            )
            for chunk in client.stream(
                [{"role":"user","content":prompt_text}],
                system=SYSTEM_PROMPT
            ):
                full_ai += chunk
                stream_ph.markdown(full_ai + "▌")
            stream_ph.markdown(full_ai)
            st.session_state.cg_password_result = full_ai
            _feedback("pwd_ai")
        else:
            st.markdown("**💡 Suggestions:**")
            for s in pr.suggestions:
                st.markdown(f'<div style="color:var(--neon3);font-size:.83rem;padding:2px 0;">✅ {s}</div>', unsafe_allow_html=True)

    elif gen_btn:
        from cybersec.password_engine import generate_password as _gen, evaluate_password as _eval_pwd
        gpwd = _gen()
        pr = _eval_pwd(gpwd)
        st.markdown("**✨ Generated Strong Password:**")
        st.markdown(f'<div class="gen-pwd">{gpwd}</div>', unsafe_allow_html=True)
        st.caption("💡 Copy this and store it in a password manager (Bitwarden is free).")
        _pwd_bar(pr.score, pr.label)
        st.metric("Strength", f"{pr.label} — {pr.score}/100")

    elif st.session_state.cg_password_result:
        st.markdown("**Previous AI Coaching:**")
        st.markdown(st.session_state.cg_password_result)


# ════════════════════════════════════════════════════════════════════
# TAB 4 — STREAMING SECURITY EXPLAINER
# ════════════════════════════════════════════════════════════════════
with tab_explain:
    st.markdown("### 📖 Security Explainer")
    st.markdown('<p style="color:var(--text2);font-size:.85rem;">Ask about any cybersecurity term or scenario — get a plain-language explanation with analogies.</p>', unsafe_allow_html=True)

    explain_q = st.text_input(
        "Question", max_chars=500,
        placeholder='e.g. "What is ransomware?" or "How does a VPN work?"',
        label_visibility="collapsed", key="explain_input"
    )
    ex1, ex2 = st.columns([3,1])
    explain_btn = ex1.button("💡  Explain", type="primary", use_container_width=True, key="btn_explain")
    if ex2.button("✕ Clear", use_container_width=True, key="btn_explain_clear"):
        st.session_state.cg_explainer_result = ""
        st.rerun()

    if explain_btn:
        if not explain_q.strip():
            st.warning("Please enter a term or question.")
        else:
            _neon()
            stream_ph = st.empty()
            full_ai = ""
            prompt = f"{FEW_SHOTS.get('explainer','')}\n\nExplain this in simple, jargon-free language with an everyday analogy:\n{explain_q}"
            if client.available:
                for chunk in client.stream(
                    [{"role":"user","content":prompt}],
                    system=SYSTEM_PROMPT
                ):
                    full_ai += chunk
                    stream_ph.markdown(full_ai + "▌")
                stream_ph.markdown(full_ai)
            else:
                full_ai = client.chat([{"role":"user","content":prompt}], system=SYSTEM_PROMPT)
                stream_ph.markdown(full_ai)
            st.session_state.cg_explainer_result = full_ai
            _feedback("explain_ai")

    elif st.session_state.cg_explainer_result:
        st.markdown(st.session_state.cg_explainer_result)
        _feedback("explain_ai_prev")


# ════════════════════════════════════════════════════════════════════
# TAB 5 — STREAMING SECURITY NUDGE
# ════════════════════════════════════════════════════════════════════
with tab_nudge:
    st.markdown("### 💡 Security Nudge")
    st.markdown('<p style="color:var(--text2);font-size:.85rem;">Get a quick, personalised, actionable security tip you can act on right now.</p>', unsafe_allow_html=True)

    if st.button("🔔  Get a Security Tip", type="primary", use_container_width=False, key="btn_nudge"):
        _neon()
        stream_ph = st.empty()
        full_ai = ""
        prompt = (
            f"{FEW_SHOTS.get('behavior','')}\n\n"
            "Give me ONE short, friendly, actionable cybersecurity tip I can act on right now. "
            "Keep it under 3 sentences. Be specific and practical."
        )
        if client.available:
            for chunk in client.stream(
                [{"role":"user","content":prompt}],
                system=SYSTEM_PROMPT
            ):
                full_ai += chunk
                stream_ph.markdown(full_ai + "▌")
            stream_ph.markdown(full_ai)
        else:
            full_ai = client.chat([{"role":"user","content":prompt}], system=SYSTEM_PROMPT)
            stream_ph.markdown(full_ai)
        st.session_state.cg_nudge_result = full_ai
        _feedback("nudge_ai")

    elif st.session_state.cg_nudge_result:
        st.info(st.session_state.cg_nudge_result)
        _feedback("nudge_ai_prev")


# ── FOOTER ────────────────────────────────────────────────────────────────────
_neon()
st.markdown("""
<p style="text-align:center;color:var(--text2);font-size:.76rem;">
  🛡️ <strong style="color:var(--text);">CyberGuard AI</strong>
  &nbsp;·&nbsp; IBM AI for Cybersecurity Project
  &nbsp;·&nbsp; NVIDIA NIM · mistralai/mistral-nemotron
  &nbsp;·&nbsp; ⚡ Streaming responses
  &nbsp;·&nbsp; 🔒 No personal data stored
</p>""", unsafe_allow_html=True)
