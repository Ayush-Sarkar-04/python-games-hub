"""Streamlit web implementation of Hangman."""

import streamlit as st

from games.hangman import DIFFICULTIES, HANGMAN_STAGES, get_words, word_complete


def _new_state() -> dict:
    words = get_words()
    category = next(iter(words))
    return {
        "screen": "setup",
        "words": words,
        "category": category,
        "difficulty": "easy",
        "word": "",
        "guessed": set(),
        "attempts": 0,
        "max_attempts": DIFFICULTIES["easy"]["attempts"],
        "hint_used": False,
        "outcome": None,
        "message": "",
    }


def _ensure_state() -> dict:
    if "hangman" not in st.session_state:
        st.session_state["hangman"] = _new_state()
    return st.session_state["hangman"]


def reset_hangman() -> None:
    st.session_state["hangman"] = _new_state()


def _start_game(difficulty: str, category: str) -> None:
    game = _ensure_state()
    settings = DIFFICULTIES[difficulty]
    candidates = [
        word.lower()
        for word in game["words"][category]["words"]
        if settings["min_length"] <= len(word) <= settings["max_length"]
        and word.isalpha()
    ]
    if not candidates:
        candidates = [word.lower() for word in game["words"][category]["words"] if word.isalpha()]
    import random
    game.update({
        "screen": "game",
        "difficulty": difficulty,
        "category": category,
        "word": random.choice(candidates),
        "guessed": set(),
        "attempts": 0,
        "max_attempts": settings["attempts"],
        "hint_used": False,
        "outcome": None,
        "message": "",
    })


def new_game() -> None:
    game = _ensure_state()
    _start_game(game["difficulty"], game["category"])


def _guess(letter: str) -> None:
    game = _ensure_state()
    if game["outcome"] is not None or letter in game["guessed"]:
        return
    game["message"] = ""
    game["guessed"].add(letter)
    if letter not in game["word"]:
        game["attempts"] += 1
        game["message"] = "Wrong guess."
    else:
        game["message"] = "Good guess!"
    if word_complete(game["word"], game["guessed"]):
        game["outcome"] = "win"
    elif game["attempts"] >= game["max_attempts"]:
        game["outcome"] = "loss"


def _use_hint() -> None:
    game = _ensure_state()
    if game["hint_used"] or game["outcome"] is not None:
        return
    remaining = [letter for letter in game["word"] if letter not in game["guessed"]]
    if not remaining:
        return
    import random
    letter = random.choice(remaining)
    game["guessed"].add(letter)
    game["hint_used"] = True
    game["attempts"] += 1
    game["message"] = f"Hint revealed: {letter.upper()} (-1 attempt)"
    if word_complete(game["word"], game["guessed"]):
        game["outcome"] = "win"
    elif game["attempts"] >= game["max_attempts"]:
        game["outcome"] = "loss"


def render_setup() -> None:
    game = _ensure_state()
    st.title("Hangman")
    st.caption("Guess the hidden word before you run out of attempts.")

    labels = list(game["words"])
    current = game["category"]
    category_label = st.radio(
        "Category",
        labels,
        index=labels.index(current),
        format_func=lambda value: game["words"][value]["name"],
        horizontal=True,
    )
    difficulty_label = st.radio(
        "Difficulty",
        ["Easy", "Medium", "Hard"],
        index=["easy", "medium", "hard"].index(game["difficulty"]),
        horizontal=True,
    )
    difficulty = difficulty_label.lower()
    settings = DIFFICULTIES[difficulty]
    st.write(
        f"**{game['words'][category_label]['name']}** • "
        f"{settings['min_length']}–{settings['max_length']} letters • "
        f"{settings['attempts']} attempts"
    )
    if st.button("Start Game", type="primary", use_container_width=True):
        _start_game(difficulty, category_label)
        st.rerun()


def render_game() -> None:
    game = _ensure_state()
    st.markdown(
        """
        <style>
        .hm-stage{font-family:monospace;white-space:pre;display:flex;justify-content:center;
        background:#151922;border:1px solid #303642;border-radius:16px;padding:18px;
        font-size:1rem;line-height:1.25;}
        .hm-word{text-align:center;font-size:2rem;font-weight:800;letter-spacing:.22em;
        padding:18px;border-radius:14px;background:#151922;border:1px solid #303642;}
        .hm-stat{text-align:center;padding:10px;border-radius:10px;background:#151922;
        border:1px solid #303642;}
        .hm-label{font-size:.72rem;color:#9ca3af;text-transform:uppercase;letter-spacing:.08em;}
        .hm-value{font-size:1.15rem;font-weight:800;margin-top:3px;}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("Hangman")
    st.caption(
        f"{game['words'][game['category']]['name']} • "
        f"{game['difficulty'].title()} difficulty"
    )

    stage = HANGMAN_STAGES[min(game["attempts"], len(HANGMAN_STAGES) - 1)]
    st.markdown(f'<div class="hm-stage">{stage}</div>', unsafe_allow_html=True)

    word_display = " ".join(
        letter.upper() if letter in game["guessed"] else "_"
        for letter in game["word"]
    )
    st.markdown(f'<div class="hm-word">{word_display}</div>', unsafe_allow_html=True)

    stats = st.columns(3)
    values = [
        ("Attempts Left", game["max_attempts"] - game["attempts"]),
        ("Guessed", len(game["guessed"])),
        ("Hint", "Used" if game["hint_used"] else "Available"),
    ]
    for col, (label, value) in zip(stats, values):
        with col:
            st.markdown(
                f'<div class="hm-stat"><div class="hm-label">{label}</div>'
                f'<div class="hm-value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    if game["message"] and game["outcome"] is None:
        st.info(game["message"])

    if game["outcome"] is not None:
        if game["outcome"] == "win":
            st.success(f"You won! The word was **{game['word'].upper()}**.")
        else:
            st.error(f"Game over. The word was **{game['word'].upper()}**.")
        return

    hint_col, _ = st.columns([1, 4])
    with hint_col:
        st.button(
            "Use Hint",
            key="hangman_hint",
            disabled=game["hint_used"],
            on_click=_use_hint,
            use_container_width=True,
        )

    st.subheader("Choose a letter")
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    for start in range(0, 26, 7):
        cols = st.columns(7)
        for col, letter in zip(cols, alphabet[start:start + 7]):
            with col:
                st.button(
                    letter.upper(),
                    key=f"hangman_letter_{letter}",
                    disabled=letter in game["guessed"],
                    on_click=_guess,
                    args=(letter,),
                    use_container_width=True,
                )


def render_hangman() -> None:
    if _ensure_state()["screen"] == "setup":
        render_setup()
    else:
        render_game()
