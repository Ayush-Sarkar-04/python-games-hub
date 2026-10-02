"""Streamlit web implementation of Minesweeper."""

import random

import streamlit as st

from games.minesweeper import DIFFICULTIES, neighbors


def _new_state() -> dict:
    return {
        "screen": "setup",
        "difficulty": "easy",
        "rows": 9,
        "columns": 9,
        "mine_count": 10,
        "mines": set(),
        "counts": {},
        "revealed": set(),
        "flagged": set(),
        "first_move": True,
        "score": 0,
        "outcome": None,
        "message": "",
        "flag_mode": False,
    }


def _ensure_state() -> dict:
    if "minesweeper_web" not in st.session_state:
        st.session_state["minesweeper_web"] = _new_state()
    return st.session_state["minesweeper_web"]


def reset_minesweeper() -> None:
    st.session_state["minesweeper_web"] = _new_state()
    st.session_state["minesweeper_flag_mode"] = False
    st.session_state["minesweeper_flag_mode"] = False


def _generate_mines(game, safe_cell):
    cells = [
        (r, c) for r in range(game["rows"]) for c in range(game["columns"])
        if (r, c) != safe_cell
    ]
    game["mines"] = set(random.sample(cells, game["mine_count"]))
    game["counts"] = {
        (r, c): sum(
            neighbor in game["mines"]
            for neighbor in neighbors(r, c, game["rows"], game["columns"])
        )
        for r in range(game["rows"])
        for c in range(game["columns"])
    }


def _reveal(game, start):
    if start in game["flagged"] or start in game["revealed"]:
        return
    if start in game["mines"]:
        game["revealed"].add(start)
        game["outcome"] = "loss"
        game["message"] = "You hit a mine."
        return

    stack = [start]
    while stack:
        cell = stack.pop()
        if cell in game["revealed"] or cell in game["flagged"] or cell in game["mines"]:
            continue
        game["revealed"].add(cell)
        if game["counts"][cell] == 0:
            stack.extend(
                neighbor
                for neighbor in neighbors(cell[0], cell[1], game["rows"], game["columns"])
                if neighbor not in game["revealed"]
            )

    safe_total = game["rows"] * game["columns"] - game["mine_count"]
    if len(game["revealed"] - game["mines"]) >= safe_total:
        game["outcome"] = "win"
        game["message"] = "Board cleared."


def _reveal_cell(row: int, column: int) -> None:
    game = _ensure_state()
    if game["outcome"] is not None:
        return
    cell = (row, column)
    if cell in game["flagged"]:
        game["message"] = "Unflag the cell before revealing it."
        return
    if game["first_move"]:
        _generate_mines(game, cell)
        game["first_move"] = False
    _reveal(game, cell)
    game["score"] = len(game["revealed"] - game["mines"])


def _toggle_flag(row: int, column: int) -> None:
    game = _ensure_state()
    if game["outcome"] is not None:
        return
    cell = (row, column)
    if cell in game["revealed"]:
        return
    if cell in game["flagged"]:
        game["flagged"].remove(cell)
    else:
        game["flagged"].add(cell)


def _sync_setup_preferences() -> None:
    game = _ensure_state()
    game["difficulty"] = st.session_state["minesweeper_setup_difficulty"].lower()


def _sync_flag_mode() -> None:
    game = _ensure_state()
    game["flag_mode"] = st.session_state["minesweeper_flag_mode"]


def _start_game(difficulty: str) -> None:
    game = _ensure_state()
    settings = DIFFICULTIES[difficulty]
    game.update({
        "screen": "game",
        "difficulty": difficulty,
        "rows": settings["rows"],
        "columns": settings["columns"],
        "mine_count": settings["mines"],
        "mines": set(),
        "counts": {},
        "revealed": set(),
        "flagged": set(),
        "first_move": True,
        "score": 0,
        "outcome": None,
        "message": "",
        "flag_mode": False,
    })
    st.session_state["minesweeper_flag_mode"] = False


def new_game() -> None:
    _start_game(_ensure_state()["difficulty"])


def _cell_label(game, cell):
    if cell in game["flagged"]:
        return "🚩"
    if cell not in game["revealed"]:
        return "■"
    if cell in game["mines"]:
        return "💣"
    count = game["counts"][cell]
    return "·" if count == 0 else str(count)


def render_setup() -> None:
    game = _ensure_state()
    st.title("Minesweeper")
    st.caption("Reveal every safe cell without hitting a mine.")

    if "minesweeper_setup_difficulty" not in st.session_state:
        st.session_state["minesweeper_setup_difficulty"] = game["difficulty"].title()

    difficulty_label = st.radio(
        "Difficulty",
        ["Easy", "Medium", "Hard"],
        key="minesweeper_setup_difficulty",
        horizontal=True,
        on_change=_sync_setup_preferences,
    )
    difficulty = difficulty_label.lower()
    settings = DIFFICULTIES[difficulty]
    st.write(
        f"**{settings['name']}** · {settings['rows']} × {settings['columns']} "
        f"· {settings['mines']} mines"
    )
    if st.button("Start Game", type="primary", use_container_width=True):
        _start_game(difficulty)
        st.rerun()


def render_game() -> None:
    game = _ensure_state()

    st.markdown(
        """
        <style>
        .ms-stat{
            padding:9px 14px;
            border:1px solid #303642;
            border-radius:10px;
            background:#151922;
            display:flex;
            justify-content:space-between;
        }
        .ms-board{
            border:1px solid #303642;
            border-radius:14px;
            background:#0f131a;
            padding:8px;
        }
        [class*="st-key-ms_cell_"] button{
            min-height:34px !important;
            height:34px !important;
            padding:0 !important;
            font-size:0.8rem !important;
            border-radius:5px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Minesweeper")
    st.caption(
        f"{game['difficulty'].title()} · {game['rows']} × {game['columns']} · "
        f"{game['mine_count']} mines"
    )

    stats = st.columns(3)
    values = [
        ("Mines", game["mine_count"]),
        ("Flags", len(game["flagged"])),
        ("Score", game["score"]),
    ]
    for col, (label, value) in zip(stats, values):
        with col:
            st.markdown(
                f'<div class="ms-stat"><span>{label}</span><strong>{value}</strong></div>',
                unsafe_allow_html=True,
            )

    if game["message"] and game["outcome"] is None:
        st.info(game["message"])

    if game["outcome"] == "win":
        st.success(f"You cleared the board! Score: {game['score']}")
    elif game["outcome"] == "loss":
        st.error(f"Game over — {game['message']}")
    else:
        mode_label = "Flag mode" if game["flag_mode"] else "Reveal mode"
        st.caption(f"{mode_label} · Click a cell to {'flag or unflag' if game['flag_mode'] else 'reveal'} it.")

    if "minesweeper_flag_mode" not in st.session_state:
        st.session_state["minesweeper_flag_mode"] = game["flag_mode"]

    st.toggle(
        "Flag Mode",
        key="minesweeper_flag_mode",
        disabled=game["outcome"] is not None,
        on_change=_sync_flag_mode,
        help="Turn this on to place or remove flags. Turn it off to reveal cells.",
    )
    game["flag_mode"] = st.session_state["minesweeper_flag_mode"]

    cell_size = {"easy": 34, "medium": 28, "hard": 24}[game["difficulty"]]

    # Fixed-size buttons inside centered horizontal rows. This prevents
    # Streamlit's column layout from stretching the board across the page.
    for row in range(game["rows"]):
        with st.container(horizontal=True, horizontal_alignment="center", gap=0, wrap=False):
            for column in range(game["columns"]):
                cell = (row, column)
                if game["flag_mode"]:
                    st.button(
                        _cell_label(game, cell),
                        key=f"ms_cell_flag_{row}_{column}",
                        width=cell_size,
                        disabled=game["outcome"] is not None or cell in game["revealed"],
                        on_click=_toggle_flag,
                        args=(row, column),
                    )
                else:
                    st.button(
                        _cell_label(game, cell),
                        key=f"ms_cell_reveal_{row}_{column}",
                        width=cell_size,
                        disabled=game["outcome"] is not None or cell in game["revealed"] or cell in game["flagged"],
                        on_click=_reveal_cell,
                        args=(row, column),
                    )

    if game["outcome"] is not None:
        if st.button("Play Again", type="primary", width="stretch"):
            new_game()
            st.rerun()


def render_minesweeper() -> None:
    if _ensure_state()["screen"] == "setup":
        render_setup()
    else:
        render_game()
