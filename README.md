# Python Games Hub

A complete terminal-based Python game platform featuring **nine distinct
games** and shared systems for sessions, profiles, statistics,
achievements, progression, Quick Play, and persistence.

Each game retains its own rules and personality while the platform
provides consistent configuration, scoring, and player systems.

## Games

  -----------------------------------------------------------------------
  Game                                Highlights
  ----------------------------------- -----------------------------------
  **Tic-Tac-Toe**                     PvP/PvC, difficulty levels, minimax
                                      AI, hints, scoring, and streaks

  **Connect Four**                    PvP/PvC, difficulty levels, minimax
                                      AI, hints, and scoring

  **Hangman**                         Categories, difficulty-based
                                      attempts, hints, ASCII stages, and
                                      scoring

  **Rock Paper Scissors**             Classic RPS, Lizard-Spock,
                                      fixed-length matches, and computer
                                      personalities

  **Word Scramble**                   Difficulty-based word selection,
                                      hints, scoring, and local fallback

  **Snake**                           Real-time terminal gameplay,
                                      multiple speeds, power-ups,
                                      wrap-around, and high-score
                                      tracking

  **Minesweeper**                     First-click safety, flood reveal,
                                      flagging, and difficulty-based
                                      boards

  **Typing Test**                     Timed typing challenges, WPM,
                                      accuracy, and scoring

  **Mastermind**                      Hidden color codes, exact/misplaced
                                      feedback, and difficulty levels
  -----------------------------------------------------------------------

## Features

-   Unified terminal Game Hub with Quick Play
-   Static game registry and shared session configuration
-   Standardized `SessionConfig`, `GameState`, and `GameResult`
    contracts
-   Competitive and Practice modes
-   Persistent profiles, statistics, achievements, and progression
-   Game-specific difficulty and configuration options
-   Independently runnable games
-   Local JSON persistence
-   Automated regression tests

### Architecture

``` text
Game Hub / Quick Play
        |
   Game Registry
        |
 Session Configuration
        |
   Game Gameplay
        |
   GameState
        |
   GameResult
        |
Statistics / Achievements / Progression
        |
    Persistence
```

Shared infrastructure lives in `engine/`, while game rules, gameplay
state, AI, scoring, and interaction remain in `games/`.

## Technology

-   Python 3.10+
-   Python standard library for runtime functionality
-   `pytest` for automated testing
-   JSON for local persistence
-   Terminal / command-line interface

## Getting Started

### 1. Clone the repository

``` bash
git clone https://github.com/Ayush-Sarkar-04/python-games-hub.git
cd python-games-hub
```

### 2. Create a virtual environment (optional)

Windows PowerShell:

``` powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

``` bash
python -m pip install -r requirements.txt
```

### 4. Launch the Game Hub

``` bash
python main.py
```

## Run Individual Games

Each game can also be launched independently:

``` bash
python games/tic_tac_toe.py
python games/connect_four.py
python games/hangman.py
python games/rock_paper_scissors.py
python games/word_scramble.py
python games/snake.py
python games/minesweeper.py
python games/typing_test.py
python games/mastermind.py
```

## Testing

The project has a regression suite covering game mechanics, shared
engine components, hub flow, persistence, profiles, statistics,
achievements, settings, difficulty configuration, Practice mode, and
cross-system integration.

**Latest verified result: 130 tests passed.**

Run the complete suite:

``` bash
python -m pytest -q
```

## Project Structure

``` text
python-games-hub/
├── main.py
├── engine/
│   ├── game.py
│   ├── state.py
│   ├── result.py
│   ├── persistence.py
│   ├── profiles.py
│   ├── statistics.py
│   ├── achievements.py
│   ├── settings.py
│   └── utils.py
├── games/
│   ├── tic_tac_toe.py
│   ├── connect_four.py
│   ├── hangman.py
│   ├── rock_paper_scissors.py
│   ├── word_scramble.py
│   ├── snake.py
│   ├── minesweeper.py
│   ├── typing_test.py
│   └── mastermind.py
├── tests/
├── pytest.ini
├── requirements.txt
├── README.md
└── PROJECT DOCUMENTATION.md
```

Runtime player data is stored in `.game_data/` and ignored by Git.

## Design Principles

-   Keep game-specific mechanics inside their respective modules.
-   Share infrastructure only where it improves consistency and
    maintainability.
-   Use explicit contracts for configuration, state, and results.
-   Keep the registry static and predictable.
-   Separate Practice sessions from competitive records and progression.
-   Prefer readable Python and testable behavior over unnecessary
    abstraction.

## Scope

Python Games Hub is intentionally a **terminal-based game platform**. It
does not include a GUI, web interface, online multiplayer,
database-backed storage, a plugin ecosystem, or a generic game-engine
framework.

The objective is to demonstrate maintainable Python architecture through
nine different games operating as one coherent application.

## Documentation

See **[PROJECT DOCUMENTATION.md](PROJECT%20DOCUMENTATION.md)** for the
detailed technical reference covering architecture, shared systems,
game-specific behavior, difficulty mapping, persistence, testing, design
decisions, and project scope.
