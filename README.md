# Python Games Hub

A terminal-based Python games hub with six independently runnable games and a shared session, state, result, and persistence layer.

## Games

- **Tic-Tac-Toe** — Player vs Computer or Player vs Player, Easy/Medium/Hard, computer personalities, minimax, hints, replay, and win streaks.
- **Connect Four** — Player vs Computer or Player vs Player, Easy/Medium/Hard, gravity, win detection, minimax, hints, replay, and win streaks.
- **Hangman** — Category-based word selection, difficulty levels, hints, ASCII stages, and streak tracking.
- **Rock Paper Scissors** — Standard RPS or Lizard-Spock, single games or matches, computer personalities, history-based play, and streak tracking.
- **Word Scramble** — API-backed word selection with local fallbacks, difficulty levels, hints, attempts, and streak tracking.
- **Snake** — Real-time terminal gameplay with multiple speeds, keyboard controls, pause/quit, power-ups, wrap-around, and score tracking.

All six games are connected to the hub. Each game remains independently runnable, while the hub owns session difficulty, mode, and game-specific configuration.

## Architecture

```text
python-games-hub/
├── main.py
├── engine/
│   ├── __init__.py
│   ├── game.py
│   ├── state.py
│   ├── result.py
│   ├── utils.py
│   ├── persistence.py
│   ├── profiles.py
│   ├── statistics.py
│   ├── achievements.py
│   └── settings.py
├── games/
│   ├── __init__.py
│   ├── tic_tac_toe.py
│   ├── connect_four.py
│   ├── hangman.py
│   ├── rock_paper_scissors.py
│   ├── word_scramble.py
│   └── snake.py
├── tests/
│   ├── test_games.py
│   ├── test_game.py
│   ├── test_result.py
│   ├── test_state.py
│   ├── test_utils.py
│   ├── test_persistence.py
│   ├── test_systems.py
│   ├── test_registry.py
│   └── test_flow.py
├── README.md
├── gameplan.md
└── .gitignore
```

### `main.py`

Owns the hub menu, game registry, session configuration, and launching of games that are connected to the hub.

### `engine/`

Contains shared models and supporting systems:

- `game.py` — session configuration and game contract
- `state.py` — mutable state for a game session
- `result.py` — standard game result model
- `utils.py` — shared terminal input and display helpers
- `persistence.py` — JSON storage
- `profiles.py` — player profile storage
- `statistics.py` — game statistics storage
- `achievements.py` — achievement storage
- `settings.py` — application settings storage

### `games/`

Contains the six game implementations. Each game keeps its gameplay rules and terminal presentation locally rather than forcing every game into the same feature set.

### `tests/`

`test_games.py` contains the tests for all six games. The remaining test files cover the shared engine, persistence, registry, and hub flow.

## Running

Python 3.10+ is recommended.

Run the hub:

```bash
python main.py
```

Run an individual game:

```bash
python games/tic_tac_toe.py
python games/connect_four.py
python games/hangman.py
python games/rock_paper_scissors.py
python games/word_scramble.py
python games/snake.py
```

The project uses the Python standard library at runtime. `pytest` is used for development and testing.

Run the test suite:

```bash
pytest -q
```

## Design Principles

- Keep game rules inside their game modules.
- Share only genuinely common session and infrastructure concerns.
- Record real player moves, not AI simulations or speculative states.
- Keep game-specific features optional instead of forcing a uniform interface.
- Keep the hub static and predictable rather than introducing dynamic plugin discovery.
- Prefer straightforward Python over unnecessary abstraction.
- Keep the games independently runnable as well as accessible through the hub where integrated.

## Scope

The project focuses on terminal games and a clean, maintainable Python architecture. It does not aim to become a GUI, web, online multiplayer, database, or plugin platform.
