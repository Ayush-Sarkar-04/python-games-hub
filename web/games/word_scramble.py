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
    st.title("Word Scramble")
    st.caption(f"{game['difficulty'].title()} difficulty • Attempt {min(game['attempts'] + 1, MAX_ATTEMPTS)}/{MAX_ATTEMPTS}")
    st.subheader("Unscramble this word")
    st.markdown(f"### {'  '.join(game['scrambled'].upper())}")
    if game["revealed"]: st.write(f"Hint: **{_render_hint(game)}**")
    if game["last_guess"] == "invalid": st.warning("Please enter letters only.")
    elif game["last_guess"] and game["last_guess"] != game["word"] and game["outcome"] is None:
        st.warning("Not quite. Try again.")
    if game["outcome"] == "win":
        st.success(f"Correct! The word was **{game['word'].upper()}**. Score: **{game['score']}**")
        return
    if game["outcome"] == "loss":
        st.error(f"Out of attempts. The word was **{game['word'].upper()}**.")
        return
    with st.form("word_scramble_guess_form"):
        guess = st.text_input("Your guess", placeholder="Enter the unscrambled word")
        if st.form_submit_button("Submit Guess", use_container_width=True):
            _submit_guess(guess)
            st.rerun()


def render_word_scramble() -> None:
    if _ensure_state()["screen"] == "setup": render_setup()
    else: render_game()