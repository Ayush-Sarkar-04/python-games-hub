"""Streamlit web implementation of Word Scramble."""

import streamlit as st

from games.word_scramble import (
    DIFFICULTY, HINT_SCHEDULE, MAX_ATTEMPTS, SCORE_BY_ATTEMPT,
    get_word, reveal_more_letters, scramble_word,
)


def _new_state() -> dict:
    difficulty = "easy"
    word = get_word(difficulty)
    return {"screen": "setup", "difficulty": difficulty, "word": word,
            "scrambled": scramble_word(word), "attempts": 0, "revealed": set(),
            "score": 0, "outcome": None, "last_guess": None}


def reset_word_scramble() -> None:
    st.session_state["word_scramble"] = _new_state()


def _ensure_state() -> dict:
    if "word_scramble" not in st.session_state:
        reset_word_scramble()
    return st.session_state["word_scramble"]


def _start_game(difficulty: str) -> None:
    word = get_word(difficulty)
    game = _ensure_state()
    game.update({"screen": "game", "difficulty": difficulty, "word": word,
                 "scrambled": scramble_word(word), "attempts": 0, "revealed": set(),
                 "score": 0, "outcome": None, "last_guess": None})


def new_game() -> None:
    _start_game(_ensure_state()["difficulty"])


def _submit_guess(guess: str) -> None:
    game = _ensure_state()
    if game["outcome"] is not None: return
    guess = guess.strip().lower()
    if not guess.isalpha():
        game["last_guess"] = "invalid"
        return
    game["last_guess"] = guess
    game["attempts"] += 1
    if guess == game["word"]:
        game["score"] = SCORE_BY_ATTEMPT[game["attempts"]]
        game["outcome"] = "win"
        return
    remaining = MAX_ATTEMPTS - game["attempts"]
    if remaining:
        first_hint, last_hint = HINT_SCHEDULE[game["difficulty"]]
        if game["attempts"] == 1:
            reveal_more_letters(game["word"], game["revealed"], first_hint)
        if remaining == 1:
            reveal_more_letters(game["word"], game["revealed"], last_hint)
    if game["attempts"] >= MAX_ATTEMPTS:
        game["outcome"] = "loss"


def _render_hint(game: dict) -> str:
    return "  ".join(letter.upper() if index in game["revealed"] else "_"
                       for index, letter in enumerate(game["word"]))


def render_setup() -> None:
    game = _ensure_state()
    st.title("Word Scramble")
    st.caption("Unscramble the word before you run out of attempts.")
    difficulty_label = st.radio("Difficulty", ["Easy", "Medium", "Hard"],
                                index=["easy", "medium", "hard"].index(game["difficulty"]),
                                horizontal=True)
    difficulty = difficulty_label.lower()
    title, min_length, max_length = DIFFICULTY[difficulty]
    st.write(f"**{title}** • Word length: {min_length}–{max_length} letters • {MAX_ATTEMPTS} attempts")
    if st.button("Start Game", type="primary", use_container_width=True):
        _start_game(difficulty)
        st.rerun()


def render_game() -> None:
    game = _ensure_state()

    st.markdown(
        """
        <style>
        .ws-round {
            display: inline-block;
            padding: 7px 14px;
            border-radius: 999px;
            background: #1f2937;
            border: 1px solid #374151;
            font-size: 0.85rem;
            margin-bottom: 18px;
        }
        .ws-word-card {
            text-align: center;
            padding: 28px 24px;
            border-radius: 18px;
            background: #151922;
            border: 1px solid #303642;
            margin: 10px 0 18px 0;
        }
        .ws-label {
            font-size: 0.78rem;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 16px;
        }
        .ws-letters {
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 8px;
        }
        .ws-letter {
            width: 46px;
            height: 52px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 10px;
            background: #202531;
            border: 1px solid #3b4352;
            font-size: 1.45rem;
            font-weight: 800;
        }
        .ws-hint {
            text-align: center;
            padding: 14px;
            border-radius: 12px;
            background: #1a202b;
            border: 1px dashed #3b4352;
            margin: 12px 0;
            font-size: 1rem;
            letter-spacing: 0.08em;
        }
        .ws-stat {
            text-align: center;
            padding: 14px 10px;
            border-radius: 14px;
            background: #151922;
            border: 1px solid #303642;
        }
        .ws-stat-label {
            font-size: 0.75rem;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .ws-stat-value {
            font-size: 1.5rem;
            font-weight: 800;
            margin-top: 4px;
        }
        .ws-feedback {
            min-height: 42px;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 10px 14px;
            border-radius: 10px;
            margin: 12px 0 16px 0;
            background: #241f12;
            border: 1px solid #5b4f1f;
            color: #f4e7a1;
            font-size: 0.9rem;
        }
        .ws-feedback.empty {
            visibility: hidden;
        }
        .ws-result {
            text-align: center;
            padding: 18px;
            border-radius: 14px;
            background: #151922;
            border: 1px solid #303642;
            margin: 16px 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, center, right = st.columns([1, 4, 1])
    with center:
        st.title("Word Scramble")
        st.markdown(
            f'<div class="ws-round">ATTEMPT {min(game["attempts"] + 1, MAX_ATTEMPTS)} / {MAX_ATTEMPTS}'
            f' &nbsp; • &nbsp; {game["difficulty"].upper()}</div>',
            unsafe_allow_html=True,
        )

        letters = "".join(
            f'<div class="ws-letter">{letter}</div>'
            for letter in game["scrambled"].upper()
        )
        st.markdown(
            f'<div class="ws-word-card"><div class="ws-label">Unscramble the word</div>'
            f'<div class="ws-letters">{letters}</div></div>',
            unsafe_allow_html=True,
        )

        if game["revealed"]:
            st.markdown(
                f'<div class="ws-hint">HINT &nbsp; {_render_hint(game)}</div>',
                unsafe_allow_html=True,
            )

        stats = st.columns(2)
        with stats[0]:
            st.markdown(
                f'<div class="ws-stat"><div class="ws-stat-label">Attempts Used</div>'
                f'<div class="ws-stat-value">{game["attempts"]} / {MAX_ATTEMPTS}</div></div>',
                unsafe_allow_html=True,
            )
        with stats[1]:
            st.markdown(
                f'<div class="ws-stat"><div class="ws-stat-label">Current Score</div>'
                f'<div class="ws-stat-value">{game["score"]}</div></div>',
                unsafe_allow_html=True,
            )

        feedback = ""
        if game["last_guess"] == "invalid":
            feedback = "Please enter letters only."
        elif game["last_guess"] and game["last_guess"] != game["word"] and game["outcome"] is None:
            feedback = "Not quite. Try again."

        feedback_class = "ws-feedback" if feedback else "ws-feedback empty"
        st.markdown(
            f'<div class="{feedback_class}">{feedback or " "}</div>',
            unsafe_allow_html=True,
        )

        if game["outcome"] == "win":
            st.markdown(
                f'<div class="ws-result"><strong>CORRECT!</strong><br>'
                f'The word was <strong>{game["word"].upper()}</strong><br>'
                f'Score: <strong>{game["score"]}</strong></div>',
                unsafe_allow_html=True,
            )
            return

        if game["outcome"] == "loss":
            st.markdown(
                f'<div class="ws-result"><strong>OUT OF ATTEMPTS</strong><br>'
                f'The word was <strong>{game["word"].upper()}</strong></div>',
                unsafe_allow_html=True,
            )
            return

        st.subheader("Your guess")
        with st.form("word_scramble_guess_form"):
            guess = st.text_input(
                "Enter the unscrambled word",
                placeholder="Type your answer here...",
                label_visibility="collapsed",
            )
            if st.form_submit_button("SUBMIT GUESS", use_container_width=True, type="primary"):
                _submit_guess(guess)
                st.rerun()

def render_word_scramble() -> None:
    if _ensure_state()["screen"] == "setup": render_setup()
    else: render_game()