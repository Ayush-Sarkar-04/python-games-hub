"""Streamlit web implementation of Snake."""

import random
import time

import streamlit as st

from games.snake import COLUMNS, DIRECTIONS, OPPOSITE, ROWS, DIFFICULTIES, FOOD_SCORE

snake_keyboard = st.components.v2.component(
    name="snake_keyboard_controls",
    html='<div class="snake-keyboard">Keyboard controls active · Use ↑ ↓ ← →</div>',
    css="""
        .snake-keyboard {
            width: 100%;
            box-sizing: border-box;
            padding: 10px 12px;
            border: 1px solid #303642;
            border-radius: 10px;
            background: #151922;
            color: #d3d4c0;
            text-align: center;
            font-size: 0.85rem;
        }
    """,
    js="""
        export default function({ setTriggerValue }) {
            const directions = {
                ArrowUp: "UP",
                ArrowDown: "DOWN",
                ArrowLeft: "LEFT",
                ArrowRight: "RIGHT",
            };

            const handler = (event) => {
                const direction = directions[event.key];
                if (!direction) return;

                const target = event.target;
                if (
                    target instanceof HTMLInputElement ||
                    target instanceof HTMLTextAreaElement ||
                    target instanceof HTMLSelectElement ||
                    target?.isContentEditable
                ) {
                    return;
                }

                event.preventDefault();
                if (event.repeat) return;
                setTriggerValue("move", direction);
            };

            if (window.__snakeKeyboardHandler) {
                window.removeEventListener("keydown", window.__snakeKeyboardHandler);
            }

            window.__snakeKeyboardHandler = handler;
            window.addEventListener("keydown", handler);

            return () => {
                window.removeEventListener("keydown", handler);
                if (window.__snakeKeyboardHandler === handler) {
                    delete window.__snakeKeyboardHandler;
                }
            };
        }
    """,
)


def _new_state() -> dict:
    snake = [(ROWS // 2, COLUMNS // 2), (ROWS // 2, COLUMNS // 2 - 1), (ROWS // 2, COLUMNS // 2 - 2)]
    return {
        "screen": "setup",
        "difficulty": "easy",
        "snake": snake,
        "food": None,
        "direction": "RIGHT",
        "score": 0,
        "outcome": None,
        "wrap": False,
        "paused": False,
        "message": "",
        "last_tick": time.monotonic(),
    }


def _ensure_state() -> dict:
    if "snake_web" not in st.session_state:
        st.session_state["snake_web"] = _new_state()
    return st.session_state["snake_web"]


def reset_snake() -> None:
    st.session_state["snake_web"] = _new_state()


def _food(snake):
    cells = [
        (r, c) for r in range(ROWS) for c in range(COLUMNS)
        if (r, c) not in snake
    ]
    return random.choice(cells) if cells else None


def _start_game(difficulty: str, wrap: bool) -> None:
    game = _ensure_state()
    snake = [(ROWS // 2, COLUMNS // 2), (ROWS // 2, COLUMNS // 2 - 1), (ROWS // 2, COLUMNS // 2 - 2)]
    game.update({
        "screen": "game",
        "difficulty": difficulty,
        "snake": snake,
        "food": _food(snake),
        "direction": "RIGHT",
        "score": 0,
        "outcome": None,
        "wrap": wrap,
        "paused": False,
        "message": "",
        "last_tick": time.monotonic(),
    })


def new_game() -> None:
    game = _ensure_state()
    _start_game(game["difficulty"], game["wrap"])


def _set_direction(direction: str) -> None:
    game = _ensure_state()
    if game["outcome"] is not None or game["paused"]:
        return
    if direction in DIRECTIONS and direction != OPPOSITE[game["direction"]]:
        game["direction"] = direction


def _move(direction=None) -> None:
    game = _ensure_state()
    if game["outcome"] is not None or game["paused"]:
        return
    if direction:
        _set_direction(direction)

    row, col = game["snake"][0]
    dr, dc = DIRECTIONS[game["direction"]]
    head = (row + dr, col + dc)

    if game["wrap"]:
        head = (head[0] % ROWS, head[1] % COLUMNS)
    elif not (0 <= head[0] < ROWS and 0 <= head[1] < COLUMNS):
        game["outcome"] = "loss"
        game["message"] = "You hit the wall."
        return

    if head in game["snake"]:
        game["outcome"] = "loss"
        game["message"] = "You hit yourself."
        return

    game["snake"].insert(0, head)
    if head == game["food"]:
        game["score"] += FOOD_SCORE
        game["food"] = _food(game["snake"])
        if game["food"] is None:
            game["outcome"] = "win"
    else:
        game["snake"].pop()


def _tick() -> None:
    _move()


def render_setup() -> None:
    game = _ensure_state()
    st.title("Snake")
    st.caption("Guide the snake, eat food, and avoid the walls and yourself.")

    difficulty_label = st.radio(
        "Difficulty",
        ["Easy", "Medium", "Hard"],
        index=["easy", "medium", "hard"].index(game["difficulty"]),
        horizontal=True,
    )
    difficulty = difficulty_label.lower()
    wrap = st.toggle("Wrap around walls", value=game["wrap"])

    if st.button("Start Game", type="primary", use_container_width=True):
        _start_game(difficulty, wrap)
        st.rerun()


def _board_html(game: dict) -> str:
    snake = set(game["snake"])
    head = game["snake"][0]
    rows = []
    for r in range(ROWS):
        cells = []
        for c in range(COLUMNS):
            cell = (r, c)
            if cell == head:
                value = "●"
                cls = "snake-head"
            elif cell in snake:
                value = "●"
                cls = "snake-body"
            elif cell == game["food"]:
                value = "◆"
                cls = "food"
            else:
                value = ""
                cls = "empty"
            cells.append(f'<div class="snake-cell {cls}">{value}</div>')
        rows.append("".join(cells))
    return '<div class="snake-board">' + "".join(rows) + "</div>"


@st.fragment(run_every=0.04)
def _render_live_board() -> None:
    game = _ensure_state()
    if game["screen"] != "game":
        return

    if game["outcome"] is None and not game["paused"]:
        now = time.monotonic()
        interval = DIFFICULTIES[game["difficulty"]][1]
        last_tick = game.get("last_tick", now)

        if now - last_tick >= interval:
            _move()
            game["last_tick"] = now

    st.markdown(_board_html(game), unsafe_allow_html=True)


@st.fragment(run_every=0.04)
def _render_sidebar() -> None:
    game = _ensure_state()

    stats = st.columns(2)
    with stats[0]:
        st.markdown(
            f'<div class="snake-stat"><span>Score</span><strong>{game["score"]}</strong></div>',
            unsafe_allow_html=True,
        )
    with stats[1]:
        st.markdown(
            f'<div class="snake-stat"><span>Length</span><strong>{len(game["snake"])}</strong></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="snake-status-spacer"></div>', unsafe_allow_html=True)

    if game["outcome"] is not None:
        if game["outcome"] == "win":
            st.success(f"You cleared the board! Score: {game['score']}")
        else:
            st.error(f"Game over — {game['message']} Score: {game['score']}")
    else:
        st.markdown('<div class="snake-status-placeholder"></div>', unsafe_allow_html=True)

    st.subheader("Controls")

    keyboard = snake_keyboard(
        key="snake_keyboard",
        on_move_change=lambda: None,
    )
    if keyboard.move:
        _set_direction(keyboard.move)

    st.caption("Keyboard")
    st.write("Use the arrow keys to steer the snake.")

    up = st.columns([1, 1, 1])
    with up[1]:
        st.button(
            "↑",
            key="snake_up",
            use_container_width=True,
            on_click=_set_direction,
            args=("UP",),
        )

    middle = st.columns([1, 1, 1])
    with middle[0]:
        st.button(
            "←",
            key="snake_left",
            use_container_width=True,
            on_click=_set_direction,
            args=("LEFT",),
        )
    with middle[1]:
        st.markdown(
            '<div style="height:38px;display:flex;align-items:center;'
            'justify-content:center;border:1px solid #303642;border-radius:10px;'
            'background:#151922;color:#778873;font-size:14px;">●</div>',
            unsafe_allow_html=True,
        )
    with middle[2]:
        st.button(
            "→",
            key="snake_right",
            use_container_width=True,
            on_click=_set_direction,
            args=("RIGHT",),
        )

    down = st.columns([1, 1, 1])
    with down[1]:
        st.button(
            "↓",
            key="snake_down",
            use_container_width=True,
            on_click=_set_direction,
            args=("DOWN",),
        )

    if st.button(
        "Pause" if not game["paused"] else "Resume",
        key="snake_pause",
        use_container_width=True,
    ):
        game["paused"] = not game["paused"]
        game["last_tick"] = time.monotonic()
        st.rerun()

    st.markdown(
        '<div class="snake-bottom-caption">'
        'The snake moves continuously. Use the arrow keys to change direction.'
        '</div>',
        unsafe_allow_html=True,
    )


def render_game() -> None:
    game = _ensure_state()

    st.markdown(
        """
        <style>
        .snake-board{
            display:grid;
            grid-template-columns:repeat(30,minmax(0,1fr));
            gap:2px;
            width:min(100%, calc((100vh - 330px) * 1.5));
            max-height:calc(100vh - 330px);
            margin:0 auto;
            box-sizing:border-box;
            background:#0f131a;
            padding:8px;
            border-radius:14px;
            border:1px solid #303642;
        }
        .snake-cell{
            aspect-ratio:1/1;
            display:flex;
            align-items:center;
            justify-content:center;
            border-radius:3px;
            font-size:12px;
            background:#171c25;
            color:transparent;
        }
        .snake-head{
            background:#f3e4c9;
            color:#0a2947;
            font-weight:900;
        }
        .snake-body{
            background:#778873;
            color:#f3e4c9;
        }
        .food{
            background:#8b5e3c;
            color:#f3e4c9;
            font-size:10px;
        }
        .snake-stat{
            padding:9px 14px;
            border:1px solid #303642;
            border-radius:10px;
            background:#151922;
            display:flex;
            justify-content:space-between;
        }
        .snake-status-spacer{
            height:14px;
        }
        .snake-status-placeholder{
            height:0;
        }
        .snake-bottom-caption{
            margin-top:14px;
            color:#8b8f98;
            font-size:0.82rem;
            line-height:1.3;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Snake")
    st.markdown(
        f"**{game['difficulty'].title()}** · "
        f"{'Wrap enabled' if game['wrap'] else 'Walls enabled'}"
    )

    board_col, controls_col = st.columns([2, 1], gap="large")

    with board_col:
        _render_live_board()

    with controls_col:
        _render_sidebar()


def render_snake() -> None:
    if _ensure_state()["screen"] == "setup":
        render_setup()
    else:
        render_game()
