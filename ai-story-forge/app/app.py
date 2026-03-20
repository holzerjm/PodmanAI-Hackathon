"""
📖 AI Story Forge — Choose-Your-Own-Adventure with Local AI
Pods, Prompts & Prototypes Hackathon | Powered by Ollama

Pick a genre, make choices, and watch an interactive story unfold.
"""

import os
import re
import ollama
import streamlit as st

# ── Config ────────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "granite3.1-dense:8b")
MAX_TURNS = 10

# ── Page Setup ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Story Forge",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

    .stApp {
        background: linear-gradient(135deg, #1a0a2e 0%, #16213e 50%, #0f3460 100%);
    }

    .main-header {
        text-align: center;
        padding: 1.5rem 0 1rem;
    }
    .main-header h1 {
        background: linear-gradient(90deg, #f9d423, #ff4e50, #bc2cff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }
    .main-header p {
        color: #8892b0;
        font-size: 1.1rem;
    }

    .story-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 12px;
        font-family: 'Crimson Text', serif;
        font-size: 1.15rem;
        line-height: 1.7;
        color: #e2e8f0;
    }

    .player-choice {
        background: rgba(249, 212, 35, 0.06);
        border-left: 3px solid #f9d423;
        border-radius: 0 12px 12px 0;
        padding: 12px 18px;
        margin-bottom: 12px;
        color: #f9d423;
        font-style: italic;
        font-size: 1rem;
    }

    .choice-btn {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 8px;
        color: #e2e8f0;
        transition: all 0.2s;
    }
    .choice-btn:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: #f9d423;
    }

    .ending-card {
        background: linear-gradient(135deg, rgba(249, 212, 35, 0.08), rgba(188, 44, 255, 0.08));
        border: 1px solid rgba(249, 212, 35, 0.3);
        border-radius: 16px;
        padding: 24px 28px;
        margin: 20px 0;
        text-align: center;
    }
    .ending-card h2 {
        background: linear-gradient(90deg, #f9d423, #ff4e50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
    }

    .genre-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        transition: all 0.2s;
    }
    .genre-card:hover {
        background: rgba(255, 255, 255, 0.08);
    }
    .genre-card .icon { font-size: 2.5rem; }
    .genre-card .name { color: #e2e8f0; font-weight: 600; margin-top: 6px; }

    .status-pill {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 2px 4px;
    }
    .pill-green  { background: #064e3b; color: #6ee7b7; }
    .pill-blue   { background: #1e3a5f; color: #7dd3fc; }
    .pill-purple { background: #3b0764; color: #c084fc; }

    section[data-testid="stSidebar"] {
        background: rgba(26, 10, 46, 0.9);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State ─────────────────────────────────────────────────────
if "story_parts" not in st.session_state:
    st.session_state.story_parts = []
if "choices" not in st.session_state:
    st.session_state.choices = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0
if "story_active" not in st.session_state:
    st.session_state.story_active = False
if "story_finished" not in st.session_state:
    st.session_state.story_finished = False


# ── Ollama Client ─────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    return ollama.Client(host=OLLAMA_BASE_URL)


# ── Prompt Engineering ────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an interactive fiction narrator. You write vivid, engaging \
choose-your-own-adventure stories. You must ALWAYS respond in this exact format:

STORY: <A compelling narrative paragraph of 2-4 sentences advancing the story. Be descriptive and immersive.>

CHOICE_1: <First option — an action the player can take>
CHOICE_2: <Second option — a different action>
CHOICE_3: <Third option — a surprising or creative action>

Rules:
- ALWAYS include exactly 3 choices
- Keep each choice to one short sentence
- Make choices meaningfully different from each other
- Build on the player's previous choices naturally
- Never break character or mention you are an AI"""

ENDING_PROMPT = """You are an interactive fiction narrator. The story is reaching its \
climax and must end NOW. Write a dramatic, satisfying conclusion in 3-5 sentences. \
Do NOT offer any choices. Wrap up all loose threads and give the player a memorable ending.

Respond in this format:
STORY: <The dramatic conclusion of the adventure>
THE_END"""


def parse_response(text: str) -> dict:
    """Parse structured response into story text and choices."""
    result = {"story": "", "choices": []}

    # Extract story text
    story_match = re.search(r"STORY:\s*(.+?)(?=CHOICE_1:|THE_END|$)", text, re.DOTALL)
    if story_match:
        result["story"] = story_match.group(1).strip()
    else:
        # Fallback: take everything before the first numbered choice
        lines = text.strip().split("\n")
        story_lines = []
        for line in lines:
            if re.match(r"(CHOICE_\d|^\d+[\.\)])", line.strip()):
                break
            story_lines.append(line)
        result["story"] = "\n".join(story_lines).strip()

    # Extract choices
    for i in range(1, 4):
        choice_match = re.search(rf"CHOICE_{i}:\s*(.+?)(?=CHOICE_{i+1}:|THE_END|$)", text, re.DOTALL)
        if choice_match:
            result["choices"].append(choice_match.group(1).strip())

    # Fallback: try numbered list format (1. / 2. / 3.)
    if not result["choices"]:
        numbered = re.findall(r"\d+[\.\)]\s*(.+)", text)
        if len(numbered) >= 3:
            result["choices"] = [c.strip() for c in numbered[:3]]

    # Check for ending
    if "THE_END" in text:
        result["choices"] = []

    return result


def build_messages(genre: str) -> list:
    """Build the message history for the Ollama API call."""
    messages = []

    # Only include the last 5 turns to stay within context limits
    recent_parts = st.session_state.story_parts
    if len(recent_parts) > 10:
        recent_parts = recent_parts[-10:]

    for part in recent_parts:
        if part["role"] == "narrator":
            messages.append({"role": "assistant", "content": f"STORY: {part['text']}"})
        else:
            messages.append({"role": "user", "content": f"I choose: {part['text']}"})

    return messages


def generate_turn(genre: str, model: str, temperature: float, player_choice: str = None):
    """Generate the next story turn."""
    client = get_client()

    is_final = st.session_state.turn_count >= MAX_TURNS - 1
    system = ENDING_PROMPT if is_final else SYSTEM_PROMPT

    messages = build_messages(genre)

    if player_choice:
        messages.append({"role": "user", "content": f"I choose: {player_choice}"})
    else:
        messages.append({
            "role": "user",
            "content": f"Start a new {genre} choose-your-own-adventure story. "
                       f"Set the scene with a compelling, atmospheric opening.",
        })

    response = client.chat(
        model=model,
        messages=[{"role": "system", "content": system}] + messages,
        options={"temperature": temperature},
    )

    return parse_response(response["message"]["content"])


# ── Genre Config ──────────────────────────────────────────────────────
GENRES = {
    "Fantasy": "🏰",
    "Sci-Fi": "🚀",
    "Mystery": "🔎",
    "Horror": "👻",
    "Pirate Adventure": "🏴‍☠️",
    "Space Western": "🤠",
    "Fairy Tale": "🧚",
    "Superhero": "🦸",
}


# ── Sidebar ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")

    genre = st.selectbox("Genre", list(GENRES.keys()), index=0)
    model = st.selectbox(
        "Ollama Model",
        ["granite3.1-dense:8b", "qwen2.5:7b", "mistral:7b", "llama3.1:8b"],
        index=0,
    )
    temperature = st.slider("Creativity", 0.5, 1.0, 0.8, 0.05)

    st.markdown("---")
    st.markdown("## 📊 Adventure Stats")
    st.markdown(
        f'<div style="background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);'
        f'border-radius:10px;padding:16px;text-align:center;">'
        f'<div style="font-size:1.8rem;font-weight:700;color:#e2e8f0;">{st.session_state.turn_count}</div>'
        f'<div style="color:#8892b0;font-size:0.85rem;">Turns Taken</div></div>',
        unsafe_allow_html=True,
    )

    if st.session_state.story_active:
        st.markdown("")
        progress = st.session_state.turn_count / MAX_TURNS
        st.progress(progress, text=f"Story progress: {st.session_state.turn_count}/{MAX_TURNS}")

    st.markdown("---")
    st.markdown(
        '<span class="status-pill pill-green">🟢 Local AI</span>'
        '<span class="status-pill pill-blue">🔵 Ollama</span>'
        '<span class="status-pill pill-purple">🟣 Beginner</span>',
        unsafe_allow_html=True,
    )

    if st.session_state.story_active or st.session_state.story_finished:
        st.markdown("---")
        if st.button("🔄 New Story", use_container_width=True):
            st.session_state.story_parts = []
            st.session_state.choices = []
            st.session_state.turn_count = 0
            st.session_state.story_active = False
            st.session_state.story_finished = False
            st.rerun()


# ── Main Area ─────────────────────────────────────────────────────────
st.markdown(
    """<div class="main-header">
        <h1>📖 AI Story Forge</h1>
        <p>Choose your path. Shape your story. Powered by local AI.<br>
        <em>100% local · Ollama · Zero cloud dependency</em></p>
    </div>""",
    unsafe_allow_html=True,
)

# Stats row
c1, c2, c3, c4 = st.columns(4)
c1.metric("📖 Genre", genre)
c2.metric("🎲 Turn", f"{st.session_state.turn_count}/{MAX_TURNS}")
c3.metric("🤖 Model", model.split(":")[0])
status = "Finished" if st.session_state.story_finished else ("Playing" if st.session_state.story_active else "Ready")
c4.metric("📡 Status", status)

st.markdown("---")

# ── Start Screen ──────────────────────────────────────────────────────
if not st.session_state.story_active and not st.session_state.story_finished:
    st.markdown("### 👋 Welcome, Adventurer!")
    st.markdown("Pick a genre from the sidebar and begin your journey. "
                "Every choice you make shapes the story — no two adventures are alike.")

    st.markdown("")

    # Genre showcase
    cols = st.columns(4)
    for i, (g, icon) in enumerate(GENRES.items()):
        with cols[i % 4]:
            st.markdown(
                f'<div class="genre-card">'
                f'<div class="icon">{icon}</div>'
                f'<div class="name">{g}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("")
    col_btn, col_space = st.columns([1, 3])
    with col_btn:
        if st.button("⚔️ Begin Your Adventure", use_container_width=True, type="primary"):
            with st.spinner("🌍 The world takes shape..."):
                result = generate_turn(genre, model, temperature)

            st.session_state.story_parts.append({"role": "narrator", "text": result["story"]})
            st.session_state.choices = result["choices"]
            st.session_state.turn_count = 1
            st.session_state.story_active = True
            st.rerun()

# ── Story Display ─────────────────────────────────────────────────────
if st.session_state.story_active or st.session_state.story_finished:
    for part in st.session_state.story_parts:
        if part["role"] == "narrator":
            st.markdown(
                f'<div class="story-card">{part["text"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="player-choice">▸ {part["text"]}</div>',
                unsafe_allow_html=True,
            )

# ── Story Ending ──────────────────────────────────────────────────────
if st.session_state.story_finished:
    st.markdown(
        '<div class="ending-card">'
        '<h2>📜 The End</h2>'
        '<p style="color:#c9d1d9;">Your adventure has concluded. '
        'Start a new story to explore a different path!</p></div>',
        unsafe_allow_html=True,
    )
    col_restart, _ = st.columns([1, 3])
    with col_restart:
        if st.button("🔄 Start New Adventure", use_container_width=True, type="primary"):
            st.session_state.story_parts = []
            st.session_state.choices = []
            st.session_state.turn_count = 0
            st.session_state.story_active = False
            st.session_state.story_finished = False
            st.rerun()

# ── Choice Buttons ────────────────────────────────────────────────────
if st.session_state.story_active and st.session_state.choices:
    st.markdown("### ⚔️ What do you do?")
    cols = st.columns(3)

    for i, choice in enumerate(st.session_state.choices):
        with cols[i]:
            if st.button(choice, key=f"choice_{st.session_state.turn_count}_{i}", use_container_width=True):
                # Record the player's choice
                st.session_state.story_parts.append({"role": "player", "text": choice})

                # Generate next turn
                with st.spinner("📖 The story unfolds..."):
                    result = generate_turn(genre, model, temperature, player_choice=choice)

                st.session_state.story_parts.append({"role": "narrator", "text": result["story"]})
                st.session_state.turn_count += 1

                if not result["choices"] or st.session_state.turn_count >= MAX_TURNS:
                    st.session_state.choices = []
                    st.session_state.story_active = False
                    st.session_state.story_finished = True
                else:
                    st.session_state.choices = result["choices"]

                st.rerun()
