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
    if match_type == "match":
        st.write("Number of rounds")
        round_options = list(range(2, 11))
        round_columns = st.columns(len(round_options))
        for option, column in zip(round_options, round_columns):
            with column:
                if st.button(
                    str(option),
                    key=f"rps_round_{option}",
                    type="primary" if game["rounds"] == option else "secondary",
                    use_container_width=True,
                ):
                    game["rounds"] = option
                    st.rerun()
        rounds = game["rounds"]
    else:
        rounds = 1
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

    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1400px;
            padding-top: 5rem;
            padding-bottom: 2.5rem;
        }
        .rps-header {
            padding: 4px 0 12px 0;
        }
        .rps-round {
            display: inline-block;
            padding: 7px 14px;
            border-radius: 999px;
            background: #1f2937;
            border: 1px solid #374151;
            font-size: 0.9rem;
            margin-bottom: 18px;
        }
        .rps-score {
            text-align: center;
            padding: 14px 12px;
            border-radius: 14px;
            background: #151922;
            border: 1px solid #303642;
            margin-bottom: 8px;
        }
        .rps-score-label {
            font-size: 0.82rem;
            color: #9ca3af;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        .rps-score-value {
            font-size: 1.75rem;
            font-weight: 800;
            margin-top: 4px;
        }
        .rps-vs {
            text-align: center;
            font-size: 1.15rem;
            font-weight: 800;
            color: #9ca3af;
            padding-top: 28px;
        }
        .rps-move-card {
            text-align: center;
            padding: 16px 12px;
            border-radius: 14px;
            background: #151922;
            border: 1px solid #303642;
            min-height: 118px;
        }
        .rps-move-icon {
            font-size: 2.6rem;
            line-height: 1.1;
        }
        .rps-move-name {
            margin-top: 7px;
            font-size: 0.95rem;
            font-weight: 700;
        }
        .rps-result {
            text-align: center;
            padding: 12px;
            border-radius: 12px;
            margin: 8px 0 18px 0;
            background: #151922;
            border: 1px solid #303642;
            font-size: 1.05rem;
            font-weight: 700;
        }
        div[data-testid="stButton"] button {
            min-height: 58px;
            border-radius: 12px;
            font-size: 0.95rem;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="rps-header">', unsafe_allow_html=True)
    st.title("Rock Paper Scissors")
    if game["match_type"] == "match":
        st.markdown(
            f'<div class="rps-round">ROUND {game["current_round"]} / {game["rounds"]}</div>',
            unsafe_allow_html=True,
        )
    else:
        st.caption(f"{game['variant'].title()} • {game['difficulty'].title()} difficulty")
    st.markdown("</div>", unsafe_allow_html=True)

    score_left, score_vs, score_right = st.columns([1, 0.5, 1])
    with score_left:
        st.markdown(
            f'<div class="rps-score"><div class="rps-score-label">You</div>'
            f'<div class="rps-score-value">{game["player_score"]}</div></div>',
            unsafe_allow_html=True,
        )
    with score_vs:
        st.markdown('<div class="rps-vs">VS</div>', unsafe_allow_html=True)
    with score_right:
        st.markdown(
            f'<div class="rps-score"><div class="rps-score-label">Computer</div>'
            f'<div class="rps-score-value">{game["computer_score"]}</div></div>',
            unsafe_allow_html=True,
        )

    if game["last_result"] is not None:
        icons = {
            "rock": "🪨",
            "paper": "📄",
            "scissors": "✂️",
            "lizard": "🦎",
            "spock": "🖖",
        }
        player_move = game["last_player"]
        computer_move = game["last_computer"]
        move_left, move_vs, move_right = st.columns([1, 0.5, 1])
        with move_left:
            st.markdown(
                f'<div class="rps-move-card"><div class="rps-move-icon">{icons[player_move]}</div>'
                f'<div class="rps-move-name">You<br>{player_move.title()}</div></div>',
                unsafe_allow_html=True,
            )
        with move_vs:
            st.markdown('<div class="rps-vs">VS</div>', unsafe_allow_html=True)
        with move_right:
            st.markdown(
                f'<div class="rps-move-card"><div class="rps-move-icon">{icons[computer_move]}</div>'
                f'<div class="rps-move-name">Computer<br>{computer_move.title()}</div></div>',
                unsafe_allow_html=True,
            )

        result_text = {
            "player": "YOU WIN THIS ROUND",
            "computer": "COMPUTER WINS THIS ROUND",
            "draw": "ROUND DRAW",
        }[game["last_result"]]
        st.markdown(
            f'<div class="rps-result">{result_text}</div>',
            unsafe_allow_html=True,
        )

    if game["outcome"] is not None:
        outcome_text = {
            "win": "YOU WIN THE MATCH",
            "loss": "COMPUTER WINS THE MATCH",
            "draw": "MATCH DRAW",
        }[game["outcome"]]
        st.markdown(
            f'<div class="rps-result">{outcome_text}<br>'
            f'<span style="font-weight:500;">Final score: You {game["player_score"]} — '
            f'Computer {game["computer_score"]}</span></div>',
            unsafe_allow_html=True,
        )
        return

    moves = EXTENDED_MOVES if game["variant"] == "extended" else STANDARD_MOVES
    icons = {
        "rock": "🪨",
        "paper": "📄",
        "scissors": "✂️",
        "lizard": "🦎",
        "spock": "🖖",
    }

    st.subheader("Choose your move")
    columns = st.columns(len(moves))
    for index, move in enumerate(moves):
        with columns[index]:
            if st.button(
                f"{icons[move]}  {move.title()}",
                key=f"rps_move_{move}",
                use_container_width=True,
            ):
                _play_round(move)
                st.rerun()

def render_rps() -> None:
    game = _ensure_state()
    if game["screen"] == "setup": render_setup()
    else: render_game()