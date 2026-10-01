"""Streamlit entry point for Python Games Hub Web V2."""

import streamlit as st

from web.games.tic_tac_toe import reset_ttt, render_ttt


st.set_page_config(
    page_title="Python Games Hub",
    page_icon="🎮",
    layout="wide",
)


GAMES = [
    ("Tic-Tac-Toe", "Classic 3x3 strategy game", "Available"),
    ("Connect Four", "Connect four pieces before your opponent", "Coming next"),
    ("Hangman", "Guess the hidden word", "Coming next"),
    ("Rock Paper Scissors", "Classic RPS", "Coming next"),
    ("Word Scramble", "Unscramble the word", "Coming next"),
    ("Snake", "Classic Snake", "Coming next"),
    ("Minesweeper", "Clear the board without hitting a mine", "Coming next"),
]


def home() -> None:
    st.title("Python Games Hub")
    st.caption("A modular Python game platform — now moving to the web.")

    st.markdown("## Game Hub")
    cols = st.columns(3)

    for index, (name, description, status) in enumerate(GAMES):
        with cols[index % 3]:
            with st.container(border=True):
                st.subheader(name)
                st.write(description)

                if status == "Available":
                    if st.button(
                        "Play",
                        key=f"play_{index}",
                        use_container_width=True,
                    ):
                        st.session_state["page"] = name
                        st.rerun()
                else:
                    st.caption(status)


def tic_tac_toe_page() -> None:
    top_left, top_right = st.columns([1, 5])

    with top_left:
        if st.button("← Back to Games", use_container_width=True):
            st.session_state["page"] = "Home"
            st.rerun()

    with top_right:
        if st.button("New Game", use_container_width=True):
            reset_ttt()
            st.rerun()

    render_ttt()


def main() -> None:
    if "page" not in st.session_state:
        st.session_state["page"] = "Home"

    if st.session_state["page"] == "Tic-Tac-Toe":
        tic_tac_toe_page()
    else:
        home()


if __name__ == "__main__":
    main()
