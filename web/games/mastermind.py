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
        st.session_state["mastermind"] = {
            "screen": "setup",
            "difficulty": "medium",
        }

    game = st.session_state["mastermind"]
    game.setdefault("screen", "setup")
    game.setdefault("difficulty", "medium")
    game.setdefault("round_id", 0)
    return game


def _sync_setup_preferences() -> None:
    game = _ensure_state()
    game["difficulty"] = st.session_state["mastermind_setup_difficulty"].lower()


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        [data-testid="stMainBlockContainer"] {
            max-width: 1180px !important;
            margin: 0 auto !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }

        .mm-hero {
            padding: 0.25rem 0 1rem 0;
        }

        .mm-kicker {
            color: #8fa1b8;
            font-size: 0.74rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .mm-title {
            font-size: 2.55rem;
            font-weight: 850;
            line-height: 1;
            margin: 0;
        }

        .mm-subtitle {
            color: #9aa5b5;
            margin-top: 0.65rem;
            font-size: 0.98rem;
        }

        .mm-stat {
            min-height: 78px;
            box-sizing: border-box;
            padding: 15px 17px;
            border: 1px solid #2c3442;
            border-radius: 14px;
            background: linear-gradient(145deg, #171c26, #11151c);
        }

        .mm-stat-label,
        .mm-panel-title {
            color: #9aa6b7;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.09em;
            text-transform: uppercase;
        }

        .mm-stat-value {
            margin-top: 5px;
            font-size: 1.35rem;
            font-weight: 850;
        }

        .mm-panel {
            box-sizing: border-box;
            width: 100%;
            padding: 18px;
            border: 1px solid #2c3442;
            border-radius: 16px;
            background: linear-gradient(145deg, #151a23, #11151c);
        }

        .mm-colors {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }

        .mm-color {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 7px 10px 7px 8px;
            border: 1px solid #30394a;
            border-radius: 999px;
            background: #1a202b;
            color: #f1f5f9;
            font-size: 0.82rem;
            font-weight: 750;
        }

        .mm-dot {
            width: 19px;
            height: 19px;
            border-radius: 50%;
            border: 2px solid rgba(255,255,255,.55);
            box-sizing: border-box;
            display: inline-block;
        }

        .mm-guess-header {
            height: 52px;
            box-sizing: border-box;
            display: flex;
            align-items: center;
            padding: 0 18px;
            border: 1px solid #2c3442;
            border-radius: 14px;
            background: linear-gradient(145deg, #151a23, #11151c);
        }

        .mm-history-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
            margin-top: 12px;
        }

        .mm-history-card {
            min-height: 112px;
            box-sizing: border-box;
            padding: 14px 15px;
            border: 1px solid #2c3442;
            border-radius: 14px;
            background: #11161f;
        }

        .mm-attempt {
            color: #7f8ca0;
            font-size: 0.7rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            margin-bottom: 12px;
        }

        .mm-pegs {
            display: flex;
            align-items: center;
            gap: 7px;
        }

        .mm-peg {
            width: 27px;
            height: 27px;
            border-radius: 50%;
            border: 2px solid rgba(255,255,255,.35);
            box-sizing: border-box;
            box-shadow: inset 0 2px 4px rgba(0,0,0,.28);
        }

        .mm-feedback {
            display: flex;
            gap: 6px;
            margin-top: 13px;
        }

        .mm-badge {
            padding: 5px 8px;
            border: 1px solid #30394a;
            border-radius: 999px;
            background: #1a202b;
            color: #cbd5e1;
            font-size: 0.72rem;
            font-weight: 750;
        }

        .mm-empty {
            margin-top: 12px;
            min-height: 112px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-sizing: border-box;
            padding: 20px;
            border: 1px dashed #30394a;
            border-radius: 14px;
            color: #7f8ca0;
            text-align: center;
        }

        .mm-result {
            margin-top: 14px;
            padding: 14px 16px;
            border-radius: 12px;
            font-weight: 750;
        }

        .mm-win {
            border: 1px solid rgba(34,197,94,.35);
            background: rgba(34,197,94,.10);
            color: #86efac;
        }

        .mm-loss {
            border: 1px solid rgba(239,68,68,.35);
            background: rgba(239,68,68,.10);
            color: #fca5a5;
        }

        .mm-code {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            margin-left: 8px;
            vertical-align: middle;
        }

        @media (max-width: 800px) {
            .mm-history-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _peg(code: str, size: int = 27) -> str:
    color = COLOR_MAP.get(code, "#64748b")
    return (
        f'<span class="mm-peg" style="width:{size}px;height:{size}px;'
        f'background:{color};"></span>'
    )


def _color_legend(colors: tuple[str, ...]) -> str:
    return "".join(
        f'<span class="mm-color">'
        f'<span class="mm-dot" style="background:{COLOR_MAP[color]}"></span>{color}'
        f'</span>'
        for color in colors
    )


def new_game() -> None:
    game = _ensure_state()
    difficulty = game["difficulty"]

    state = MastermindGame().setup(
        SessionConfig(
            game="mastermind",
            difficulty=difficulty,
            mode="practice",
        )
    )

    game["round_id"] += 1
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
        <div class="mm-hero">
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
        on_change=_sync_setup_preferences,
    )
    difficulty = difficulty_label.lower()
    settings = DIFFICULTIES[difficulty]

    with st.container(border=True):
        st.markdown("**Challenge**")
        st.write(
            f'{settings["length"]} colors · {settings["attempts"]} attempts · '
            f'Colors: {" · ".join(settings["colors"])}'
        )

    if st.button("Start Game", type="primary", use_container_width=True):
        game["difficulty"] = difficulty
        new_game()
        st.rerun()


def _render_history(history: list) -> None:
    if not history:
        st.markdown(
            '<div class="mm-empty">No guesses yet. Your first attempt will appear here.</div>',
            unsafe_allow_html=True,
        )
        return

    cards = []
    for index, (guess, exact, misplaced) in enumerate(history, start=1):
        pegs = "".join(_peg(color) for color in guess)
        cards.append(
            f"""
            <div class="mm-history-card">
                <div class="mm-attempt">ATTEMPT #{index:02d}</div>
                <div class="mm-pegs">{pegs}</div>
                <div class="mm-feedback">
                    <span class="mm-badge">Exact {exact}</span>
                    <span class="mm-badge">Misplaced {misplaced}</span>
                </div>
            </div>
            """
        )

    st.markdown(
        '<div class="mm-history-grid">' + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )


def render_game() -> None:
    game = _ensure_state()
    _inject_styles()

    remaining = max(0, game["max_attempts"] - game["attempts"])

    st.markdown(
        f"""
        <div class="mm-hero">
            <div class="mm-kicker">Codebreaker</div>
            <div class="mm-title">Mastermind</div>
            <div class="mm-subtitle">
                {game["difficulty"].title()} · Find the hidden {game["length"]}-color code.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    stat1, stat2, stat3 = st.columns(3, gap="medium")
    stats = [
        (stat1, "Attempts Left", f"{remaining} / {game['max_attempts']}"),
        (stat2, "Code Length", f"{game['length']} colors"),
        (stat3, "Score", str(game["score"])),
    ]
    for column, label, value in stats:
        with column:
            st.markdown(
                f'<div class="mm-stat"><div class="mm-stat-label">{label}</div>'
                f'<div class="mm-stat-value">{value}</div></div>',
                unsafe_allow_html=True,
            )

    st.write("")

    colors_col, guesses_col = st.columns([1, 2], gap="large")

    with colors_col:
        st.markdown(
            '<div class="mm-panel">'
            '<div class="mm-panel-title">Available Colors</div>'
            f'<div class="mm-colors">{_color_legend(game["colors"])}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.write("")

        with st.container(border=True):
            st.markdown("**Make a Guess**")
            st.caption(f'Enter {game["length"]} colors separated by spaces.')

            raw = st.text_input(
                "Guess",
                placeholder="R G B Y",
                label_visibility="collapsed",
                key=f"mastermind_guess_{game['round_id']}",
                disabled=game["outcome"] is not None,
            )

            if st.button(
                "Submit Guess",
                type="primary",
                use_container_width=True,
                key="mastermind_submit_guess",
                disabled=game["outcome"] is not None,
            ):
                try:
                    guess = validate_guess(raw, game["difficulty"])
                except ValueError as exc:
                    game["message"] = str(exc)
                else:
                    exact, misplaced = evaluate_guess(tuple(game["code"]), guess)
                    game["attempts"] += 1
                    game["history"].append((guess, exact, misplaced))
                    game["message"] = f"Exact: {exact} · Misplaced: {misplaced}"

                    if exact == game["length"]:
                        game["outcome"] = "win"
                        game["score"] = (
                            game["max_attempts"] - game["attempts"] + 1
                        ) * 10
                    elif game["attempts"] >= game["max_attempts"]:
                        game["outcome"] = "loss"

                st.rerun()

            if game["message"] and game["outcome"] is None:
                st.info(game["message"])

    with guesses_col:
        st.markdown(
            '<div class="mm-guess-header"><div class="mm-panel-title">Your Guesses</div></div>',
            unsafe_allow_html=True,
        )
        _render_history(game["history"])

    if game["outcome"] == "win":
        st.markdown(
            f'<div class="mm-result mm-win">Code cracked. Score: {game["score"]}</div>',
            unsafe_allow_html=True,
        )
    elif game["outcome"] == "loss":
        code = "".join(_peg(color, 30) for color in game["code"])
        st.markdown(
            f'<div class="mm-result mm-loss">Code not cracked. The sequence was'
            f'<span class="mm-code">{code}</span></div>',
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
