"""Streamlit entry point for Python Games Hub Web V2."""

import sys
from pathlib import Path

import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from web.games.connect_four import new_game as new_connect_four_game
from web.games.connect_four import render_connect_four
from web.games.rock_paper_scissors import new_game as new_rps_game
from web.games.rock_paper_scissors import render_rps
from web.games.tic_tac_toe import new_game, render_ttt
from web.games.word_scramble import new_game as new_word_scramble_game
from web.games.word_scramble import render_word_scramble

st.set_page_config(page_title="Python Games Hub", page_icon="🎮", layout="wide")

GAMES = [
    ("Tic-Tac-Toe", "Classic 3x3 strategy game", "Available"),
    ("Connect Four", "Connect four pieces before your opponent", "Available"),
    ("Hangman", "Guess the hidden word", "Coming next"),
    ("Rock Paper Scissors", "Classic RPS", "Available"),
    ("Word Scramble", "Unscramble the word", "Available"),
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


def tic_tac_toe_page() -> None:
    game = st.session_state.get("ttt", {})
    screen = game.get("screen", "setup")
    if screen == "game":
        top_left, top_right = st.columns([1, 5])
        with top_left:
            if st.button("← Back to Games", use_container_width=True):
                st.session_state["page"] = "Home"
                st.rerun()
        with top_right:
            if st.button("New Game", key="ttt_page_new_game", use_container_width=True):
                new_game()
                st.rerun()
    else:
        if st.button("← Back to Games", use_container_width=True):
            st.session_state["page"] = "Home"
            st.rerun()
    render_ttt()


def connect_four_page() -> None:
    game = st.session_state.get("connect_four", {})
    screen = game.get("screen", "setup")
    if screen == "game":
        top_left, top_right = st.columns([1, 5])
        with top_left:
            if st.button("← Back to Games", key="connect_four_back_to_games", use_container_width=True):
                st.session_state["page"] = "Home"
                st.rerun()
        with top_right:
            if st.button("New Game", key="connect_four_page_new_game", use_container_width=True):
                new_connect_four_game()
                st.rerun()
    else:
        if st.button("← Back to Games", key="connect_four_setup_back_to_games", use_container_width=True):
            st.session_state["page"] = "Home"
            st.rerun()
    render_connect_four()


def rps_page() -> None:
    game = st.session_state.get("rps", {})
    screen = game.get("screen", "setup")
    if screen == "game":
        top_left, top_right = st.columns([1, 5])
        with top_left:
            if st.button("← Back to Games", key="rps_back_to_games", use_container_width=True):
                st.session_state["page"] = "Home"
                st.rerun()
        with top_right:
            if st.button("New Game", key="rps_page_new_game", use_container_width=True):
                new_rps_game()
                st.rerun()
    else:
        if st.button("← Back to Games", key="rps_setup_back_to_games", use_container_width=True):
            st.session_state["page"] = "Home"
            st.rerun()
    render_rps()


def word_scramble_page() -> None:
    game = st.session_state.get("word_scramble", {})
    screen = game.get("screen", "setup")
    if screen == "game":
        top_left, top_right = st.columns([1, 5])
        with top_left:
            if st.button("← Back to Games", key="word_scramble_back_to_games", use_container_width=True):
                st.session_state["page"] = "Home"
                st.rerun()
        with top_right:
            if st.button("New Game", key="word_scramble_page_new_game", use_container_width=True):
                new_word_scramble_game()
                st.rerun()
    else:
        if st.button("← Back to Games", key="word_scramble_setup_back_to_games", use_container_width=True):
            st.session_state["page"] = "Home"
            st.rerun()
    render_word_scramble()


def main() -> None:
    if "page" not in st.session_state:
        st.session_state["page"] = "Home"
    if st.session_state["page"] == "Tic-Tac-Toe":
        tic_tac_toe_page()
    elif st.session_state["page"] == "Connect Four":
        connect_four_page()
    elif st.session_state["page"] == "Rock Paper Scissors":
        rps_page()
    elif st.session_state["page"] == "Word Scramble":
        word_scramble_page()
    else:
        home()


if __name__ == "__main__":
    main()