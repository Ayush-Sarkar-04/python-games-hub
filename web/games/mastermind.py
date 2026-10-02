"""Streamlit UI for Mastermind."""

import streamlit as st

from engine.game import SessionConfig

from games.mastermind import DIFFICULTIES, MastermindGame, evaluate_guess, validate_guess


def _ensure_state() -> dict:
    if "mastermind" not in st.session_state:
        st.session_state["mastermind"] = {"screen": "setup", "difficulty": "medium"}
    return st.session_state["mastermind"]


def new_game() -> None:
    game = _ensure_state()
    difficulty = game["difficulty"]
    core = MastermindGame()
    config = SessionConfig(game="mastermind", difficulty=difficulty, mode="practice")
    state = core.setup(config)
    game.update({
        "screen": "game",
        "code": state.data["code"],
        "attempts": 0,
        "history": [],
        "max_attempts": state.data["max_attempts"],
        "colors": DIFFICULTIES[difficulty]["colors"],
        "length": DIFFICULTIES[difficulty]["length"],
        "message": "",
        "outcome": None,
        "score": 0,
    })


def render_setup() -> None:
    game = _ensure_state()
    st.title("Mastermind")
    st.caption("Crack the hidden color code.")
    if "mastermind_setup_difficulty" not in st.session_state:
        st.session_state["mastermind_setup_difficulty"] = game["difficulty"].title()
    difficulty_label = st.radio(
        "Difficulty", ["Easy", "Medium", "Hard"],
        key="mastermind_setup_difficulty", horizontal=True,
    )
    difficulty = difficulty_label.lower()
    settings = DIFFICULTIES[difficulty]
    st.write(
        f"**{settings['name']}** • {settings['length']} colors • "
        f"{settings['attempts']} attempts • Available: {' '.join(settings['colors'])}"
    )
    if st.button("Start Game", type="primary", use_container_width=True):
        game["difficulty"] = difficulty
        new_game()
        st.rerun()


def render_game() -> None:
    game = _ensure_state()
    st.title("Mastermind")
    st.caption(
        f"{game['difficulty'].title()} difficulty • "
        f"Attempt {game['attempts'] + 1} of {game['max_attempts']}"
    )
    if game["history"]:
        st.subheader("Previous Guesses")
        for guess, exact, misplaced in game["history"]:
            st.write(f"{' '.join(guess)} — Exact: {exact} • Misplaced: {misplaced}")

    st.markdown("**Available colors:** " + " · ".join(game["colors"]))
    raw = st.text_input(
        f"Enter {game['length']} colors separated by spaces",
        key="mastermind_guess",
        disabled=game["outcome"] is not None,
    )
    if st.button("Submit Guess", type="primary", use_container_width=True):
        try:
            guess = validate_guess(raw, game["difficulty"])
        except ValueError as exc:
            game["message"] = str(exc)
            st.rerun()
        else:
            exact, misplaced = evaluate_guess(tuple(game["code"]), guess)
            game["attempts"] += 1
            game["history"].append((guess, exact, misplaced))
            game["message"] = f"Exact: {exact} • Misplaced: {misplaced}"
            if exact == game["length"]:
                game["outcome"] = "win"
                game["score"] = (game["max_attempts"] - game["attempts"] + 1) * 10
            elif game["attempts"] >= game["max_attempts"]:
                game["outcome"] = "loss"
            st.rerun()

    if game["message"]:
        st.info(game["message"])

    if game["outcome"] == "win":
        st.success(f"You cracked the code! Score: {game['score']}")
    elif game["outcome"] == "loss":
        st.error(f"Game over. The code was: {' '.join(game['code'])}")
    if game["outcome"] is not None:
        if st.button("Play Again", type="primary", use_container_width=True):
            new_game()
            st.rerun()


def render_mastermind() -> None:
    if _ensure_state()["screen"] == "setup":
        render_setup()
    else:
        render_game()
