"""Streamlit web implementation of Connect Four."""

import streamlit as st

from games.connect_four import (
    COLUMNS,
    COMPUTER,
    CUSTOM_MINIMAX_DEPTH_MAX,
    CUSTOM_MINIMAX_DEPTH_MIN,
    DIFFICULTY_MAP,
    EMPTY,
    PLAYER,
    ROWS,
    board_full,
    check_winner,
    computer_move,
    create_board,
    simulate_move,
)


def _new_state() -> dict:
    return {
        "screen": "setup",
        "board": create_board(),
        "current_player": PLAYER,
        "outcome": None,
        "winner": None,
        "player_mode": "computer",
        "difficulty": "easy",
        "first_player": PLAYER,
        "minimax_depth": 4,
    }


def reset_connect_four() -> None:
    st.session_state["connect_four"] = _new_state()


def new_game() -> None:
    """Start a fresh board while keeping the current configuration."""
    game = _ensure_state()
    game["screen"] = "game"
    game["board"] = create_board()
    game["current_player"] = game["first_player"]
    game["outcome"] = None
    game["winner"] = None

    if game["player_mode"] == "computer" and game["current_player"] == COMPUTER:
        _computer_turn()


def _ensure_state() -> dict:
    if "connect_four" not in st.session_state:
        reset_connect_four()
    return st.session_state["connect_four"]


def _finish_if_needed(game: dict, player: str) -> bool:
    if check_winner(game["board"], player):
        game["outcome"] = "loss" if (
            game["player_mode"] == "computer" and player == COMPUTER
        ) else "win"
        game["winner"] = player
        return True

    if board_full(game["board"]):
        game["outcome"] = "draw"
        game["winner"] = None
        return True

    return False


def _computer_turn() -> None:
    game = _ensure_state()

    if game["outcome"] is not None:
        return

    if game["player_mode"] != "computer":
        return

    if game["current_player"] != COMPUTER:
        return

    difficulty = DIFFICULTY_MAP.get(
        game["difficulty"],
        game["difficulty"],
    )

    custom_depth = (
        game["minimax_depth"]
        if game["difficulty"] == "custom"
        else None
    )

    column = computer_move(
        game["board"],
        difficulty,
        custom_depth,
    )

    if column is None:
        game["outcome"] = "draw"
        return

    simulate_move(game["board"], column, COMPUTER)

    if _finish_if_needed(game, COMPUTER):
        return

    game["current_player"] = PLAYER


def _make_move(column: int) -> None:
    game = _ensure_state()

    if game["outcome"] is not None:
        return

    if game["current_player"] not in {PLAYER, "O"}:
        return

    if game["player_mode"] == "computer" and game["current_player"] != PLAYER:
        return

    valid_columns = [
        index for index in range(COLUMNS)
        if game["board"][0][index] == EMPTY
    ]

    if column not in valid_columns:
        return

    player = game["current_player"]
    simulate_move(game["board"], column, player)

    if _finish_if_needed(game, player):
        return

    if game["player_mode"] == "computer":
        game["current_player"] = COMPUTER
        _computer_turn()
    else:
        game["current_player"] = "O" if player == PLAYER else PLAYER


def _start_game(
    player_mode: str,
    difficulty: str,
    first_player: str,
    minimax_depth: int,
) -> None:
    game = _ensure_state()

    game["screen"] = "game"
    game["board"] = create_board()
    game["current_player"] = first_player
    game["outcome"] = None
    game["winner"] = None
    game["player_mode"] = player_mode
    game["difficulty"] = difficulty
    game["first_player"] = first_player
    game["minimax_depth"] = minimax_depth

    if player_mode == "computer" and first_player == COMPUTER:
        _computer_turn()


def render_setup() -> None:
    game = _ensure_state()

    st.title("Connect Four")
    st.caption("Configure your game before starting.")

    st.subheader("Game Mode")

    player_mode_label = st.radio(
        "Choose how you want to play",
        ["Play against Computer", "Two Players"],
        index=0 if game["player_mode"] == "computer" else 1,
        horizontal=True,
    )

    player_mode = (
        "computer"
        if player_mode_label == "Play against Computer"
        else "player"
    )

    if player_mode == "computer":
        st.subheader("Difficulty")

        difficulty_label = st.radio(
            "Computer difficulty",
            ["Easy", "Medium", "Hard", "Custom"],
            index=["easy", "medium", "hard", "custom"].index(
                game["difficulty"]
            ),
            horizontal=True,
        )

        difficulty = {
            "Easy": "easy",
            "Medium": "medium",
            "Hard": "hard",
            "Custom": "custom",
        }[difficulty_label]

        if difficulty == "custom":
            st.subheader("Custom Difficulty")
            minimax_depth = st.slider(
                "Minimax search depth",
                min_value=CUSTOM_MINIMAX_DEPTH_MIN,
                max_value=CUSTOM_MINIMAX_DEPTH_MAX,
                value=game["minimax_depth"],
            )
        else:
            minimax_depth = game["minimax_depth"]
    else:
        difficulty = "medium"
        minimax_depth = game["minimax_depth"]

    st.subheader("Who Goes First?")

    if player_mode == "computer":
        first_player_label = st.radio(
            "Choose the first player",
            ["You (X)", "Computer (O)"],
            index=0 if game["first_player"] == PLAYER else 1,
            horizontal=True,
        )
        first_player = (
            PLAYER
            if first_player_label == "You (X)"
            else COMPUTER
        )
    else:
        first_player_label = st.radio(
            "Choose the first player",
            ["Player X", "Player O"],
            index=0 if game["first_player"] == PLAYER else 1,
            horizontal=True,
        )
        first_player = (
            PLAYER
            if first_player_label == "Player X"
            else "O"
        )

    if st.button(
        "Start Game",
        type="primary",
        use_container_width=True,
    ):
        _start_game(
            player_mode=player_mode,
            difficulty=difficulty,
            first_player=first_player,
            minimax_depth=minimax_depth,
        )
        st.rerun()


def render_game() -> None:
    game = _ensure_state()

    st.title("Connect Four")

    if game["player_mode"] == "computer":
        difficulty_display = game["difficulty"].title()
        st.caption(
            f"Player X vs Computer O • "
            f"{difficulty_display} • "
            f"{'You' if game['first_player'] == PLAYER else 'Computer'} goes first"
        )
    else:
        st.caption(
            f"Two Players • "
            f"{'Player X' if game['first_player'] == PLAYER else 'Player O'} goes first"
        )

    if game["outcome"] == "win":
        if game["player_mode"] == "computer":
            if game["winner"] == PLAYER:
                st.success("You win!")
            else:
                st.error("Computer wins!")
        else:
            st.success(f"Player {game['winner']} wins!")

    elif game["outcome"] == "loss":
        st.error("Computer wins!")

    elif game["outcome"] == "draw":
        st.info("It's a draw!")

    else:
        if game["player_mode"] == "computer":
            if game["current_player"] == PLAYER:
                st.write("Your turn — choose a column.")
            else:
                st.write("Computer is thinking...")
        else:
            st.write(
                f"Current turn: **Player {game['current_player']}**"
            )

    # Column controls.
    column_cols = st.columns(COLUMNS)
    for column, column_col in enumerate(column_cols):
        with column_col:
            is_full = game["board"][0][column] != EMPTY
            is_disabled = (
                game["outcome"] is not None
                or is_full
                or (
                    game["player_mode"] == "computer"
                    and game["current_player"] != PLAYER
                )
            )

            st.button(
                str(column + 1),
                key=f"connect_four_column_{column}",
                use_container_width=True,
                disabled=is_disabled,
                on_click=_make_move,
                args=(column,),
            )

    # Board display. Buttons are display-only; moves are made through columns.
    st.markdown("---")

    for row in range(ROWS):
        row_cols = st.columns(COLUMNS)
        for column, cell_col in enumerate(row_cols):
            value = game["board"][row][column]
            display_value = "·" if value == EMPTY else value

            with cell_col:
                st.markdown(
                    f"<div style='text-align:center; font-size:28px; "
                    f"font-weight:700; padding:4px;'>{display_value}</div>",
                    unsafe_allow_html=True,
                )

    st.divider()

    if st.button(
        "Back to Setup",
        key="connect_four_back_to_setup",
        use_container_width=True,
    ):
        game["screen"] = "setup"
        st.rerun()


def render_connect_four() -> None:
    game = _ensure_state()

    if game["screen"] == "setup":
        render_setup()
    else:
        render_game()
