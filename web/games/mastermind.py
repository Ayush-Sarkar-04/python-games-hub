"""Streamlit UI for Mastermind."""

import streamlit as st

from engine.game import SessionConfig

from games.mastermind import DIFFICULTIES, MastermindGame, evaluate_guess, validate_guess


COLOR_MAP = {
    "R": "#ef4444",
    "G": "#22c55e",
    "B": "#3b82f6",
    "Y": "#facc15",
    "O": "#f97316",
    "P": "#a855f7",
}


def _ensure_state() -> dict:
    if "mastermind" not in st.session_state:
        st.session_state["mastermind"] = {"screen": "setup", "difficulty": "medium"}
    return st.session_state["mastermind"]


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .mm-shell {
            max-width: 1050px;
            margin: 0 auto;
        }
        .mm-hero {
            padding: 8px 0 18px 0;
        }
        .mm-kicker {
            color: #94a3b8;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .mm-title {
            font-size: 2.55rem;
            font-weight: 800;
            line-height: 1.05;
            margin: 0;
        }
        .mm-subtitle {
            color: #94a3b8;
            margin-top: 8px;
            font-size: 1rem;
        }
        .mm-stat {
            background: linear-gradient(145deg, #171b25, #10131a);
            border: 1px solid #2b3140;
            border-radius: 14px;
            padding: 14px 16px;
            min-height: 82px;
        }
        .mm-stat-label {
            color: #8d96a8;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .mm-stat-value {
            font-size: 1.35rem;
            font-weight: 800;
            margin-top: 4px;
        }
        .mm-panel {
            background: linear-gradient(145deg, #151922, #10131a);
            border: 1px solid #2b3140;
            border-radius: 18px;
            padding: 22px;
            margin-top: 14px;
        }
        .mm-panel-title {
            font-size: 0.82rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #aab3c2;
            margin-bottom: 14px;
        }
        .mm-colors {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .mm-color {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #1b202b;
            border: 1px solid #303746;
            border-radius: 999px;
            padding: 7px 11px 7px 8px;
            font-weight: 700;
            font-size: 0.84rem;
        }
        .mm-dot {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-block;
            border: 2px solid rgba(255,255,255,.55);
            box-shadow: inset 0 1px 2px rgba(0,0,0,.35);
        }
        .mm-guess-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 10px;
            margin-top: 4px;
        }
        .mm-history {
            min-width: 0;
            background: #11151e;
            border: 1px solid #292f3b;
            border-radius: 12px;
            padding: 10px;
        }
        .mm-attempt {
            color: #7f899b;
            font-weight: 800;
            font-size: 0.72rem;
            margin-bottom: 8px;
        }
        .mm-pegs {
            display: flex;
            gap: 5px;
            align-items: center;
        }
        .mm-pegs .mm-peg {
            width: 24px;
            height: 24px;
        }
        .mm-peg {
            width: 29px;
            height: 29px;
            border-radius: 50%;
            border: 2px solid rgba(255,255,255,.35);
            box-shadow: inset 0 2px 4px rgba(0,0,0,.28);
        }
        .mm-feedback {
            display: flex;
            gap: 7px;
            align-items: center;
            white-space: nowrap;
        }
        .mm-badge {
            border-radius: 999px;
            padding: 5px 9px;
            background: #1b202b;
            border: 1px solid #303746;
            color: #cbd2dd;
            font-size: 0.75rem;
            font-weight: 700;
        }
        .mm-empty {
            color: #70798a;
            text-align: center;
            padding: 28px 10px 12px;
        }
        .mm-result {
            border-radius: 14px;
            padding: 16px 18px;
            margin-top: 14px;
            font-weight: 700;
        }
        .mm-result-win {
            background: rgba(34,197,94,.10);
            border: 1px solid rgba(34,197,94,.35);
            color: #86efac;
        }
        .mm-result-loss {
            background: rgba(239,68,68,.10);
            border: 1px solid rgba(239,68,68,.35);
            color: #fca5a5;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _peg(code: str, size: str = "29px") -> str:
    color = COLOR_MAP.get(code, "#64748b")
    return (
        f'<span class="mm-peg" style="width:{size};height:{size};'
        f'background:{color};display:inline-block;"></span>'
    )


def _color_legend(colors: tuple[str, ...]) -> str:
    return "".join(
        f'<span class="mm-color"><span class="mm-dot" style="background:{COLOR_MAP[c]}"></span>{c}</span>'
        for c in colors
    )


def new_game() -> None:
    game = _ensure_state()
    difficulty = game["difficulty"]
    core = MastermindGame()
    config = SessionConfig(game="mastermind", difficulty=difficulty, mode="practice")
    state = core.setup(config)
    game.update(
        {
            "screen": "game",
            "code": state.data["code"],
            "attempts": 0,
            "history": [],
            "max_attempts": state.data["max_attempts"],
            "colors": DIFFICULTIES[difficulty]["colors"],
            "length": DIFFICULTIES[difficulty]["length"],
            "message": "",
            "outcome": None,
            "score": 0,
        }
    )


def render_setup() -> None:
    game = _ensure_state()
    _inject_styles()

    st.markdown(
        """
        <div class="mm-shell mm-hero">
            <div class="mm-kicker">Codebreaker</div>
            <div class="mm-title">Mastermind</div>
            <div class="mm-subtitle">Crack the hidden color sequence before your attempts run out.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "mastermind_setup_difficulty" not in st.session_state:
        st.session_state["mastermind_setup_difficulty"] = game["difficulty"].title()

    difficulty_label = st.radio(
        "Difficulty",
        ["Easy", "Medium", "Hard"],
        key="mastermind_setup_difficulty",
        horizontal=True,
    )
    difficulty = difficulty_label.lower()
    settings = DIFFICULTIES[difficulty]

    st.markdown(
        f"""
        <div class="mm-panel mm-shell">
            <div class="mm-panel-title">Your challenge</div>
            <div style="font-size:1.05rem;font-weight:700;">
                {settings["length"]} color code · {settings["attempts"]} attempts
            </div>
            <div style="color:#8d96a8;margin-top:7px;">
                Available colors: {" · ".join(settings["colors"])}
            </div>
            <div class="mm-colors" style="margin-top:15px;">
                {_color_legend(settings["colors"])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Start Game", type="primary", use_container_width=True):
        game["difficulty"] = difficulty
        new_game()
        st.rerun()


def render_game() -> None:
    game = _ensure_state()
    _inject_styles()

    remaining = max(0, game["max_attempts"] - game["attempts"])

    st.markdown(
        f"""
        <div class="mm-shell mm-hero">
            <div class="mm-kicker">Codebreaker</div>
            <div class="mm-title">Mastermind</div>
            <div class="mm-subtitle">
                {game["difficulty"].title()} · Find the hidden {game["length"]}-color code.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stat1, stat2, stat3 = st.columns(3)
    with stat1:
        st.markdown(
            f'<div class="mm-stat"><div class="mm-stat-label">Attempts left</div>'
            f'<div class="mm-stat-value">{remaining} / {game["max_attempts"]}</div></div>',
            unsafe_allow_html=True,
        )
    with stat2:
        st.markdown(
            f'<div class="mm-stat"><div class="mm-stat-label">Code length</div>'
            f'<div class="mm-stat-value">{game["length"]} colors</div></div>',
            unsafe_allow_html=True,
        )
    with stat3:
        st.markdown(
            f'<div class="mm-stat"><div class="mm-stat-label">Score</div>'
            f'<div class="mm-stat-value">{game["score"]}</div></div>',
            unsafe_allow_html=True,
        )

    colors_col, guesses_col = st.columns([1, 2], gap="large")

    with colors_col:
        st.markdown(
            '<div class="mm-panel" style="margin-top:14px;">'
            '<div class="mm-panel-title">Available colors</div>'
            '<div class="mm-colors">' + _color_legend(game["colors"]) + '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="mm-panel" style="margin-top:14px;">'
            '<div class="mm-panel-title">Make a guess</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"Enter {game['length']} colors separated by spaces.")
        raw = st.text_input(
            "Guess",
            placeholder="R G B Y",
            label_visibility="collapsed",
            key="mastermind_guess",
            disabled=game["outcome"] is not None,
        )
        if st.button("Submit Guess", type="primary", use_container_width=True):
            try:
                guess = validate_guess(raw, game["difficulty"])
            except ValueError as exc:
                game["message"] = str(exc)
                st.rerun()
            else:
                exact, misplaced = evaluate_guess(tuple(game["code"]), guess)
                game["attempts"] += 1
                game["history"].append((guess, exact, misplaced))
                game["message"] = f"Exact: {exact} · Misplaced: {misplaced}"
                if exact == game["length"]:
                    game["outcome"] = "win"
                    game["score"] = (game["max_attempts"] - game["attempts"] + 1) * 10
                elif game["attempts"] >= game["max_attempts"]:
                    game["outcome"] = "loss"
                st.rerun()

        if game["message"] and game["outcome"] is None:
            st.info(game["message"])

        st.markdown("</div>", unsafe_allow_html=True)

    with guesses_col:
        st.markdown(
            '<div class="mm-panel" style="margin-top:14px;"><div class="mm-panel-title">Your guesses</div>',
            unsafe_allow_html=True,
        )

        if game["history"]:
            st.markdown('<div class="mm-guess-grid">', unsafe_allow_html=True)
            for index, (guess, exact, misplaced) in enumerate(game["history"], start=1):
                pegs = "".join(_peg(color) for color in guess)
                st.markdown(
                    f"""
                    <div class="mm-history">
                        <div class="mm-attempt">#{index:02d}</div>
                        <div class="mm-pegs">{pegs}</div>
                        <div class="mm-feedback" style="margin-top:8px;">
                            <span class="mm-badge">Exact {exact}</span>
                            <span class="mm-badge">Misplaced {misplaced}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="mm-empty">No guesses yet. Make your first attempt below.</div>',
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    if game["outcome"] == "win":
        st.markdown(
            f'<div class="mm-result mm-result-win mm-shell">Code cracked. Score: {game["score"]}</div>',
            unsafe_allow_html=True,
        )
    elif game["outcome"] == "loss":
        code = "".join(_peg(color, "30px") for color in game["code"])
        st.markdown(
            f'<div class="mm-result mm-result-loss mm-shell">Code not cracked. The sequence was '
            f'<span style="display:inline-flex;gap:7px;vertical-align:middle;margin-left:8px;">{code}</span></div>',
            unsafe_allow_html=True,
        )

    if game["outcome"] is not None:
        if st.button("Play Again", type="primary", use_container_width=True):
            new_game()
            st.rerun()

    if game["outcome"] == "win":
        st.markdown(
            f'<div class="mm-result mm-result-win mm-shell">Code cracked. Score: {game["score"]}</div>',
            unsafe_allow_html=True,
        )
    elif game["outcome"] == "loss":
        code = "".join(_peg(color, "30px") for color in game["code"])
        st.markdown(
            f'<div class="mm-result mm-result-loss mm-shell">Code not cracked. The sequence was '
            f'<span style="display:inline-flex;gap:7px;vertical-align:middle;margin-left:8px;">{code}</span></div>',
            unsafe_allow_html=True,
        )

    if game["outcome"] is not None:
        if st.button("Play Again", type="primary", use_container_width=True):
            new_game()
            st.rerun()


def render_mastermind() -> None:
    if _ensure_state()["screen"] == "setup":
        render_setup()
    else:
        render_game()
