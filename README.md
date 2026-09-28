# Python Games Hub

A terminal-based Python Games Hub containing six independently runnable
games, a shared session/configuration layer, standardized game state and
results, persistent player systems, competitive statistics,
achievements, progression, Quick Play, and configurable terminal
presentation.

The project is intentionally built with straightforward Python and
standard-library components where possible. The hub owns session-level
configuration and shared systems, while each game owns its gameplay
rules.

## Games

-   **Tic-Tac-Toe** --- Player vs Computer or Player vs Player,
    Easy/Medium/Hard, Advanced custom minimax depth, computer
    personalities, minimax AI, hints, replay, rematch, scoring, and win
    streaks.
-   **Connect Four** --- Player vs Computer or Player vs Player,
    Easy/Medium/Hard, Advanced custom minimax depth, gravity, win
    detection, minimax AI, hints, replay, rematch, scoring, and win
    streaks.
-   **Hangman** --- Category-based word selection, Easy/Medium/Hard,
    Advanced custom attempt count, hints, ASCII stages, scoring,
    rematch, and streak tracking.
-   **Rock Paper Scissors** --- Standard RPS or Lizard-Spock, single
    games or fixed-length matches, computer personalities, history-based
    play, scoring, rematch, and streak tracking.
-   **Word Scramble** --- API-backed word selection with local
    fallbacks, difficulty levels, hints, attempt-based scoring, rematch,
    and streak tracking.
-   **Snake** --- Real-time terminal gameplay with multiple speeds,
    keyboard controls, pause/quit, power-ups, wrap-around, score
    tracking, rematch, and top-run records.

All six games are connected to the hub and remain independently
runnable.

------------------------------------------------------------------------

## V2 Architecture

``` text
python-games-hub/
├── main.py
├── pytest.ini
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
└── .gitignore
```

Runtime player data is stored separately under `.game_data/` and is
ignored by Git.

### Registry

The hub uses a single static game registry as the source of truth for
game registration.

Each registry entry defines the game's:

-   Game class
-   Supported modes
-   Standard difficulties
-   Capabilities
-   Game-specific configuration options
-   Custom parameters where supported

The hub uses these capabilities to present features without introducing
dynamic plugin discovery.

------------------------------------------------------------------------

## Hub Flow

``` text
                    ┌──────────────┐
                    │     Hub      │
                    └──────┬───────┘
                           │
                 ┌─────────┴─────────┐
                 │                   │
              Play              Quick Play
                 │                   │
                 └─────────┬─────────┘
                           ↓
                     Choose Game
                           ↓
                   Configure Session
                           ↓
              Difficulty / Advanced
                           ↓
                    SessionConfig
                           ↓
                     Game.setup()
                           ↓
                      Game.play()
                           ↓
                      GameResult
                           ↓
          ┌────────────────┼────────────────┐
          ↓                ↓                ↓
      Statistics       Achievements      Progression
          └────────────────┼────────────────┘
                           ↓
                       Persistence
                           ↓
                Profile / Summary / UI
```

The game itself owns gameplay rules and mutable game state. When a game is
launched through the hub, the hub owns session configuration and the
cross-game systems that consume completed results. Standalone game entry
points may provide equivalent local configuration before creating the same
`SessionConfig`.

------------------------------------------------------------------------

## Shared Systems

### Session Configuration

`SessionConfig` represents the configuration selected before a game starts.
The Game Hub collects it centrally for hub-launched sessions; standalone
game entry points may collect equivalent values locally.

It contains:

-   Game
-   Difficulty
-   Session mode
-   Game-specific options
-   Custom settings

Games do not reopen the hub's configuration menus during their gameplay
lifecycle. Standalone entry points may run their own configuration menus
before constructing the session configuration.

### Game State

`GameState` provides explicit mutable state and committed move history.

Only real committed player/game moves are recorded. AI simulations,
minimax exploration, hints, and speculative state changes do not pollute
move history.

### Game Result

`GameResult` provides a standardized result containing:

-   Game
-   Outcome
-   Difficulty
-   Session mode
-   Score where applicable
-   Move count
-   Structured metadata
-   Configuration metadata under `metadata["configuration"]`

Results are the handoff point between individual games and the shared
systems.

### Statistics

Competitive completed sessions contribute to per-game statistics.

The statistics layer supports:

-   Games played
-   Wins, losses, and draws where applicable
-   Win/loss records
-   Streaks and best streaks
-   Game-specific scoring records
-   Hangman mistake records
-   Word Scramble attempt records
-   RPS variant/personality statistics
-   Snake top runs
-   Cross-game aggregate progression data

Practice sessions are excluded from competitive statistics.

### Achievements

Achievements are code-defined and evaluated from `GameResult` data.

Achievement state is persisted to the player's profile data and includes
unlock information such as unlock timestamps.

Achievement examples include:

-   First victory
-   Connect Four win streak milestones
-   Perfect Hangman
-   Lizard-Spock RPS victory
-   First-try Word Scramble
-   Snake high-score milestones
-   Cross-game completion achievements

Practice sessions cannot unlock competitive achievements.

### Profile & Progression

The profile system stores the player's identity and aggregate
progression.

Competitive completed sessions contribute aggregate XP, with an
additional XP contribution for competitive wins.

Progression is intentionally:

-   Aggregate
-   Cross-game
-   Cosmetic
-   Independent of gameplay balancing

Progression does not change AI behavior, game difficulty, scoring rules,
or competitive statistics.

### Settings

The Settings system persists user preferences such as:

-   Terminal banner style
-   Advisory difficulty suggestion preference

Difficulty suggestions are advisory only and do not override the
player's selected difficulty.

### Persistence

Shared JSON persistence provides safe local storage with atomic writes.

Runtime data is kept under:

``` text
.game_data/
```

This directory is intentionally ignored by Git.

### Player Summary Export

The hub can generate a readable Markdown player summary containing
profile, progression, statistics, and achievement information.

------------------------------------------------------------------------

## Custom Difficulty

Advanced / Custom configuration is available only for games that declare
meaningful custom parameters.

  Game           Custom setting     Valid range
  -------------- ---------------- -------------
  Tic-Tac-Toe    Minimax depth             1--9
  Connect Four   Minimax depth             1--6
  Hangman        Attempt count            3--10
  Snake          Not supported              ---

The hub collects the custom value and passes it through `SessionConfig`.

Each game validates its own custom parameter. Invalid values are
rejected rather than silently clamped.

Snake intentionally remains limited to its standard difficulty levels.

------------------------------------------------------------------------

## Difficulty Mapping

The shared difficulty concept is translated locally by each game.

### Tic-Tac-Toe

-   **Easy** --- random/basic computer behavior
-   **Medium** --- tactical computer behavior
-   **Hard** --- minimax
-   **Custom** --- configurable minimax depth

### Connect Four

-   **Easy** --- simpler/randomized computer behavior
-   **Medium** --- tactical behavior
-   **Hard** --- deeper minimax
-   **Custom** --- configurable minimax depth

### Hangman

-   **Easy** --- more attempts
-   **Medium** --- standard attempts
-   **Hard** --- fewer attempts
-   **Custom** --- configurable attempt count

### Rock Paper Scissors

-   **Easy** --- balanced personality
-   **Medium** --- adaptive personality
-   **Hard** --- unpredictable personality

### Word Scramble

Difficulty controls the target word-length range and associated
challenge.

### Snake

Difficulty controls game speed:

-   **Easy** --- slower
-   **Medium** --- standard
-   **Hard** --- faster

------------------------------------------------------------------------

## Game-Specific Features

### Board Games

Tic-Tac-Toe and Connect Four support:

-   Player vs Computer
-   Player vs Player
-   AI personalities where applicable
-   Hints
-   Replay
-   Rematch
-   Competitive/practice separation
-   AI simulation isolation from committed move history
-   Custom minimax depth

Replay uses the committed move history and does not mutate the recorded
game state.

### Rock Paper Scissors

Supports:

-   Standard RPS
-   Lizard-Spock
-   Single games
-   Fixed-length matches
-   Difficulty-driven computer personalities
-   Player history
-   Scoring
-   Rematch

### Hangman

Supports:

-   Categories
-   Remote word data with local fallback
-   Difficulty-based attempt counts
-   Custom attempt counts
-   Hint mechanics
-   ASCII hangman stages
-   Scoring
-   Streak tracking
-   Rematch

### Word Scramble

Supports:

-   Remote word selection with local fallback
-   Difficulty-based word lengths
-   Multiple attempts
-   Hint mechanics
-   Attempt-based scoring
-   Streak tracking
-   Rematch

### Snake

Supports:

-   Real-time keyboard input
-   WASD/arrow controls
-   Pause
-   Quit
-   Speed-based difficulty
-   Food and growth
-   Power-ups
-   Wrap-around
-   Collision handling
-   Full-board completion handling
-   Score tracking
-   Top-run statistics
-   Rematch

------------------------------------------------------------------------

## Practice Mode

Practice mode is deliberately separate from competitive progression.

Practice sessions:

-   Do not affect competitive statistics
-   Do not unlock competitive achievements
-   Do not contribute competitive progression

This allows players to experiment with games and configurations without
changing their competitive record.

------------------------------------------------------------------------

## Running

Python 3.10+ is recommended.

### Run the hub

``` bash
python main.py
```

### Run an individual game

``` bash
python games/tic_tac_toe.py
python games/connect_four.py
python games/hangman.py
python games/rock_paper_scissors.py
python games/word_scramble.py
python games/snake.py
```

### Run the test suite

``` bash
python -m pytest -q
```

The repository includes `pytest.ini` so the project root is configured
consistently for test execution.

------------------------------------------------------------------------

## Testing

The project has a centralized game test suite plus separate tests for
the shared engine and infrastructure.

Coverage includes:

-   Session configuration
-   Game state
-   Result contracts
-   Registry behavior
-   Persistence
-   Profiles
-   Statistics
-   Achievements
-   Settings
-   Hub flow
-   All six games
-   Difficulty behavior
-   Custom configuration bounds
-   Practice-mode isolation
-   Move-history integrity
-   Replay behavior
-   Game-specific scoring
-   Achievement evaluation
-   Progression
-   Result-to-system integration

------------------------------------------------------------------------

## Design Principles

-   Keep game rules inside their game modules.
-   Keep session configuration owned by the hub for hub-launched games;
    standalone entry points may provide equivalent local configuration.
-   Share only genuinely common session and infrastructure concerns.
-   Record real committed moves, not AI simulations or speculative
    states.
-   Keep game-specific features optional instead of forcing a uniform
    interface.
-   Keep the registry static and predictable.
-   Prefer straightforward Python over unnecessary abstraction.
-   Keep all six games independently runnable.
-   Keep competitive progression aggregate and cosmetic-only.
-   Keep Practice mode isolated from competitive records.
-   Validate configuration at the appropriate layer rather than silently
    correcting invalid values.
-   Prefer explicit contracts and tests over implicit behavior.

------------------------------------------------------------------------

## Scope

The project is a Python terminal game platform.

The focus is a maintainable, testable terminal game hub that
demonstrates clean Python architecture while preserving the individual
character of the original games.
