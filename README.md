# Python Games Hub

A terminal-based Python games hub with six independently runnable games and a shared session, state, result, persistence, statistics, achievements, and progression layer.

## Games

- **Tic-Tac-Toe** — Player vs Computer or Player vs Player, Easy/Medium/Hard, Advanced custom minimax depth, computer personalities, minimax, hints, replay, and win streaks.
- **Connect Four** — Player vs Computer or Player vs Player, Easy/Medium/Hard, Advanced custom minimax depth, gravity, win detection, minimax, hints, replay, and win streaks.
- **Hangman** — Category-based word selection, difficulty levels, Advanced custom attempt count, hints, ASCII stages, scoring, and streak tracking.
- **Rock Paper Scissors** — Standard RPS or Lizard-Spock, single games or matches, computer personalities, history-based play, scoring, and streak tracking.
- **Word Scramble** — API-backed word selection with local fallbacks, difficulty levels, hints, attempt-based scoring, and streak tracking.
- **Snake** — Real-time terminal gameplay with multiple speeds, keyboard controls, pause/quit, power-ups, wrap-around, score tracking, and top-run records.

All six games are connected to the hub. The hub owns session configuration, while each game owns its gameplay rules.

## V2 Architecture

```text
python-games-hub/
├── main.py
├── engine/
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
│   ├── tic_tac_toe.py
│   ├── connect_four.py
│   ├── rock_paper_scissors.py
│   ├── hangman.py
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

### Hub flow

```text
Hub
 ↓
Play / Quick Play
 ↓
Choose Game
 ↓
Configure Session
 ↓
Difficulty / Advanced
 ↓
Game receives SessionConfig
 ↓
GameResult
 ↓
Statistics + Achievements + Profile Progression
 ↓
Persistence
```

The registry is the single source of game registration. Each registry entry declares its game class, supported modes, standard difficulties, capabilities, configuration options, and custom parameters where applicable.

## Shared systems

- **SessionConfig** — hub-owned difficulty, mode, custom settings, and game options.
- **GameState** — explicit mutable state and committed move history.
- **GameResult** — standardized outcome, score, move count, and structured configuration metadata.
- **Statistics** — competitive-only per-game records, streaks, scoring records, and Snake top runs.
- **Achievements** — code-defined achievement definitions with profile-owned persisted unlock state.
- **Profile** — player identity, aggregate XP/level, and cosmetic terminal-style unlocks.
- **Settings** — banner style and advisory difficulty suggestions.
- **Persistence** — safe JSON storage with atomic writes.
- **Export** — readable Markdown player summary containing profile, statistics, achievements, and progression.

Practice sessions are deliberately excluded from competitive statistics, achievements, and competitive progression.

## Custom Difficulty

Advanced / Custom is shown only for games that declare meaningful custom parameters:

- Tic-Tac-Toe: minimax depth **1–9**
- Connect Four: minimax depth **1–6**
- Hangman: attempts **3–10**

The game validates the parameters. The hub does not silently clamp invalid values.

Snake intentionally remains Easy/Medium/Hard only.

## Progression

Competitive completed sessions contribute simple aggregate XP. A competitive win contributes an additional XP point. Snake `game_over` runs contribute activity but are never treated as synthetic wins.

Progression is cosmetic-only. It does not alter gameplay, balancing, or player statistics.

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

Runtime persistence is stored under `.game_data/` and is ignored by Git.

Run the test suite:

```bash
python -m pytest -q
```

## Design Principles

- Keep game rules inside their game modules.
- Share only genuinely common session and infrastructure concerns.
- Record real player moves, not AI simulations or speculative states.
- Keep game-specific features optional instead of forcing a uniform interface.
- Keep the hub static and predictable rather than introducing dynamic plugin discovery.
- Prefer straightforward Python over unnecessary abstraction.
- Keep all six games independently runnable.
- Keep progression aggregate and cosmetic-only.

## Scope

The project remains a Python terminal game platform. It does not aim to become a GUI, web application, online multiplayer platform, database-backed service, generic game engine, plugin ecosystem, or AI research platform.
