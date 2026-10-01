"""Streamlit presentation and session-state adapter for Tic-Tac-Toe."""

import streamlit as st

from games.tic_tac_toe import WINNING_COMBINATIONS, check_winner, get_winner


EMPTY = " "


def _new_state() -> dict:
    return {
        "board": [EMPTY] * 9,
        "current_player": "X",
        "outcome": None,
        "winner": None,
    }


def reset_ttt() -> None:
    st.session_state["ttt"] = _new_state()


def _ensure_state() -> dict:
    if "ttt" not in st.session_state:
        reset_ttt()
    return st.session_state["ttt"]


def _winner_line(board):
    for combo in WINNING_COMBINATIONS:
        a, b, c = combo
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return combo
    return None


def _make_move(position: int) -> None:
    game = _ensure_state()
    if game["outcome"] is not None or game["board"][position] != EMPTY:
        return

    player = game["current_player"]
    game["board"][position] = player

    if check_winner(game["board"]):
        game["outcome"] = "win"
        game["winner"] = get_winner(game["board"])
    elif EMPTY not in game["board"]:
        game["outcome"] = "draw"
    else:
        game["current_player"] = "O" if player == "X" else "X"


def render_ttt() -> None:
    game = _ensure_state()
    st.title("Tic-Tac-Toe")
    st.caption("Web V2 vertical slice — browser interaction over the existing game rules.")

    left, right = st.columns([2, 1])
    with left:
        winning_line = _winner_line(game["board"])
        for row in range(3):
            cols = st.columns(3)
            for col, button_col in enumerate(cols):
                position = row * 3 + col
                label = game["board"][position]
                if winning_line and position in winning_line:
                    label = f"★ {label}"
                with button_col:
                    st.button(
                        label if label != EMPTY else "·",
                        key=f"ttt_{position}",
                        use_container_width=True,
                        disabled=(game["outcome"] is not None or game["board"][position] != EMPTY),
                        on_click=_make_move,
                        args=(position,),
                    )

    with right:
        st.subheader("Game Status")
        if game["outcome"] == "win":
            st.success(f"Player {game['winner']} wins!")
        elif game["outcome"] == "draw":
            st.info("It's a draw!")
        else:
            st.write(f"Current turn: **Player {game['current_player']}**")

        st.caption("The browser UI is intentionally thin; game rules remain separate from presentation.")
