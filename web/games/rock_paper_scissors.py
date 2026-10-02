"""Streamlit web implementation of Rock Paper Scissors."""

import streamlit as st

from games.rock_paper_scissors import (
    DIFFICULTY_PERSONALITY,
    EXTENDED_MOVES,
    STANDARD_MOVES,
    choose_computer_move,
    get_round_winner,
)


def _new_state() -> dict:
    return {
        "screen": "setup", "variant": "standard", "match_type": "single",
        "rounds": 1, "difficulty": "easy", "personality": "balanced",
        "current_round": 1, "history": [], "player_score": 0,
        "computer_score": 0, "last_player": None, "last_computer": None,
        "last_result": None, "outcome": None,
    }


def reset_rps() -> None:
    st.session_state["rps"] = _new_state()


def _ensure_state() -> dict:
    if "rps" not in st.session_state:
        reset_rps()
    return st.session_state["rps"]


def new_game() -> None:
    game = _ensure_state()
    game.update({
        "screen": "game", "current_round": 1, "history": [],
        "player_score": 0, "computer_score": 0, "last_player": None,
        "last_computer": None, "last_result": None, "outcome": None,
    })


def _play_round(player: str) -> None:
    game = _ensure_state()
    moves = EXTENDED_MOVES if game["variant"] == "extended" else STANDARD_MOVES
    computer = choose_computer_move(game["history"], moves, game["personality"])
    game["history"].append(player)
    result = get_round_winner(player, computer)
    game["last_player"] = player
    game["last_computer"] = computer
    game["last_result"] = result
    if result == "player":
        game["player_score"] += 1
    elif result == "computer":
        game["computer_score"] += 1
    if game["current_round"] >= game["rounds"]:
        if game["player_score"] > game["computer_score"]:
            game["outcome"] = "win"
        elif game["computer_score"] > game["player_score"]:
            game["outcome"] = "loss"
        else:
            game["outcome"] = "draw"
    else:
        game["current_round"] += 1


def render_setup() -> None:
    game = _ensure_state()
    st.title("Rock Paper Scissors")
    st.caption("Choose your variant and match format.")
    variant_label = st.radio("Variant", ["Standard", "Lizard & Spock"],
                             index=0 if game["variant"] == "standard" else 1,
                             horizontal=True)
    variant = "standard" if variant_label == "Standard" else "extended"
    match_label = st.radio("Match Type", ["Single Game", "Fixed-Length Match"],
                           index=0 if game["match_type"] == "single" else 1,
                           horizontal=True)
    match_type = "single" if match_label == "Single Game" else "match"
    rounds = st.slider("Number of rounds", 2, 10, max(2, min(10, game["rounds"]))) if match_type == "match" else 1
    difficulty_label = st.radio("Difficulty", ["Easy", "Medium", "Hard"],
                                index=["easy", "medium", "hard"].index(game["difficulty"]),
                                horizontal=True)
    difficulty = difficulty_label.lower()
    if st.button("Start Game", type="primary", use_container_width=True):
        game.update({"variant": variant, "match_type": match_type, "rounds": rounds,
                     "difficulty": difficulty,
                     "personality": DIFFICULTY_PERSONALITY[difficulty]})
        new_game()
        st.rerun()


def render_game() -> None:
    game = _ensure_state()
    st.title("Rock Paper Scissors")
    if game["match_type"] == "match":
        st.caption(f"Round {game['current_round']}/{game['rounds']} • Score: You {game['player_score']} | Computer {game['computer_score']}")
    else:
        st.caption(f"{game['variant'].title()} • {game['difficulty'].title()} difficulty")
    if game["last_result"] is not None:
        st.divider()
        st.write(f"**You:** {game['last_player'].title()}  **Computer:** {game['last_computer'].title()}")
        if game["last_result"] == "player": st.success("You win this round!")
        elif game["last_result"] == "computer": st.error("Computer wins this round!")
        else: st.info("This round is a draw.")
    if game["outcome"] is not None:
        st.divider()
        if game["outcome"] == "win": st.success("You win the match!")
        elif game["outcome"] == "loss": st.error("Computer wins the match!")
        else: st.info("The match is a draw.")
        st.write(f"Final score: **You {game['player_score']}** — **Computer {game['computer_score']}**")
        return
    moves = EXTENDED_MOVES if game["variant"] == "extended" else STANDARD_MOVES
    st.subheader("Choose your move")
    columns = st.columns(len(moves))
    for index, move in enumerate(moves):
        with columns[index]:
            if st.button(move.title(), key=f"rps_move_{move}", use_container_width=True):
                _play_round(move)
                st.rerun()


def render_rps() -> None:
    game = _ensure_state()
    if game["screen"] == "setup": render_setup()
    else: render_game()