"""Streamlit entry point for Python Games Hub Web V2."""

import streamlit as st

from web.games.tic_tac_toe import reset_ttt, render_ttt


st.set_page_config(
    page_title="Python Games Hub",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
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
                    if st.button("Play", key=f"play_{index}", use_container_width=True):
                        st.session_state["page"] = name
                        st.rerun()
                else:
                    st.caption(status)


def main() -> None:
    if "page" not in st.session_state:
        st.session_state["page"] = "Home"

    with st.sidebar:
        st.title("Games Hub")
        page = st.radio(
            "Navigate",
            ["Home", "Tic-Tac-Toe"],
            index=["Home", "Tic-Tac-Toe"].index(st.session_state["page"]),
        )
        st.session_state["page"] = page

        if page == "Tic-Tac-Toe" and st.button("New Game", use_container_width=True):
            reset_ttt()
            st.rerun()

    if st.session_state["page"] == "Tic-Tac-Toe":
        render_ttt()
    else:
        home()


if __name__ == "__main__":
    main()
