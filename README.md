# Python Games Hub

A complete terminal-based Python game platform featuring **nine distinct games**
and shared systems for sessions, profiles, statistics, achievements, progression,
Quick Play, and persistence.

Each game keeps its own rules and personality while the platform provides the
common infrastructure that makes the collection feel like one product.

## Games

| Game | Highlights |
|---|---|
| **Tic-Tac-Toe** | PvP/PvC, difficulty levels, minimax AI, hints, scoring |
| **Connect Four** | PvP/PvC, difficulty levels, minimax AI, hints, scoring |
| **Hangman** | Categories, difficulty-based attempts, hints, scoring |
| **Rock Paper Scissors** | RPS, Lizard-Spock, fixed-length matches, personalities |
| **Word Scramble** | Difficulty levels, hints, scoring, local fallback |
| **Snake** | Real-time controls, speeds, power-ups, scoring |
| **Minesweeper** | First-click safety, flood reveal, flagging, difficulty boards |
| **Typing Test** | Timed typing, WPM, accuracy, scoring |
| **Mastermind** | Hidden color codes, exact/misplaced feedback, difficulty levels |
## Platform

- Unified terminal Game Hub and Quick Play
- Static Game Registry
- Shared `SessionConfig`, `GameState`, and `GameResult`
- Competitive and Practice modes
- Profiles, progression, statistics, and achievements
- Game-specific difficulty and configuration
- Independently runnable games
- Local JSON persistence
- Automated regression testing
```text
Game Hub / Quick Play
        ↓
Game Registry → Session Configuration
        ↓
Game → GameState → GameResult
        ↓
Statistics / Achievements / Progression
        ↓
Persistence
```

Shared infrastructure lives in `engine/`; game rules, gameplay state, AI,
scoring, and interaction remain inside `games/`.
## Technology

Python 3.10+ · Standard library at runtime · pytest · JSON persistence · Terminal/CLI
## Testing

Automated regression tests cover the games, shared engine, hub flow,
persistence, profiles, statistics, achievements, settings, Quick Play,
Practice Mode, difficulty, and cross-system integration.
```bash
python -m pytest -q
```

## Running
```bash
python main.py
```

Individual games:
```bash
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

## Structure
```text
python-games-hub/
├── main.py
├── engine/
├── games/
├── tests/
├── pytest.ini
├── README.md
└── PROJECT DOCUMENTATION.md
```

Runtime player data is stored in `.game_data/` and ignored by Git.

## Scope

Python Games Hub is intentionally a **terminal game platform**. It is not a GUI,
web, online multiplayer, database-backed platform, plugin ecosystem, or generic
game-engine framework.

The goal is a maintainable Python project where nine different games operate
as one coherent product.
## Documentation

**[PROJECT DOCUMENTATION.md](PROJECT DOCUMENTATION.md)** contains the complete
technical documentation covering architecture, systems, difficulty mapping,
game-specific behavior, persistence, testing, design principles, and scope.
