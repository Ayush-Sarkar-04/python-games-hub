"""Streamlit UI for Typing Test."""

import time

import streamlit as st

from engine.game import SessionConfig
from games.typing_test import DIFFICULTIES, TypingTestGame, calculate_metrics


def _ensure_state() -> dict:
    if "typing_test" not in st.session_state:
        st.session_state["typing_test"] = {
            "screen": "setup",
            "difficulty": "medium",
            "text": "",
            "duration": 30,
            "started": None,
            "typed": "",
            "metrics": None,
            "score": 0,
        }

    game = st.session_state["typing_test"]
    game.setdefault("screen", "setup")
    game.setdefault("difficulty", "medium")
    game.setdefault("text", "")
    game.setdefault("duration", 30)
    game.setdefault("started", None)
    game.setdefault("typed", "")
    game.setdefault("metrics", None)
    game.setdefault("score", 0)
    return game


def _sync_setup_preferences() -> None:
    game = _ensure_state()
    game["difficulty"] = st.session_state["typing_test_setup_difficulty"].lower()


def new_game() -> None:
    game = _ensure_state()
    difficulty = game["difficulty"]

    state = TypingTestGame().setup(
        SessionConfig(
            game="typing_test",
            difficulty=difficulty,
            mode="practice",
        )
    )

    game.update(
        {
            "screen": "game",
            "difficulty": difficulty,
            "text": state.data["text"],
            "duration": state.data["duration"],
            "started": None,
            "typed": "",
            "metrics": None,
            "score": 0,
        }
    )
    st.session_state["typing_test_input"] = ""


def render_setup() -> None:
    game = _ensure_state()

    st.title("Typing Test")
    st.caption("Type the passage accurately and quickly.")

    if "typing_test_setup_difficulty" not in st.session_state:
        st.session_state["typing_test_setup_difficulty"] = game["difficulty"].title()

    difficulty_label = st.radio(
        "Difficulty",
        ["Easy", "Medium", "Hard"],
        key="typing_test_setup_difficulty",
        horizontal=True,
        on_change=_sync_setup_preferences,
    )
    difficulty = difficulty_label.lower()
    settings = DIFFICULTIES[difficulty]

    st.write(f"**{settings['name']}** · {settings['duration']} seconds")

    if st.button("Start Test", type="primary", use_container_width=True):
        game["difficulty"] = difficulty
        new_game()
        st.rerun()


def _render_passage(game: dict) -> None:
    st.markdown("### Type the passage")
    with st.container(border=True):
        st.markdown(
            f'<div class="typing-passage">{game["text"]}</div>',
            unsafe_allow_html=True,
        )


def _finish_test(game: dict, typed: str, elapsed: float) -> None:
    elapsed_for_score = max(min(elapsed, game["duration"]), 0.001)
    metrics = calculate_metrics(game["text"], typed, elapsed_for_score)
    game["typed"] = typed
    game["metrics"] = metrics
    game["score"] = metrics["score"]
    game["screen"] = "result"
    game["started"] = None


@st.fragment(run_every=0.2)
def _render_live_test() -> None:
    game = _ensure_state()
    if game["screen"] != "game" or game["started"] is None:
        return

    elapsed = max(0.0, time.monotonic() - game["started"])
    remaining = max(0.0, game["duration"] - elapsed)

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
        _finish_test(game, typed, elapsed)
        st.rerun()

    st.caption("Type exactly as shown. The test ends automatically when the timer reaches zero.")


def _render_result(game: dict) -> None:
    metrics = game.get("metrics") or {}

    st.markdown("### Test complete")

    result_cols = st.columns(3)
    values = [
        ("WPM", f'{metrics.get("wpm", 0):.2f}'),
        ("Accuracy", f'{metrics.get("accuracy", 0):.2f}%'),
        ("Score", str(metrics.get("score", 0))),
    ]

    for column, (label, value) in zip(result_cols, values):
        with column:
            st.metric(label, value)

    st.caption(
        f'{metrics.get("correct_characters", 0)} correct characters out of '
        f'{metrics.get("typed_characters", 0)} typed.'
    )

    if st.button("New Test", type="primary", use_container_width=True):
        new_game()
        st.rerun()


def render_game() -> None:
    game = _ensure_state()

    st.markdown(
        """
        <style>
        .typing-passage {
            padding: 1.1rem 1.25rem;
            line-height: 1.75;
            font-size: 1.05rem;
            color: #f3f4f6;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Typing Test")
    st.caption(f'{game["difficulty"].title()} difficulty · {game["duration"]} seconds')

    if game["screen"] == "result":
        _render_result(game)
        return

    _render_passage(game)

    if game["started"] is None:
        if st.button("Begin Typing", type="primary", use_container_width=True):
            game["started"] = time.monotonic()
            game["screen"] = "game"
            st.session_state["typing_test_input"] = ""
            st.rerun()
        return

    _render_live_test()
