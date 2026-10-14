# Python Games Hub

A complete terminal-based Python game platform containing seven independently
runnable games, a shared session/configuration layer, standardized game state
and results, persistent player systems, competitive statistics, achievements,
progression, Quick Play, and configurable terminal presentation.

The project is designed as one coherent product: each game keeps its own rules
and personality while the platform provides the common systems that make the
collection consistent, testable, and persistent.

The implementation favors straightforward Python and standard-library
components at runtime. Shared infrastructure is centralized where it genuinely
belongs, while game-specific mechanics remain inside their own modules.

## Games

- **Tic-Tac-Toe** — Player vs Computer or Player vs Player, Easy/Medium/Hard,
  Advanced custom minimax depth, computer personalities, minimax AI, hints,
  replay, rematch, scoring, and win streaks.
- **Connect Four** — Player vs Computer or Player vs Player, Easy/Medium/Hard,
  Advanced custom minimax depth, gravity, win detection, minimax AI, hints,
  replay, rematch, scoring, and win streaks.
- **Hangman** — Category-based word selection, Easy/Medium/Hard, Advanced
  custom attempt count, hints, ASCII stages, scoring, rematch, and streak
  tracking.
- **Rock Paper Scissors** — Standard RPS or Lizard-Spock, single games or
  fixed-length matches, computer personalities, history-based play, scoring,
  rematch, and streak tracking.
- **Word Scramble** — API-backed word selection with local fallbacks, difficulty
  levels, hints, attempt-based scoring, rematch, and streak tracking.
- **Snake** — Real-time terminal gameplay with multiple speeds, keyboard
  controls, pause/quit, power-ups, wrap-around, score tracking, rematch, and
  top-run records.
- **Minesweeper** — Hidden-mine grid, first-click safety, safe-cell reveals,
  flood reveal, flagging, difficulty-based boards, scoring, and win/loss
  detection.

All seven games are connected to the hub and remain independently runnable.

------------------------------------------------------------------------

## Architecture

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

## Minesweeper

Minesweeper adds a hidden-state grid game to the platform while using the same
session, result, statistics, achievement, progression, and persistence
systems as the other games.

### Difficulty

| Difficulty | Board | Mines |
|---|---:|---:|
| Easy | 9 x 9 | 10 |
| Medium | 16 x 16 | 40 |
| Hard | 16 x 30 | 99 |

The first reveal is safe. Revealed numbers show how many mines are present in
the surrounding cells, and empty areas can be opened through flood reveal.

### Commands

```text
r ROW COL    Reveal a cell
f ROW COL    Flag / unflag a cell
h            Show help
q            Quit
```

The game displays row and column coordinates, explains its symbols and
commands in-game, and can be played without external instructions.

Minesweeper returns the same `GameResult` contract used by the other games and
participates in the normal platform flow:

```text
Minesweeper
    ↓
GameResult
    ↓
Statistics / Achievements / Progression
    ↓
Persistence
```

Its addition also validates that a genuinely different game can be registered
and integrated without creating a separate hub architecture.

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
python games/minesweeper.py
```

### Run the test suite

``` bash
python -m pytest -q
```

The repository includes `pytest.ini` so the project root is configured
consistently for test execution.

------------------------------------------------------------------------

## Testing

The current regression suite contains **119 passing tests** covering the games, shared engine, hub flow, persistence, and cross-system integration.

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
-   All seven games
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
-   Keep all seven games independently runnable.
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
character of the games.

------------------------------------------------------------------------

# Project History and Decision Record

This section records the reasoning behind the final architecture and the
turning points that shaped the product. It is intentionally preserved as
technical project history rather than treated as a task checklist.

## 1. Preserve Working Gameplay

**Decision:** Build around the existing games instead of rewriting all gameplay
from scratch.

**Reason:** The original games already contained useful AI, difficulty,
scoring, hints, real-time behavior, external data fallbacks, and regression
coverage. Rewriting working mechanics would add risk without adding product
value.

**Result:** The platform provides shared infrastructure while each game keeps
its own rules and personality.

```text
Existing gameplay
      ↓
Reusable boundaries
      ↓
Shared platform contracts
      ↓
Game-specific implementation
```

## 2. Share Infrastructure, Not Game Mechanics

**Decision:** Share platform concerns, not a universal representation of every
game.

**Reason:** Tic-Tac-Toe, Connect Four, Hangman, RPS, Word Scramble, Snake, and
Minesweeper have fundamentally different state and interaction models.

**Shared:** configuration, results, persistence, statistics, achievements,
profiles, settings, hub flow.

**Local:** rules, gameplay state, AI, scoring details, input interpretation,
real-time behavior, and game-specific mechanics.

**Result:** The project becomes a platform without becoming a generic game
engine.

## 3. `SessionConfig` Separates Configuration From Gameplay

**Decision:** Represent the configuration of a session explicitly.

**Reason:** Difficulty, mode, options, and custom settings describe what is
being started. They are not the mutable state of the running game.

```text
SessionConfig = what session is being started
GameState     = what is happening inside the session
GameResult    = what happened when the session ended
```

**Result:** Configuration can be validated before gameplay and state can change
without rewriting session configuration.

## 4. Difficulty Is Shared but Game-Specific

**Decision:** The hub uses Easy / Medium / Hard, while each game translates
those labels into its own mechanics.

**Reason:** A minimax depth, Snake speed, Hangman attempt count, and Minesweeper
mine density are different dimensions.

Examples:

```text
Tic-Tac-Toe → Easy: simpler AI, Hard: minimax
Hangman     → Easy: more attempts, Hard: fewer
Snake       → Easy: slower, Hard: faster
Minesweeper → Easy: smaller board, Hard: larger/harder board
```

**Result:** The player gets a consistent hub experience without pretending
that difficulty is identical across games.

## 5. Custom Difficulty Is Capability-Driven

**Decision:** Only games with meaningful bounded custom parameters expose
custom configuration.

**Reason:** A Custom option on every game would create artificial
configuration. TTT/Connect Four can meaningfully expose minimax depth and
Hangman can expose attempt count.

**Result:** Custom configuration remains useful rather than becoming a generic
settings form.

## 6. `GameResult` Is the Platform Handoff

**Decision:** Every completed session produces a standard `GameResult`.

**Reason:** Statistics, achievements, progression, and persistence need one
stable boundary even though the games behave differently.

```text
Game
 ↓
GameResult
 ↓
Statistics / Achievements / Progression
 ↓
Persistence
```

**Result:** The hub does not need separate post-game pipelines for every game.

## 7. `GameState` Is Explicit

**Decision:** Mutable gameplay state belongs to the game and is distinct from
configuration and result data.

**Reason:** Board state, guessed letters, Snake positions, Minesweeper cells,
and other game-specific values change during play.

**Result:** The hub manages lifecycle; the game manages gameplay state.

## 8. Only Real Moves Enter Move History

**Decision:** AI simulations, hints, minimax searches, and speculative
mutations never become committed move history.

**Reason:** A history containing moves that never happened is misleading and
breaks replay, move counts, debugging, and tests.

```text
Real committed move → record
AI simulation       → do not record
Hint simulation     → do not record
```

**Result:** Move history represents actual gameplay.

## 9. Static Registry Instead of a Plugin Framework

**Decision:** Use one explicit `GAME_REGISTRY`.

**Reason:** Seven games do not justify dynamic discovery or a plugin ecosystem.
Dynamic plugins would add indirection, configuration, failure modes, and
testing requirements without solving a current product problem.

**Result:** Adding a game remains explicit:

```text
Implement → Register → Declare capabilities → Test
```

## 10. Do Not Build a Generic Game Engine

**Decision:** Stop at a platform-level contract rather than creating a
universal engine loop.

**Reason:** Snake needs real-time input; RPS needs match semantics; Hangman
needs word state; Minesweeper needs hidden-grid state. A universal engine
would require excessive abstraction or exceptions.

**Result:** The project remains readable and appropriately scoped.

## 11. Practice Mode Is Isolated

**Decision:** Practice sessions do not affect competitive statistics,
achievements, or progression.

**Reason:** Players need to experiment without changing their competitive
record.

```text
Competitive → Statistics / Achievements / Progression
Practice    → Gameplay only
```

**Result:** Competitive records remain meaningful.

## 12. Progression Is Cosmetic

**Decision:** Progression is aggregate and does not change game balance.

**Reason:** XP or levels should not alter AI, difficulty, scoring, mechanics,
or competitive advantages.

**Result:** Progression connects the seven games without becoming a hidden
gameplay system.

## 13. Player Systems Have Clear Boundaries

**Decision:** Profile, Statistics, Achievements, Settings, and Progression are
separate systems.

**Reason:**

```text
Profile       → who the player is
Statistics    → what the player has done
Achievements → which milestones were unlocked
Settings      → how the platform should behave
Progression   → aggregate platform progress
```

**Result:** Each system can be tested and persisted without one giant
player-data module.

## 14. JSON Persistence Is Enough

**Decision:** Use local JSON instead of a database.

**Reason:** This is a local terminal platform, not a concurrent multi-user
service. JSON is readable, testable, dependency-light, and sufficient for
the persistence requirements.

**Result:** Durable local state without unnecessary infrastructure.

## 15. Runtime Data Is Not Source

**Decision:** Store player data under `.game_data/` and ignore it in Git.

**Reason:** Runtime state is generated locally and should not pollute source
history, tests, or portfolio releases.

**Result:** The repository represents the application, not one player's
runtime session.

## 16. Corrupt Persistence Should Be Recoverable

**Decision:** Preserve corrupt JSON where possible, warn, then fall back to
defaults.

**Reason:** Silently overwriting corrupt data destroys useful evidence.

```text
Corrupt JSON
    ↓
Preserve as .corrupt
    ↓
Warn
    ↓
Use defaults
```

If preservation itself fails, the system warns about that failure and still
recovers with defaults.

**Result:** Persistence fails defensively without becoming over-engineered.

## 17. Standalone Execution Remains Supported

**Decision:** Every game remains independently runnable.

**Reason:** Independent execution is useful for testing, demonstrations,
debugging, and portfolio review.

**Result:**

```text
Hub → canonical game
Standalone → same canonical game
```

There are no separate standalone gameplay implementations merely to support
independent execution.

## 18. Standalone Configuration Is Allowed

**Decision:** Standalone entry points may collect equivalent local
configuration.

**Reason:** Removing useful standalone menus solely for architectural purity
would add little value.

**Boundary:**

```text
Hub-launched game → hub collects configuration
Standalone game   → standalone adapter may collect configuration
Both              → canonical game implementation
```

**Result:** Documentation reflects the actual responsibility split rather than
forcing a large refactor.

## 19. Quick Play Is Not a Second Architecture

**Decision:** Quick Play uses the same registry and session configuration
path as normal Play.

**Reason:** Quick Play is a shortcut into the platform, not a separate game
launcher.

**Result:**

```text
Play       → Registry → SessionConfig → Game
Quick Play → Registry → SessionConfig → Game
```

## 20. RPS Uses Fixed-Length Matches

**Decision:** Describe the RPS match mode as **Fixed-Length Match**, not
Best-of-N.

**Reason:** The implementation uses a fixed number of rounds. "Best-of"
implies an early-ending win condition that is not what the implementation
does.

**Result:** Documentation, UI, and code use terminology that matches behavior.

## 21. Difficulty Is Not an Objective Universal Scale

**Decision:** Difficulty labels are platform vocabulary, not claims of equal
objective challenge across games.

**Reason:** RPS personality, Snake speed, minimax depth, and Minesweeper
density cannot be measured by one mechanical scale.

For RPS, Balanced → Easy, Adaptive → Medium, and Unpredictable → Hard is a
deliberate product mapping rather than an objective equivalence.

**Result:** The labels remain useful without overclaiming what they mean.

------------------------------------------------------------------------

# The Seventh Game: Why Minesweeper

## 22. Game Seven Was an Architectural Test

**Decision:** Add a seventh game after the platform architecture was stable.

**Reason:** The project's most important extension criterion was:

> Adding a seventh game should not require redesigning the hub's core
> architecture.

Without actually adding another game, that remained an untested claim.

**Result:** Game seven became an integration test for the architecture, not
just an increase in the game count.

## 23. Why Minesweeper

**Decision:** Choose Minesweeper instead of another game that mostly
recombined existing mechanics.

**Reason:** The existing collection already covered:

```text
Board / turns     → Tic-Tac-Toe, Connect Four
Word games        → Hangman, Word Scramble
Choice / matches  → Rock Paper Scissors
Real-time         → Snake
```

Minesweeper introduced a genuinely different model:

- Hidden information
- Mine generation
- Adjacent-cell counting
- Flood reveal
- Flagging
- Safe-cell logic
- Coordinate interaction
- Win based on revealing safe cells

**Result:** Minesweeper provided a stronger architectural test than another
similar board, word, or choice game.

## 24. Minesweeper Had to Use Existing Contracts

**Decision:** Do not create a Minesweeper-specific integration architecture.

**Required path:**

```text
Game Registry
      ↓
SessionConfig
      ↓
MinesweeperGame
      ↓
GameState
      ↓
GameResult
      ↓
Statistics / Achievements / Progression
      ↓
Persistence
```

**Reason:** A special-case integration would defeat the purpose of adding the
seventh game.

**Result:** Minesweeper became evidence that the platform boundary is real.

## 25. First-Click Safety

**Decision:** The first Minesweeper reveal cannot be a mine.

**Reason:** An unavoidable first-click loss is poor onboarding and does not
help demonstrate the game's reasoning mechanics.

**Result:** Mine generation is coordinated with the first reveal.

## 26. Minesweeper Explains Itself

**Decision:** The game includes visible instructions and an in-game help
command.

**Reason:** Coordinate-driven terminal controls are not self-explanatory.
The player should not need external help to discover the interaction model.

The interface explains:

```text
r ROW COL → reveal
f ROW COL → flag / unflag
h         → help
q         → quit
```

It also explains coordinates, symbols, objectives, and number meanings.

**Result:** The game remains simple while being discoverable.

## 27. Why Minesweeper Uses Coordinate Commands

**Decision:** Use terminal commands such as `r 5 7` instead of introducing a
full-screen terminal UI framework.

**Reason:** The project intentionally favors standard-library terminal
interaction. Coordinates are easy to parse, test, document, and run across
terminals.

**Result:** Minesweeper adds a new interaction model without adding a new UI
framework.

------------------------------------------------------------------------

# Reliability Turning Points

## 28. Persistent Streaks Became the Source of Truth

**Problem:** Fresh game objects could report a streak of one even when saved
statistics already contained a longer streak.

**Decision:** Persistent competitive streaks belong to the Statistics system,
not to the lifetime of a game object.

```text
Saved streak = 4
       ↓
Win
       ↓
Saved streak = 5
```

**Result:** Streaks survive separate game launches correctly.

## 29. Achievement Context Had to Use Saved Statistics

**Problem:** Fixing persisted streaks exposed a second bug. The ten-win
achievement was still reading the fresh game's metadata instead of the saved
streak.

**Decision:** Achievements that depend on persistent context receive that
context from updated platform state.

```text
GameResult        → this session
Saved statistics  → cross-session context
```

**Result:** Statistics and achievements now agree about persistent streaks.

## 30. Draw and Quit Semantics Were Made Deliberate

**Decision:** Competitive losses break streaks; completed non-win outcomes are
handled consistently by persisted statistics; quitting is not silently
converted into a synthetic loss.

**Reason:** A draw, loss, and quit are different events. Treating them as
identical would distort the meaning of competitive records.

**Result:** Result semantics remain explicit instead of being inferred from
game-object counters.

------------------------------------------------------------------------

# Testing Decisions

## 31. Test Architecture Changes, Not Just Functions

**Decision:** Significant platform changes receive both focused tests and
integration tests.

**Reason:** A function can pass while the chain around it is broken.

```text
Configure → Play → GameResult → Statistics
                         ↓
                 Achievements
                         ↓
                    Persistence
```

**Result:** The suite validates both local behavior and system boundaries.

## 32. Game Seven Required a Hub Integration Test

**Decision:** Minesweeper was not considered complete when its own tests
passed.

**Reason:** Its purpose was to validate the platform extension model.

The meaningful verification was:

```text
Hub
 ↓
Select Minesweeper
 ↓
SessionConfig
 ↓
Minesweeper
 ↓
GameResult
 ↓
Platform systems
```

**Result:** Game seven was verified through the same path as the existing
games.

## 33. Full Regression Is the Final Safety Net

**Decision:** Run the complete suite after major integration work.

**Reason:** Shared contracts mean changes to results, configuration,
persistence, or registry behavior can affect unrelated games.

**Final baseline:** **119 passing tests.**

The exact count is less important than maintaining a green full-suite result
after the final integration and cleanup work.

------------------------------------------------------------------------

# Scope Decisions

## 34. No GUI

**Decision:** Remain terminal-based.

**Reason:** The terminal is part of the project's identity and keeps the
engineering focus on Python, game logic, state, persistence, and testing.

## 35. No Online Multiplayer

**Decision:** Keep multiplayer local where supported.

**Reason:** Online multiplayer would introduce networking, synchronization,
identity, backend infrastructure, and failure handling that belong to a
different project.

## 36. No Database

**Decision:** Keep local JSON persistence.

**Reason:** There is no multi-user or server-side storage requirement.

## 37. No Plugin Ecosystem

**Decision:** Keep the registry explicit.

**Reason:** Seven games do not justify a dynamic plugin system. Predictability
is more valuable than hypothetical third-party extensibility.

## 38. No Universal Game Engine

**Decision:** Keep the game contract small.

**Reason:** Forcing real-time Snake, RPS matches, word games, board games, and
Minesweeper through one universal engine would create abstraction rather than
reduce it.

## 39. No Game Eight

**Decision:** Stop at seven games.

**Reason:** Once Minesweeper demonstrated that a genuinely different game
could enter the platform without redesigning the core, another game would
primarily increase scope rather than provide new architectural evidence.

**Result:** Seven games are the deliberate final product scope.

------------------------------------------------------------------------

# Documentation and Release Decisions

## 40. Why the Full README Became Separate Documentation

**Decision:** Preserve the detailed README as `PROJECT DOCUMENTATION.md` and
create a concise product README.

**Reason:** The project needs two different documentation experiences.

```text
README.md
    → quick product overview

PROJECT DOCUMENTATION.md
    → complete technical reference
```

The detailed document covers architecture, systems, decisions, testing,
difficulty mapping, persistence, and scope without forcing every repository
visitor to read the full engineering history.

**Result:** The landing page is concise while the technical record is
preserved.

## 41. Why Internal Planning Is Not Product Documentation

**Decision:** Keep `gameplan.md` internal and ignored.

**Reason:** Planning material contains intermediate decisions and historical
checklists. It is not the authoritative description of the finished product.

**Result:** The public documentation describes the final system rather than
its unfinished development checklist.

## 42. Why Development Artifacts Stay Out of Release Archives

**Decision:** Exclude Git metadata, runtime state, caches, compiled Python
files, generated summaries, and internal planning files from portfolio
archives.

**Reason:** A release archive should represent intentional source files, not
the developer's working directory.

Excluded examples:

```text
.git/
.game_data/
.pytest_cache/
__pycache__/
*.pyc
*.pyo
player_summary.md
gameplan.md
```

## 43. Why Release ZIPs Are Ignored by Git

**Decision:** Ignore `*.zip`.

**Reason:** Release archives are generated artifacts, not source. Keeping them
out of Git prevents the repository from accumulating successive copies of
release packages.

------------------------------------------------------------------------

# Completion Philosophy

## 44. Feature Complete Is Not Release Complete

The project was not considered complete merely because all seven games could
launch.

The completion path was:

```text
Gameplay
   ↓
Architecture
   ↓
Integration
   ↓
Persistence
   ↓
Statistics / Achievements / Progression
   ↓
Regression testing
   ↓
Documentation
   ↓
Repository hygiene
   ↓
Release packaging
```

Each layer protects a different part of the product.

## 45. Why Feature Development Was Frozen

**Decision:** Stop feature development after Minesweeper integration and full
regression.

**Reason:** Once the architectural extension test passed, further features
had diminishing value and increasing regression risk.

The remaining work became release quality rather than new functionality.

## 46. Final Architectural Principle

The final project can be summarized by one rule:

> **Share what is genuinely shared, keep what is genuinely different local,
> and make the boundary between the two explicit.**

That principle explains the final structure:

```text
                PYTHON GAMES HUB
                       │
              Shared platform layer
                       │
       ┌───────────────┼────────────────┐
       ↓               ↓                ↓
  Configuration    Results          Persistence
       │               │                │
       └───────────────┼────────────────┘
                       ↓
                 Seven games
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
       Board         Words       Real-time
          │            │            │
          └────────────┼────────────┘
                       ↓
                  Minesweeper
              hidden-state grid test
```

The platform is unified where unification improves consistency, testing,
persistence, and extension. The games remain distinct where their mechanics
actually differ.

That is the intended final product: **seven different terminal games operating
as one coherent Python game platform.**
