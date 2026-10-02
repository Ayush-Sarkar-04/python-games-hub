import streamlit as st

from games.tic_tac_toe import (
    CUSTOM_MINIMAX_DEPTH_MAX,
    CUSTOM_MINIMAX_DEPTH_MIN,
    DIFFICULTY_MAP,
    WINNING_COMBINATIONS,
    check_winner,
    computer_move,
    get_winner,
)


EMPTY = " "

DIFFICULTIES = {
    "Easy": "easy",
    "Medium": "medium",
    "Hard": "hard",
    "Custom": "custom",
}

PERSONALITIES = {
    "Balanced": "Balanced",
    "Aggressive": "Aggressive",
    "Defensive": "Defensive",
}


def _new_state() -> dict:
    return {
        "screen": "setup",
        "board": [EMPTY] * 9,
        "current_player": "X",
        "outcome": None,
        "winner": None,
        "player_mode": "computer",
        "difficulty": "easy",
        "personality": "Balanced",
        "minimax_depth": 5,
    }


def reset_ttt() -> None:
    st.session_state["ttt"] = _new_state()


def new_game() -> None:
    """Start a fresh board while keeping the current game configuration."""
    game = _ensure_state()
    game["screen"] = "game"
    game["board"] = [EMPTY] * 9
    game["current_player"] = "X"
    game["outcome"] = None
    game["winner"] = None


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


def _start_game(
    player_mode: str,
    difficulty_label: str,
    personality: str,
    minimax_depth: int,
) -> None:
    game = _ensure_state()

    game["screen"] = "game"
    game["board"] = [EMPTY] * 9
    game["current_player"] = "X"
    game["outcome"] = None
    game["winner"] = None

    game["player_mode"] = player_mode
    game["difficulty"] = DIFFICULTIES[difficulty_label]
    game["personality"] = personality
    game["minimax_depth"] = minimax_depth


def _make_move(position: int) -> None:
    game = _ensure_state()

    if game["outcome"] is not None:
        return

    if game["board"][position] != EMPTY:
        return

    # In computer mode, the human controls X.
    if game["player_mode"] == "computer" and game["current_player"] != "X":
        return

    player = game["current_player"]
    game["board"][position] = player

    if check_winner(game["board"]):
        game["outcome"] = "win"
        game["winner"] = get_winner(game["board"])
        return

    if EMPTY not in game["board"]:
        game["outcome"] = "draw"
        return

    game["current_player"] = "O" if player == "X" else "X"

    # Computer takes its turn immediately.
    if game["player_mode"] == "computer" and game["current_player"] == "O":
        _computer_turn()


def _computer_turn() -> None:
    game = _ensure_state()

    if game["outcome"] is not None:
        return

    if game["player_mode"] != "computer":
        return

    if game["current_player"] != "O":
        return

    difficulty = game["difficulty"]

    if difficulty == "custom":
        move = computer_move(
            game["board"],
            DIFFICULTY_MAP["hard"],
            personality=game["personality"],
            custom_depth=game["minimax_depth"],
        )
    else:
        move = computer_move(
            game["board"],
            DIFFICULTY_MAP[difficulty],
            personality=game["personality"],
        )

    if move is None:
        return

    game["board"][move] = "O"

    if check_winner(game["board"]):
        game["outcome"] = "win"
        game["winner"] = get_winner(game["board"])
        return

    if EMPTY not in game["board"]:
        game["outcome"] = "draw"
        return

    game["current_player"] = "X"


def _sync_setup_preferences() -> None:
    game = _ensure_state()
    game["player_mode"] = "computer" if st.session_state["ttt_setup_player_mode"] == "Play against Computer" else "player"
    game["difficulty"] = DIFFICULTIES[st.session_state["ttt_setup_difficulty"]]
    game["personality"] = st.session_state["ttt_setup_personality"]
    game["minimax_depth"] = st.session_state["ttt_setup_minimax_depth"]


def render_setup() -> None:
    game = _ensure_state()

    st.title("Tic-Tac-Toe")
    st.caption("Configure your game before starting.")

    st.subheader("Game Mode")

    if "ttt_setup_player_mode" not in st.session_state:
        st.session_state["ttt_setup_player_mode"] = (
            "Play against Computer" if game["player_mode"] == "computer" else "Two Players"
        )
    if "ttt_setup_difficulty" not in st.session_state:
        st.session_state["ttt_setup_difficulty"] = next(
            label for label, value in DIFFICULTIES.items() if value == game["difficulty"]
        )
    if "ttt_setup_personality" not in st.session_state:
        st.session_state["ttt_setup_personality"] = game["personality"]
    if "ttt_setup_minimax_depth" not in st.session_state:
        st.session_state["ttt_setup_minimax_depth"] = game["minimax_depth"]

    player_mode_label = st.radio(
        "Choose how you want to play",
        ["Play against Computer", "Two Players"],
        key="ttt_setup_player_mode",
        horizontal=True,
        on_change=_sync_setup_preferences,
    )

    player_mode = (
        "computer"
        if player_mode_label == "Play against Computer"
        else "player"
    )

    st.subheader("Difficulty")

    difficulty_label = st.radio(
        "Computer difficulty",
        list(DIFFICULTIES.keys()),
        key="ttt_setup_difficulty",
        horizontal=True,
        disabled=player_mode != "computer",
        on_change=_sync_setup_preferences,
    )

    personality = game["personality"]

    if player_mode == "computer":
        st.subheader("Computer Personality")

        personality_label = st.selectbox(
            "Choose computer personality",
            list(PERSONALITIES.keys()),
            key="ttt_setup_personality",
            on_change=_sync_setup_preferences,
        )

        personality = PERSONALITIES[personality_label]

        if difficulty_label == "Custom":
            st.subheader("Custom Difficulty")

            minimax_depth = st.slider(
                "Minimax search depth",
                min_value=CUSTOM_MINIMAX_DEPTH_MIN,
                max_value=CUSTOM_MINIMAX_DEPTH_MAX,
                key="ttt_setup_minimax_depth",
                on_change=_sync_setup_preferences,
            )
        else:
            minimax_depth = game["minimax_depth"]

    else:
        minimax_depth = game["minimax_depth"]
        st.info("Player X goes first.")

    if st.button(
        "Start Game",
        type="primary",
        use_container_width=True,
    ):
        _start_game(
            player_mode=player_mode,
            difficulty_label=difficulty_label,
            personality=personality,
            minimax_depth=minimax_depth,
        )
        st.rerun()


def render_game() -> None:
    game = _ensure_state()

    st.title("Tic-Tac-Toe")

    if game["player_mode"] == "computer":
        difficulty_display = (
            "Custom"
            if game["difficulty"] == "custom"
            else game["difficulty"].title()
        )

        st.caption(
            f"Player X vs Computer O • "
            f"{difficulty_display} • "
            f"{game['personality']}"
        )
    else:
        st.caption("Two Players • X goes first")

    if game["outcome"] == "win":
        if game["player_mode"] == "computer":
            if game["winner"] == "X":
                st.success("You win!")
            else:
                st.error("Computer wins!")
        else:
            st.success(f"Player {game['winner']} wins!")

    elif game["outcome"] == "draw":
        st.info("It's a draw!")

    else:
        if game["player_mode"] == "computer":
            if game["current_player"] == "X":
                st.write("Your turn — choose a square.")
            else:
                st.write("Computer is thinking...")
        else:
            st.write(
                f"Current turn: **Player {game['current_player']}**"
            )

    winning_line = _winner_line(game["board"])

    for row in range(3):
        cols = st.columns(3)

        for col, button_col in enumerate(cols):
            position = row * 3 + col
            label = game["board"][position]

            if winning_line and position in winning_line:
                label = f"★ {label}"

            is_disabled = (
                game["outcome"] is not None
                or game["board"][position] != EMPTY
                or (
                    game["player_mode"] == "computer"
                    and game["current_player"] != "X"
                )
            )

            with button_col:
                st.button(
                    label if label != EMPTY else "·",
                    key=f"ttt_{position}",
                    use_container_width=True,
                    disabled=is_disabled,
                    on_click=_make_move,
                    args=(position,),
                )

    st.divider()

    if st.button(
        "Back to Setup",
        key="ttt_back_to_setup",
        use_container_width=True,
    ):
        game["screen"] = "setup"
        st.rerun()


def render_ttt() -> None:
    game = _ensure_state()

    if game["screen"] == "setup":
        render_setup()
    else:
        render_game()