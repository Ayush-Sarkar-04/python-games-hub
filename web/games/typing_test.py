"""Streamlit UI for Typing Test."""

import time

import streamlit as st

from games.typing_test import DIFFICULTIES, calculate_metrics, TypingTestGame
from engine.game import SessionConfig


def _ensure_state() -> dict:
    if "typing_test" not in st.session_state:
        st.session_state["typing_test"] = {"screen": "setup", "difficulty": "medium"}
    game = st.session_state["typing_test"]
    game.setdefault("difficulty", "medium")
    game.setdefault("text", "")
    game.setdefault("duration", 30)
    game.setdefault("started", None)
    game.setdefault("typed", "")
    game.setdefault("metrics", None)
    game.setdefault("score", 0)
    game.setdefault("screen", "setup")
    return game


def new_game() -> None:
    game = _ensure_state()
    config = st.session_state.get("typing_test_config", {})
    difficulty = config.get("difficulty", game["difficulty"])
    core = TypingTestGame()
    state = core.setup(SessionConfig(game="typing_test", difficulty=difficulty, mode="practice"))
    game.update({"screen": "game", "difficulty": difficulty, "text": state.data["text"],
                 "duration": state.data["duration"], "started": None, "typed": "",
                 "metrics": None, "score": 0})
    st.session_state["typing_test_input"] = ""


def render_setup() -> None:
    game = _ensure_state()
    st.title("Typing Test")
    st.caption("Type the passage accurately and quickly.")
    if "typing_test_setup_difficulty" not in st.session_state:
        st.session_state["typing_test_setup_difficulty"] = game["difficulty"].title()
    difficulty_label = st.radio(
        "Difficulty", ["Easy", "Medium", "Hard"],
        key="typing_test_setup_difficulty", horizontal=True,
    )
    difficulty = difficulty_label.lower()
    settings = DIFFICULTIES[difficulty]
    st.write(f"**{settings['name']}** • {settings['duration']} seconds")
    if st.button("Start Test", type="primary", use_container_width=True):
        st.session_state["typing_test_config"] = {"difficulty": difficulty}
        new_game()
        st.rerun()


@st.fragment(run_every=0.2)
def _render_active_test() -> None:
    game = _ensure_state()
    if game["started"] is None:
        return

    elapsed = max(0.0, time.monotonic() - game["started"])
    remaining = max(0.0, game["duration"] - elapsed)

    st.markdown("### Type the passage")
    st.markdown(
        f'<div class="typing-passage">{game["text"]}</div>',
        unsafe_allow_html=True,
    )

    st.progress(min(elapsed / game["duration"], 1.0))
    timer_col, count_col = st.columns(2)
    with timer_col:
        st.markdown(f"**Time remaining**  \n### {remaining:.1f}s")
    with count_col:
        current = st.session_state.get("typing_test_input", "")
        st.markdown(f"**Characters typed**  \n### {len(current)}")

    typed = st.text_area(
        "Your typing",
        key="typing_test_input",
        height=150,
        placeholder="Start typing the passage exactly as shown above...",
    )

    submit = st.button(
        "Submit Test",
        type="primary",
        use_container_width=True,
        key="typing_test_submit",
    )

    if submit or remaining <= 0:
        elapsed_for_score = max(min(elapsed, game["duration"]), 0.001)
        metrics = calculate_metrics(game["text"], typed, elapsed_for_score)
        game["typed"] = typed
        game["metrics"] = metrics
        game["score"] = metrics["score"]
        game["screen"] = "result"
        st.rerun()

    st.caption("Type exactly as shown. The test ends automatically when the timer reaches zero.")

def render_game() -> None:
    game = _ensure_state()
    st.title("Typing Test")
    duration = game.get("duration", game.get("duration_seconds", 30))
    st.caption(f"{game['difficulty'].title()} difficulty • {duration} seconds")

    if game["started"] is None:
        st.markdown("### Type this passage")
        st.code(game["text"])
        if st.button("Begin Typing", type="primary", use_container_width=True):
            game["started"] = time.monotonic()
            st.rerun()
        return

    st.markdown("""
    <style>
    .typing-passage {
        padding: 1.1rem 1.25rem;
        border: 1px solid rgba(128, 128, 128, 0.35);
        border-radius: 12px;
        background: rgba(255, 255, 255, 0.035);
        line-height: 1.75;
        font-size: 1.05rem;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    _render_active_test()

