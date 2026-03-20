"""
🔍 AI Code Reviewer — Powered by Anthropic Claude
Pods, Prompts & Prototypes Hackathon | Containerized Code Intelligence

Paste your code, get expert-level reviews with suggestions, fixes, and explanations.
"""

import os
import anthropic
import streamlit as st
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter

# ── Config ────────────────────────────────────────────────────────────
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

# ── Page Setup ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Code Reviewer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600;700&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #161b22 50%, #0d1117 100%);
    }

    .main-header {
        text-align: center;
        padding: 1.5rem 0 0.8rem;
    }
    .main-header h1 {
        background: linear-gradient(90deg, #58a6ff, #bc8cff, #f778ba);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .main-header p { color: #8b949e; font-size: 1.05rem; }

    .review-card {
        background: rgba(22, 27, 34, 0.95);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }

    .severity-critical {
        border-left: 4px solid #f85149;
        background: rgba(248, 81, 73, 0.05);
    }
    .severity-warning {
        border-left: 4px solid #d29922;
        background: rgba(210, 153, 34, 0.05);
    }
    .severity-info {
        border-left: 4px solid #58a6ff;
        background: rgba(88, 166, 255, 0.05);
    }
    .severity-good {
        border-left: 4px solid #3fb950;
        background: rgba(63, 185, 80, 0.05);
    }

    .score-ring {
        width: 120px; height: 120px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 2rem; font-weight: 800; color: #e6edf3;
        margin: 0 auto 10px;
    }
    .score-low    { background: conic-gradient(#f85149 var(--pct), #21262d var(--pct)); }
    .score-mid    { background: conic-gradient(#d29922 var(--pct), #21262d var(--pct)); }
    .score-high   { background: conic-gradient(#3fb950 var(--pct), #21262d var(--pct)); }

    .metric-box {
        background: rgba(255,255,255,0.03);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .metric-box .value { font-size: 1.8rem; font-weight: 700; color: #e6edf3; }
    .metric-box .label { color: #8b949e; font-size: 0.85rem; }

    .pill {
        display: inline-block; padding: 3px 12px;
        border-radius: 16px; font-size: 0.78rem; font-weight: 600;
        margin: 2px;
    }
    .pill-red    { background: #3d1214; color: #f85149; }
    .pill-yellow { background: #3d2e00; color: #d29922; }
    .pill-blue   { background: #0c2d6b; color: #58a6ff; }
    .pill-green  { background: #0f291a; color: #3fb950; }

    .highlight pre {
        background: #0d1117 !important;
        border-radius: 8px;
        padding: 16px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem;
        overflow-x: auto;
    }

    section[data-testid="stSidebar"] {
        background: rgba(13, 17, 23, 0.95);
        border-right: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────
if "reviews" not in st.session_state:
    st.session_state.reviews = []
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("ANTHROPIC_API_KEY", "")

# ── Review Prompt ─────────────────────────────────────────────────────
REVIEW_SYSTEM = """You are a senior software engineer performing a thorough code review.
Analyze the provided code and return your review in the following structured format.
Be specific with line references. Be constructive and educational.

Return EXACTLY this format (do NOT wrap in markdown code fences):

SCORE: <number 0-100>

SUMMARY: <2-3 sentence overall assessment>

FINDINGS:
- CRITICAL | <title> | Line <N> | <description> | <suggested fix>
- WARNING | <title> | Line <N> | <description> | <suggested fix>
- INFO | <title> | Line <N> | <description> | <suggested fix>
- GOOD | <title> | Line <N> | <description of what's done well>

IMPROVED_CODE:
```
<the full improved version of the code>
```

EXPLANATION:
<paragraph explaining the key changes and why they matter>
"""


def parse_review(text: str) -> dict:
    """Parse the structured review response."""
    review = {"score": 0, "summary": "", "findings": [], "improved_code": "", "explanation": ""}

    lines = text.strip().split("\n")
    section = None
    buffer = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("SCORE:"):
            try:
                review["score"] = int(stripped.split(":", 1)[1].strip().split("/")[0].split()[0])
            except (ValueError, IndexError):
                review["score"] = 50

        elif stripped.startswith("SUMMARY:"):
            review["summary"] = stripped.split(":", 1)[1].strip()
            section = "summary"

        elif stripped == "FINDINGS:":
            section = "findings"

        elif stripped == "IMPROVED_CODE:":
            section = "improved_code"
            buffer = []

        elif stripped == "EXPLANATION:":
            if section == "improved_code":
                code = "\n".join(buffer)
                code = code.strip().removeprefix("```").removesuffix("```")
                # Also strip language identifier on first line
                code_lines = code.split("\n")
                if code_lines and code_lines[0].strip() in ("python", "javascript", "typescript", "java", "go", "rust", "c", "cpp", "ruby", ""):
                    code_lines = code_lines[1:]
                review["improved_code"] = "\n".join(code_lines).strip()
            section = "explanation"
            buffer = []

        elif section == "findings" and stripped.startswith("- "):
            parts = stripped[2:].split(" | ")
            if len(parts) >= 4:
                finding = {
                    "severity": parts[0].strip().lower(),
                    "title": parts[1].strip(),
                    "location": parts[2].strip(),
                    "description": parts[3].strip(),
                    "fix": parts[4].strip() if len(parts) > 4 else "",
                }
                review["findings"].append(finding)

        elif section == "improved_code":
            buffer.append(line)

        elif section == "explanation":
            buffer.append(line)

        elif section == "summary" and stripped:
            review["summary"] += " " + stripped

    if section == "explanation":
        review["explanation"] = "\n".join(buffer).strip()
    if section == "improved_code" and not review["improved_code"]:
        code = "\n".join(buffer)
        code = code.strip().removeprefix("```").removesuffix("```")
        review["improved_code"] = code.strip()

    return review


def do_review(code: str, language: str, focus: str, api_key: str) -> dict:
    """Send code to Anthropic for review."""
    client = anthropic.Anthropic(api_key=api_key)
    user_msg = f"Language: {language}\nFocus areas: {focus}\n\n```{language}\n{code}\n```"

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=4096,
        system=REVIEW_SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )

    return parse_review(response.content[0].text)


def render_severity_icon(sev: str) -> str:
    icons = {"critical": "🔴", "warning": "🟡", "info": "🔵", "good": "🟢"}
    return icons.get(sev, "⚪")


# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔑 API Configuration")
    api_key = st.text_input(
        "Anthropic API Key",
        value=st.session_state.api_key,
        type="password",
        help="Your key stays in-session only. Never stored.",
    )
    if api_key:
        st.session_state.api_key = api_key

    st.markdown("---")
    st.markdown("## 🎯 Review Settings")
    language = st.selectbox(
        "Language",
        ["python", "javascript", "typescript", "java", "go", "rust", "c", "cpp", "ruby", "other"],
        index=0,
    )
    focus = st.multiselect(
        "Focus Areas",
        ["Security", "Performance", "Readability", "Best Practices", "Error Handling", "Testing", "Type Safety"],
        default=["Security", "Best Practices", "Readability"],
    )

    st.markdown("---")
    st.markdown("## 📊 Session Stats")
    total_reviews = len(st.session_state.reviews)
    avg_score = (
        sum(r["score"] for r in st.session_state.reviews) / total_reviews
        if total_reviews > 0
        else 0
    )
    st.markdown(
        f"""<div class="metric-box"><div class="value">{total_reviews}</div><div class="label">Reviews Done</div></div>""",
        unsafe_allow_html=True,
    )
    st.markdown("")
    st.markdown(
        f"""<div class="metric-box"><div class="value">{avg_score:.0f}</div><div class="label">Avg Score</div></div>""",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        '<span class="pill pill-blue">Claude API</span>'
        '<span class="pill pill-green">Containerized</span>',
        unsafe_allow_html=True,
    )


# ── Main Area ─────────────────────────────────────────────────────────
st.markdown(
    """<div class="main-header">
        <h1>🔍 AI Code Reviewer</h1>
        <p>Paste your code → Get expert-level review → Ship better software<br>
        <em>Powered by Anthropic Claude · Containerized with Podman</em></p>
    </div>""",
    unsafe_allow_html=True,
)

# Code input
tab_paste, tab_upload = st.tabs(["✏️ Paste Code", "📁 Upload File"])

code_input = ""
with tab_paste:
    code_input = st.text_area(
        "Paste your code here",
        height=350,
        placeholder="def calculate_total(items):\n    total = 0\n    for i in items:\n        total = total + i['price'] * i['qty']\n    return total",
        key="code_paste",
    )

with tab_upload:
    uploaded_file = st.file_uploader(
        "Upload a source file",
        type=["py", "js", "ts", "java", "go", "rs", "c", "cpp", "rb", "txt"],
    )
    if uploaded_file:
        code_input = uploaded_file.read().decode("utf-8")
        st.code(code_input, language=language)

# Review button
col_btn, col_spacer = st.columns([1, 3])
with col_btn:
    review_clicked = st.button(
        "🚀 Review My Code",
        use_container_width=True,
        type="primary",
        disabled=not code_input or not st.session_state.api_key,
    )

if not st.session_state.api_key:
    st.info("🔑 Enter your Anthropic API key in the sidebar to get started.")

# Do the review
if review_clicked and code_input and st.session_state.api_key:
    with st.spinner("🤖 Claude is reviewing your code..."):
        try:
            result = do_review(code_input, language, ", ".join(focus), st.session_state.api_key)
            st.session_state.reviews.append(result)
        except anthropic.AuthenticationError:
            st.error("❌ Invalid API key. Please check your Anthropic API key.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Review failed: {e}")
            st.stop()

    # ── Results ───────────────────────────────────────────────────────
    st.markdown("---")

    # Score + Summary
    score = result["score"]
    score_class = "score-low" if score < 50 else ("score-mid" if score < 80 else "score-high")
    pct = f"{score}%"

    col_score, col_summary = st.columns([1, 3])
    with col_score:
        st.markdown(
            f"""<div class="score-ring {score_class}" style="--pct: {pct}">
                <span style="background:#0d1117;border-radius:50%;width:90px;height:90px;display:flex;align-items:center;justify-content:center;">
                    {score}
                </span>
            </div>
            <p style="text-align:center;color:#8b949e;font-size:0.9rem;">Quality Score</p>""",
            unsafe_allow_html=True,
        )

    with col_summary:
        st.markdown(f"""<div class="review-card">
            <h3 style="color:#e6edf3;margin-top:0;">📋 Summary</h3>
            <p style="color:#c9d1d9;line-height:1.6;">{result['summary']}</p>
        </div>""", unsafe_allow_html=True)

    # Findings
    if result["findings"]:
        st.markdown("### 🔎 Findings")
        for f in result["findings"]:
            sev = f["severity"]
            icon = render_severity_icon(sev)
            css_class = f"severity-{sev}"
            fix_html = f"<br><strong>💡 Fix:</strong> {f['fix']}" if f.get("fix") else ""

            st.markdown(
                f"""<div class="review-card {css_class}">
                    <strong>{icon} {f['title']}</strong>
                    <span class="pill pill-{'red' if sev == 'critical' else 'yellow' if sev == 'warning' else 'blue' if sev == 'info' else 'green'}">{sev.upper()}</span>
                    <span style="color:#8b949e;margin-left:8px;">{f['location']}</span>
                    <p style="color:#c9d1d9;margin:8px 0 0;">{f['description']}{fix_html}</p>
                </div>""",
                unsafe_allow_html=True,
            )

    # Improved code
    if result["improved_code"]:
        st.markdown("### ✨ Improved Code")
        col_orig, col_improved = st.columns(2)
        with col_orig:
            st.markdown("**Original**")
            st.code(code_input, language=language)
        with col_improved:
            st.markdown("**Improved**")
            st.code(result["improved_code"], language=language)

    # Explanation
    if result["explanation"]:
        st.markdown("### 📖 Explanation")
        st.markdown(
            f"""<div class="review-card severity-info">
                <p style="color:#c9d1d9;line-height:1.7;margin:0;">{result['explanation']}</p>
            </div>""",
            unsafe_allow_html=True,
        )

# Sample code examples
if not st.session_state.reviews:
    st.markdown("---")
    st.markdown("### 💡 Try one of these examples")

    ex1, ex2, ex3 = st.columns(3)

    with ex1:
        st.markdown("""<div class="review-card">
            <h4 style="color:#e6edf3;">🐍 Python — SQL Injection</h4>
            <p style="color:#8b949e;font-size:0.85rem;">A function with a common security vulnerability</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Load Example", key="ex1"):
            st.session_state["code_paste"] = '''def get_user(username):
    query = f"SELECT * FROM users WHERE name = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()'''
            st.rerun()

    with ex2:
        st.markdown("""<div class="review-card">
            <h4 style="color:#e6edf3;">⚡ Python — Performance</h4>
            <p style="color:#8b949e;font-size:0.85rem;">An inefficient data processing function</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Load Example", key="ex2"):
            st.session_state["code_paste"] = '''def find_duplicates(lst):
    duplicates = []
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if lst[i] == lst[j] and lst[i] not in duplicates:
                duplicates.append(lst[i])
    return duplicates'''
            st.rerun()

    with ex3:
        st.markdown("""<div class="review-card">
            <h4 style="color:#e6edf3;">🛡️ Python — Error Handling</h4>
            <p style="color:#8b949e;font-size:0.85rem;">A function that swallows errors silently</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Load Example", key="ex3"):
            st.session_state["code_paste"] = '''def read_config(path):
    try:
        f = open(path)
        data = eval(f.read())
        f.close()
        return data
    except:
        return {}'''
            st.rerun()
