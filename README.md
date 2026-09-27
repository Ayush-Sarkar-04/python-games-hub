# Python Games Hub V2

A terminal-based Python games hub rebuilt around a shared session and game architecture while preserving the working V1 gameplay implementations.

## V2 Sprint 1

Sprint 1 establishes the foundation for the V2 architecture. The six V1 games are carried into `games/` with the previously approved V1 fixes preserved; gameplay migration begins in later sprints.

### Foundation

- Hub-owned `SessionConfig`
- Shared `GameState`
- Shared `GameResult`
- Static game registry
- Shared utility functions
- JSON persistence boundary
- Profile, statistics, achievement, and settings foundations
- Flat test suite under `tests/`

## Games

- **Tic-Tac-Toe** — PvC/PvP, three difficulty levels, computer personalities, minimax on Hard, and win-streak tracking.
- **Hangman** — category-based word selection, difficulty, hints, ASCII stages, and streak tracking.
- **Rock Paper Scissors** — standard RPS with optional Lizard-Spock, match modes, personalities, history bias, and streak tracking.
- **Word Scramble** — API-backed word selection with fallback words, difficulty, hints, attempts, and streak tracking.
- **Connect Four** — PvC/PvP, difficulty levels, gravity, win detection, and Hard-mode minimax.
- **Snake** — real-time terminal gameplay with multiple speeds, keyboard controls, pause/quit, power-ups, wrap-around, and scoreboard tracking.

## Project Structure

```text
python-games-hub-v2/
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

## Requirements

The games use Python's standard library and have no runtime third-party dependencies.

Python 3.10+ is recommended.

For development and testing, install `pytest`.

## Running

From the project directory:

```bash
python main.py
```

The individual game modules remain independently runnable during the migration process.

## V2 Architecture

`main.py` owns the hub and session configuration. `engine/` contains the shared architecture and supporting systems. `games/` contains the individual game implementations. `tests/` contains the complete Sprint 1 test suite in one flat directory.

The V2 design intentionally avoids a plugin framework, dynamic game discovery, GUI/web layers, databases, and other unnecessary infrastructure. The goal is to make the existing games easier to extend without turning the project into a generic game engine.

## Scope

Sprint 1 is foundation-only. The existing gameplay behavior is preserved. Tic-Tac-Toe migration starts Sprint 2, followed by Connect Four as the architectural stress test, then the remaining games and Snake in later sprints.
