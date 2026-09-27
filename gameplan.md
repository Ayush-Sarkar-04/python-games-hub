# Python Games Hub V2 — Game Plan

## 1. Project Direction

Python Games Hub V2 is an evolution of V1, not a complete rewrite.

V1 already contains six working, tested games with substantial gameplay logic. V2 will preserve the usable and proven parts of those games while rebuilding the architecture underneath them so that shared systems are handled centrally.

### V1 → V2

```text
V1
│
├── Six working games
├── AI systems
├── Difficulty systems
├── Game modes
├── Hints
├── Streaks
├── Snake mechanics
├── API + fallback logic
└── Persistent scoreboard
        │
        ▼
V2
│
├── Shared game architecture
├── Hub-level session configuration
├── Common GameResult contract
├── Explicit game state
├── Shared persistence
├── Profiles
├── Statistics
├── Achievements
├── Scoring
├── Replay / move history
└── Extensible game registry
```

The goal is not to make the project into a generic game engine. The goal is to make the existing games easier to manage, extend, test, and unify.

---

## 2. Core V2 Principle

> Preserve working V1 gameplay. Refactor the architecture around it.

For every existing game:

1. Start from the current V1 implementation.
2. Identify the gameplay logic that already works.
3. Extract only the state or shared behavior that V2 actually needs.
4. Adapt the game to the V2 contracts.
5. Preserve existing gameplay behavior unless the V2 design explicitly changes it.
6. Re-run the relevant V1 regression tests.
7. Add V2-specific tests.

Do not rewrite working game logic simply for stylistic reasons.

---

## 3. Fundamental Architectural Change

### Difficulty moves from game level to hub/session level.

### V1

```text
Launch Game
    ↓
Choose Mode
    ↓
Choose Difficulty
    ↓
Play
```

Each game independently owns its difficulty menu.

### V2

```text
Hub
 ↓
Play / Quick Play
 ↓
Choose Game
 ↓
Configure Session
 ↓
Difficulty / Advanced options
 ↓
Game receives SessionConfig
 ↓
Play
```

The hub owns the concept of difficulty.

Each game owns what that difficulty means.

| Game | Easy | Medium | Hard |
|---|---|---|---|
| Tic-Tac-Toe | Random AI | Tactical AI | Minimax |
| Connect Four | Random AI | Tactical AI | Minimax |
| Hangman | 7 attempts | 6 attempts | 5 attempts |
| Word Scramble | 4–6 letters | 6–8 letters | 8–10 letters |
| RPS | Balanced | Adaptive | Unpredictable |
| Snake | Slow | Medium | Fast |

The game should consume the selected difficulty rather than ask the player to choose it internally.

**Important translation rule:** Easy/Medium/Hard is a hub-level abstraction, not a claim that every game has the same kind of difficulty. Each game translates the shared difficulty into its own mechanics. For RPS, the deliberate mapping is Balanced → Easy, Adaptive → Medium, and Unpredictable → Hard. **Unpredictable is a design-chosen Hard mapping, not an objective equivalence between personality and difficulty.** The implementation translation function should retain a code comment stating this explicitly so the mapping is not later "corrected" into a false equivalence.

---

## 4. Session Configuration

Difficulty should not be stored as generic game state.

```text
SessionConfig
    │
    ├── profile
    ├── difficulty
    ├── mode
    ├── AI personality where applicable
    ├── game variant/options where applicable
    ├── preferences
    ├── hint settings
    └── other session-level options

GameState
    │
    ├── board
    ├── current player
    ├── moves
    ├── guessed letters
    ├── snake position
    └── other game-specific state
```

Conceptually:

```python
SessionConfig(
    profile="Player",
    difficulty="hard",
    hints=True,
)
```

The game receives the session configuration. It does not own the configuration menu.

**Configuration ownership rule:** all session choices that affect how a game is played are selected by the hub and passed through `SessionConfig`. This includes game mode, AI personality, and variant toggles such as RPS Lizard/Spock. Settings may provide defaults for these choices, but the active session configuration is authoritative. Individual games must not re-open their own configuration menus during play.

---

## 5. V2 Target Architecture

```text
python-games-hub-v2/
│
├── main.py
│
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
│
├── games/
│   ├── tic_tac_toe.py
│   ├── connect_four.py
│   ├── rock_paper_scissors.py
│   ├── hangman.py
│   ├── word_scramble.py
│   └── snake.py
│
├── tests/
│   ├── test_game.py
│   ├── test_result.py
│   ├── test_state.py
│   ├── test_utils.py
│   ├── test_persistence.py
│   ├── test_systems.py
│   ├── test_registry.py
│   └── test_flow.py
│
├── README.md
└── gameplan.md
```

The exact directory structure can be adjusted during implementation if the existing code makes a simpler structure more appropriate.

Do not create modules merely to satisfy the diagram.

---

## 6. Core Systems

### 6.1 Game Contract

Create a common game interface/contract.

Conceptually:

```python
class Game:
    name
    description

    def setup()
    def play()
    def result()
```

The implementation should remain lightweight.

The objective is for the hub to know:

> This is a game. I can start it, give it the session configuration, receive its result, and return to the hub.

Avoid building a large abstract framework.

**Contract freeze rule:** the contract is provisional while Tic-Tac-Toe and Connect Four are migrated. Once both implement it cleanly, freeze the core contract. Games 3–6 must not add new lifecycle methods or expand the abstraction merely to make their internal differences fit. If a later game genuinely requires a contract change, revisit the abstraction deliberately rather than adding another exception.

### 6.2 Game State

Games that benefit from explicit state should have it separated clearly from presentation and hub logic.

Examples:

**Tic-Tac-Toe**
```text
board
current_player
moves
mode
difficulty
```

**Connect Four**
```text
board
current_player
moves
turn_number
mode
difficulty
```

**Hangman**
```text
word
guessed_letters
attempts
hint_used
category
```

**Snake**
```text
snake
food
powerups
direction
score
difficulty
wrap_enabled
```

Game state should represent the current game, not the global player/session.

### 6.3 Common GameResult

Replace game-specific result communication with a common result contract.

Conceptually:

```python
GameResult(
    game="connect_four",
    outcome="win",
    score=120,
    difficulty="hard",
    mode="computer",
    moves=27,
    metadata={
        "configuration": {
            "custom_settings": {},
            "personality": None,
            "variant": None,
        }
    }
)
```

`metadata` is optional structured game-specific result context, not a general dumping ground. When configuration matters to statistics or achievements, it should be recorded under `metadata["configuration"]`. Reserved configuration fields include `custom_settings`, `personality`, and `variant`; games may omit fields that do not apply. For a custom session, `difficulty` is `"custom"` and the actual validated parameters are echoed in `metadata["configuration"]["custom_settings"]`. This preserves both the named difficulty category and the exact parameters used.

A completed RPS match produces one `GameResult` for the match. Individual rounds are not separate `GameResult` objects; round-level detail belongs to the match's local history and may be summarized in result metadata when useful.

Possible outcome values:

```text
win
loss
draw
quit
game_over
```

Only use values that make sense for the individual game.

Fields that do not apply to a game are optional/`None`; for example, Snake does not need a win/loss outcome or turn count. The important point is that the hub receives a consistent result object rather than special-casing individual games.

### 6.4 Shared Utilities

Create a small shared utility module for genuinely common behavior:

- `play_again()`
- generic menu selection
- banners/dividers
- common input validation where appropriate

Do not move game-specific logic into the utility module.

The utility module should remain small.

---

## 7. Persistence Architecture

V1 currently uses persistent scoreboard data.

V2 should create a proper persistence boundary rather than having `main.py` directly understand every JSON file.

Potential persisted systems:

```text
profiles
statistics
achievements
settings
records
```

Atomic-write behavior from V1 should be preserved.

The persistence layer should safely handle:

- missing files
- malformed files
- missing fields
- valid existing data
- atomic replacement when saving

---

## 8. Profiles

V2 can introduce player profiles.

Conceptually:

```text
Player
│
├── statistics
├── achievements
├── personal records
└── preferences
```

The profile should become the owner of progression data.

This replaces the V1 assumption of a single global player.

---

## 9. Statistics

Move beyond simple win/loss counters where useful.

### Tic-Tac-Toe
- games played
- wins
- losses
- draws
- streaks
- best streak

### Connect Four
- games played
- wins
- losses
- draws
- streaks
- turns/moves

### RPS
- matches
- wins
- losses
- draws
- streaks
- results by AI personality
- Lizard/Spock usage where applicable

### Hangman
- games
- wins
- losses
- fewest mistakes
- streaks

### Word Scramble
- rounds
- wins
- losses
- fewest attempts on a successful round
- streaks

### Snake
- games
- best score
- total score
- top runs

Statistics should be data-driven where practical rather than hardcoded into the hub. Aggregate competitive statistics combine applicable results across difficulty levels unless a statistic is explicitly difficulty-specific. Custom sessions remain identifiable as `difficulty="custom"` with their validated parameters available through `GameResult.metadata["configuration"]["custom_settings"]`.

---

## 10. Achievements

Introduce an achievement system after the common result/persistence architecture exists.

Potential initial achievements:

- Perfect Hangman — win with zero mistakes
- 10-win Connect Four streak
Difficulty does not reset or partition this streak; Easy, Medium, Hard, and valid Custom competitive wins may contribute to the same streak. Any competitive loss breaks the streak.
- Snake score over 200
- Win an RPS match with Lizard/Spock enabled
- First victory
- Play all six games in competitive sessions

Achievements should consume game results/events rather than being hardcoded into individual games.

Each achievement is persisted as profile-owned data with a stable `id`, display `name`, `description`, unlock status, and `unlocked_at` timestamp. Achievement definitions remain code/configuration; only the player's unlocked state is persisted.

Achievement and statistics logic must not assume every game populates `outcome` with a win/loss/draw-shaped value. Always check which fields a given `GameResult` actually uses before branching on them. Snake, for example, uses `quit`/`game_over` plus score-oriented fields rather than a win/loss/draw outcome.

Persistence should use the same safe atomic-write approach as the scoreboard.

---

## 11. Scoring

V2 should support difficulty-aware scoring.

### Word Scramble

Use the existing:

```python
SCORE_BY_ATTEMPT = {
    1: 3,
    2: 2,
    3: 1,
}
```

instead of leaving the constant unused.

### Hangman
Reward fewer mistakes.

### Tic-Tac-Toe
Difficulty-based scoring.

### Connect Four
Difficulty-based scoring.

### RPS
Score based on match/mode and result.

### Snake
Preserve the existing gameplay score.

Scoring formulas should remain simple and explainable.

Do not create complicated XP formulas unless there is a clear benefit.

---

## 12. Tic-Tac-Toe V2 Migration

Tic-Tac-Toe is the first migration target because it is simple enough to establish the architecture.

Preserve:

- PvC
- PvP
- Easy/Medium/Hard AI
- Minimax
- AI personalities
- hub-selected game mode and AI personality through `SessionConfig`
- existing board display
- win/draw detection
- streak behavior where applicable

Add through V2 architecture:

- explicit game state
- common GameResult
- move history
- practice mode
- limited AI hint
- replay support

The existing V1 minimax logic should be reused rather than rewritten unnecessarily.

---

## 13. Connect Four V2 Migration

Connect Four is the architecture stress test after Tic-Tac-Toe.

Preserve:

- 7×6 board
- gravity
- PvC/PvP
- Easy/Medium/Hard
- minimax
- immediate win/block behavior
- horizontal/vertical/diagonal detection

Add:

- explicit game state
- common GameResult
- move history
- practice mode
- AI hint
- replay support

If the architecture works cleanly for both Tic-Tac-Toe and Connect Four, continue migrating the remaining games.

---

## 14. RPS V2 Migration

Preserve:

- Standard RPS
- Lizard/Spock
- Single Game
- Best-of
- AI personalities
- adaptive behavior
- hub-selected mode, personality, and Lizard/Spock variant through `SessionConfig`
- streaks

Adapt:

- difficulty from SessionConfig
- common GameResult
- scoring
- statistics
- achievements

RPS should demonstrate that the V2 architecture supports non-board games.

---

## 15. Hangman V2 Migration

Preserve:

- remote category source
- fallback categories
- difficulty behavior
- Hangman stages
- hints
- streaks
- input validation

Adapt:

- difficulty from SessionConfig
- explicit state
- common GameResult
- scoring
- achievements
- statistics

---

## 16. Word Scramble V2 Migration

Preserve:

- Random Word API
- fallback words
- difficulty
- scrambling logic
- attempts
- hints
- streaks
- result screens

Adapt:

- difficulty from SessionConfig
- common GameResult
- scoring
- statistics
- achievements

Wire the existing attempt-based scoring rather than replacing it with a new scoring design.

---

## 17. Snake V2 Migration

Snake comes last because it differs fundamentally from turn-based games.

Preserve:

- real-time movement
- WASD/arrows
- food
- growth
- collision
- difficulty
- pause
- quit
- power-ups
- wrap-around
- scoring
- cross-platform input
- terminal restoration

Adapt:

- common SessionConfig
- common GameResult
- statistics
- top runs
- achievements
- persistence

Snake should not be forced into a turn-based abstraction simply for architectural symmetry.

Snake testing should focus on deterministic state transitions and pure game logic rather than attempting to fully mock the real-time terminal loop.

---

## 18. Shared Gameplay Features

### Practice/Sandbox Mode

Initially for:

- Tic-Tac-Toe
- Connect Four

Player controls both sides.

Practice sessions are non-competitive. They may return a `GameResult` for the current session UI, but they are excluded from competitive statistics, streaks, achievements, scoreboard records, and meta-progression. A practice session is identified by `mode="practice"`.

### Move History

For board games:

```text
1. X → 4
2. O → 2
3. X → 6
...
```

The move list should be stored as part of game state/history.

### AI Hint

For TTT and Connect Four:

- limited use
- once per match
- optionally consumes a score/point
- reuse existing AI logic
- surface the AI's recommended move

Do not duplicate minimax logic.

### Replay

For board games:

```text
Game Complete
    ↓
Replay
    ↓
Replay moves sequentially
```

Replay should consume recorded move history.

**Move-history rule:** only committed real moves are recorded. AI simulations, minimax search, hints, previews, and other speculative board mutations must never append to move history.

Do not force every game to expose identical optional capabilities. TTT and Connect Four can support replay, move history, AI hints, and practice; RPS may support history/replay in a form appropriate to rounds; Hangman can support hints without board replay; Snake uses run history rather than turn replay.

---

## 19. Hub-Level Features

The hub should own:

- profile selection
- session configuration
- difficulty
- preferences
- game registry
- game selection
- Quick Play
- statistics
- achievements
- settings

The hub flow is game-first: the player selects a game, then configures the session for that game. The earlier conceptual flow is therefore implemented as:

```text
Hub
 ↓
Play / Quick Play
 ↓
Choose Game
 ↓
Configure Session
 ↓
Difficulty / Advanced options
 ↓
Play
```

Potential hub structure:

```text
PYTHON GAMES HUB

1. Play
2. Quick Play
3. Profile & Statistics
4. Settings
5. Exit
```

`Play` leads to game selection followed by session configuration. `Quick Play` may use saved/default configuration where appropriate. Profile & Statistics contains statistics, achievements, profile details, and Export Summary.

---



**Registry key convention:** `GAME_REGISTRY` uses stable game-name identifiers (for example, `"tic_tac_toe"` and `"connect_four"`), never menu-position numbers. Menu position is presentation logic only.
## 20. Game Registry

The hub should not require a growing chain of hardcoded imports/conditions for every game.

Conceptually:

```text
Game Registry
│
├── Tic-Tac-Toe
├── Hangman
├── RPS
├── Word Scramble
├── Connect Four
└── Snake
```

Each registered game should provide:

- name
- description
- entry point
- supported modes
- supported capabilities where useful

Capabilities should be declared directly on the registry entry, for example:

```python
"tic_tac_toe": {
    "entry_point": play_tic_tac_toe,
    "capabilities": {"replay", "history", "hint", "practice"},
}
```

The hub should use these capability declarations to conditionally expose features such as Practice Mode or Replay. Do not hardcode checks such as `if game_name in (...)` throughout the hub UI.

Adding a seventh game should require registering the game rather than modifying the core hub architecture.

The registry is intentionally a static dictionary/configuration, not dynamic discovery, filesystem scanning, or plugin loading. Do not overbuild this into a plugin framework.

---

## 21. Settings

V2 can introduce a small settings system.

Potential settings:

```text
default difficulty
RPS Lizard/Spock preference
preferred AI personality
hints enabled
display preferences
```

Settings are session/user preferences, not game state.

Persist them safely.

---

## 22. Testing Strategy

V1 tests are valuable and should become the regression foundation.

For each migrated game:

```text
Existing V1 behavior
        ↓
Regression tests
        ↓
V2 migration
        ↓
V2 tests
```

Test categories:

### Core
- Game contract
- GameResult
- SessionConfig
- custom difficulty validation
- configuration ownership/translation
- shared utilities

### Persistence
- missing files
- corrupt files
- valid files
- atomic saves
- profile loading/saving

### Games
- gameplay rules
- AI
- difficulty
- results
- scoring
- state transitions

### Integration
- hub launches games
- game results return correctly
- statistics update
- practice sessions remain excluded from competitive records
- achievements trigger and persist correctly
- custom configuration is preserved in results
- profiles persist
- settings persist
- meta-progression handles Snake and non-win outcomes without synthetic wins
- profile/statistics export matches persisted data

### Final
- all Python files compile
- complete test suite passes
- every game can still run independently
- hub can launch every game

---

## 23. Migration Order

Do not migrate all six simultaneously.

```text
1. Core architecture
       ↓
2. Persistence foundation
       ↓
3. Tic-Tac-Toe
       ↓
4. Tests
       ↓
5. Connect Four
       ↓
6. Tests
       ↓
7. RPS
       ↓
8. Hangman
       ↓
9. Word Scramble
       ↓
10. Snake
       ↓
11. Shared progression
       ↓
12. Hub polish
       ↓
13. Full regression
       ↓
14. Documentation
       ↓
15. V2 release
```

Tic-Tac-Toe is the reference implementation.

Connect Four is the architecture stress test.

Snake is the final compatibility test because of its real-time nature.

---

## 24. V2 Definition of Done

- [ ] All six V1 games migrated.
- [ ] Existing gameplay behavior preserved where applicable.
- [ ] Difficulty controlled by the hub/session rather than individual game menus.
- [ ] Game mode, AI personality, and game variants are selected by the hub and passed through SessionConfig.
- [ ] SessionConfig exists.
- [ ] Game state is explicit where needed.
- [ ] GameResult is standardized.
- [ ] Shared utilities are centralized.
- [ ] Persistence has a clean boundary.
- [ ] Profiles work.
- [ ] Statistics work.
- [ ] Achievements work.
- [ ] Achievement definitions and profile-owned unlock state are persisted safely.
- [ ] Difficulty-aware scoring works.
- [ ] TTT has move history.
- [ ] Connect Four has move history.
- [ ] TTT/Connect Four support practice mode.
- [ ] TTT/Connect Four support limited AI hints.
- [ ] Board-game replay works.
- [ ] Snake retains real-time functionality.
- [ ] Snake records meaningful personal records/top runs.
- [ ] Hub game registration is centralized.
- [ ] Quick Play works.
- [ ] Settings work.
- [ ] Custom difficulty works with validated game-specific bounds.
- [ ] Difficulty auto-suggestion is advisory only.
- [ ] Cross-game meta-progression remains aggregate and cosmetic-only.
- [ ] Profile/statistics export works.
- [ ] Existing V1 regression coverage passes.
- [ ] New V2 tests pass.
- [ ] All games remain independently runnable.
- [ ] README documents the V2 architecture.
- [ ] Final repository audit passes.

---

## Advanced Hub Features

The following features are included in V2 as extensions of the existing architecture. They must remain lightweight and must not introduce a generic game-engine abstraction.

### Custom Difficulty Presets

`SessionConfig` supports a `custom` difficulty option in addition to Easy, Medium, and Hard.

```python
difficulty = "easy" | "medium" | "hard" | "custom"
```

Custom sessions may carry optional game-specific parameters, for example:

```python
custom_settings = {
    "minimax_depth": 6,
    "attempts": 8,
}
```

Each game validates and interprets only the parameters it understands; unknown custom keys are ignored by that game. Named Easy/Medium/Hard tiers remain the normal user-facing difficulty choices. Custom values must also pass game-specific sanity bounds. Invalid values are rejected and the hub prompts the player to enter a valid value again; they are not silently clamped or converted to a different difficulty. Each game's custom-parameter UI defines its allowed range.

Examples:
- Connect Four: custom minimax depth.
- Hangman: custom attempt count.
- Other games may expose custom parameters only where they have a meaningful, bounded interpretation.

Custom difficulty demonstrates that the difficulty abstraction is genuinely parameterized underneath the named tiers without turning the project into a generic configuration engine.

### Difficulty Auto-Suggestion

Once profiles and statistics exist, the hub may suggest a difficulty using existing statistics.

Example:

```text
Connect Four: Medium
Suggested: Hard — 8 wins in your last 10 Medium games.
```

The suggestion is advisory only. It must never automatically change the selected difficulty or override the player's choice.

This feature is read-only over existing statistics and requires no new persistence layer.

### Cross-Game Meta-Progression

V2 may include a lightweight player level/XP system derived from aggregate activity across all six games.

Scope rules:
- Keep the formula deliberately simple and define it once during implementation. Do not repeatedly expand or rebalance it during V2.
- Base progression on aggregate completed competitive sessions plus wins where a game has a meaningful win outcome.
- A completed Snake run contributes to activity/progression through the aggregate session count and score-based records, but is not treated as a synthetic "win."
- Draws, losses, quits, and game-over results do not create a synthetic win merely to fit the XP system.
- Do not introduce complicated XP formulas.
- Unlocks are cosmetic terminal flourishes only.
- Cosmetic unlocks may include alternate banner styles, terminal presentation styles, or similar non-gameplay changes.
- No gameplay advantages, stat boosts, or balancing modifiers are tied to progression.

The purpose is to provide a simple cross-game sense of progression without expanding V2 into a full progression system.

### Profile and Statistics Export

The hub provides an export/summary command that generates a readable text or Markdown file containing the current profile's persisted statistics, achievements, and relevant meta-progression information.

The export is a read-and-format operation over existing persisted data:

```text
Profile
 ├── Statistics
 ├── Achievements
 └── Meta Progression
          ↓
     Summary Export
          ↓
   player_summary.md
```

No new game architecture or persistence model is required for this feature.

The export should be suitable as a shareable portfolio artifact showing the player's activity, statistics, achievements, and progression.

### Hub UX Placement

**Profile/statistics export** is surfaced through the Profile & Statistics area rather than as a top-level game-style hub option.

```text
PROFILE & STATISTICS

1. View Profile
2. View Statistics
3. View Achievements
4. Export Summary
5. Back
```

The main hub remains focused on launching games and core hub actions.

**Custom difficulty** is surfaced through an Advanced path rather than alongside the standard Easy/Medium/Hard choices.

```text
Select Difficulty

1. Easy
2. Medium
3. Hard
4. Advanced / Custom
```

`Advanced / Custom` is shown only when the selected game declares meaningful custom parameters. It opens the game-specific parameter prompts directly. Games without custom parameters do not show this option.

Examples:

```text
CONNECT FOUR — CUSTOM

Minimax depth: 6
```

```text
HANGMAN — CUSTOM

Number of attempts: 8
```

Easy/Medium/Hard remain the standard difficulty choices. Custom difficulty is intended for advanced users and portfolio/demo use.

These UX decisions do not change `GAME_REGISTRY`, the `Game` contract, or the core `GameResult` shape. Custom configuration is represented through the structured `metadata["configuration"]` fields defined in §6.3.

---

## 25. Scope Boundary

V2 is not intended to become:

- a GUI application
- a web application
- an online multiplayer platform
- a database-backed service
- a generic game engine
- a plugin ecosystem
- an AI research platform

The project remains a Python terminal game platform.

The architectural goal is:

> Make the six existing games reusable, testable, configurable, and unified without sacrificing the simplicity and personality of the individual games.

---

## 26. Final V1 → V2 Goal

### V1

> Six polished Python games connected by a hub.

### V2

> A reusable terminal game platform demonstrated through six existing games, with centralized session configuration, shared state/result handling, persistence, progression, and replay-oriented game systems.

### Primary architectural success criterion

> Adding a seventh game should not require redesigning the hub's core architecture.

That is the milestone that distinguishes V2 from simply adding more features to V1.


## V2 Five-Commit Implementation Plan

V2 is intentionally limited to **five meaningful commits**. Each commit represents a coherent implementation phase and must include its related tests before the commit is made. The five commits are implementation groupings; they do not permit duplicated implementation of the same feature across milestones.

### Commit 1 — V2 Foundation & Core Architecture

Build the architectural foundation without migrating all gameplay at once.

Scope:
- Create the `engine/` architecture:
  - `game.py`
  - `state.py`
  - `result.py`
  - `utils.py`
  - `persistence.py`
  - `profiles.py`
  - `statistics.py`
  - `achievements.py`
  - `settings.py`
- Establish `SessionConfig`.
- Establish the common `GameResult` contract and metadata rules.
- Establish the static `GAME_REGISTRY` using stable game-name keys.
- Establish capability declarations in the registry.
- Establish persistence boundaries and atomic writes.
- Create profiles, statistics, achievements, and settings foundations.
- Establish the new hub flow:
  `Hub → Play/Quick Play → Choose Game → Configure Session → Difficulty/Advanced → Play`.
- Establish the competitive/practice distinction.
- Establish shared configuration ownership: the hub/session owns configuration; games consume configuration rather than presenting configuration menus.
- Establish the mechanism by which achievement definitions and evaluation consume `GameResult` data, without wiring individual game triggers yet.
- Do not implement game-specific Custom Difficulty here.

Tests required before commit:
- Core state/result tests.
- SessionConfig tests.
- Persistence tests, including atomic-write behavior.
- Registry/capability tests.
- Profile/statistics/achievement/settings persistence tests.
- Hub configuration-flow tests.
- Achievement evaluator/schema tests using controlled synthetic `GameResult` fixtures only; real-game achievement integration begins with the corresponding game migration.

### Commit 2 — Board Games Migration

Migrate Tic-Tac-Toe and Connect Four first because they establish the strongest test of the V2 abstractions.

Scope:
- Move both games into `games/`.
- Preserve existing working gameplay, AI behavior, modes, difficulty behavior, and terminal presentation.
- Move configuration ownership to `SessionConfig`.
- Move AI personality configuration into session configuration where applicable.
- Implement explicit game state.
- Implement `GameResult`.
- Implement committed-move history.
- Ensure AI simulations, minimax searches, hints, and speculative board mutations never pollute move history.
- Add practice/sandbox mode.
- Add AI hint support.
- Add replay/move-history support.
- Implement **game-side Custom Difficulty for TTT/Connect Four** through `SessionConfig`, even though the hub's Advanced menu is not surfaced until Commit 4.
- For Commit 2, custom settings are supplied directly through `SessionConfig` in tests/internal integration; no temporary duplicate hub UI is created.
- Validate and bound custom parameter values at the game/configuration boundary.
- Add result metadata for relevant custom settings/personality.
- Wire the applicable TTT/Connect Four achievement triggers into the achievement system.
- Validate that the provisional `Game` contract is cleanly implemented by both games.
- **Freeze the `Game` contract after this commit.** Later games must conform to it rather than expanding it without an explicit architectural review.

Tests required before commit:
- Full TTT regression suite.
- Full Connect Four regression suite.
- State-transition tests.
- Move-history/replay tests.
- Practice-mode isolation tests.
- AI simulation/history integrity tests.
- Custom-difficulty parameter and bounds tests using direct `SessionConfig`.
- GameResult metadata tests.
- **Achievement integration smoke tests:** a real competitive TTT/Connect Four result must reach the achievement evaluator correctly.
- Cross-game contract tests.

### Commit 3 — Non-Real-Time Games Migration

Migrate Rock Paper Scissors, Hangman, and Word Scramble.

Scope:
- Move all three games into `games/`.
- Preserve working V1 gameplay and terminal UX.
- Adapt difficulty from `SessionConfig`.
- Move RPS personality and Lizard/Spock configuration into session configuration.
- Preserve RPS Single Game and Best-of behavior.
- Preserve Hangman API/fallback, categories, hints, attempts, and streak behavior.
- Preserve Word Scramble API/fallback, difficulty, hints, streaks, and result screens.
- Wire Word Scramble's attempt-based scoring.
- Implement `GameResult` consistently.
- Use result metadata for RPS personality/variant and other game-specific information where required.
- Apply the established capability model rather than forcing board-game capabilities onto these games.
- Use `fewest_mistakes` for Hangman statistics.
- Define Word Scramble attempt statistics explicitly when implementing statistics.
- Keep competitive statistics and achievements separate from Practice Mode.
- Implement **Hangman's game-side Custom Difficulty** through `SessionConfig`, using custom attempt count as the supported parameter.
- Validate and bound Hangman's custom attempt count at the game/configuration boundary.
- Supply Hangman custom settings directly through `SessionConfig` in Commit 3 tests; the shared Advanced hub UI remains a Commit 4 concern.
- Wire the applicable RPS, Hangman, and Word Scramble achievement triggers into the achievement system.

Custom Difficulty boundary for Commit 3:
- RPS, Word Scramble, and other games without a meaningful custom parameter remain standard-tier-only unless the registry explicitly declares a custom capability.
- No game is required to expose a Custom Difficulty option merely because the global `SessionConfig` supports `"custom"`.

Tests required before commit:
- RPS regression and match-result tests.
- Hangman API/fallback/difficulty/hint tests.
- Word Scramble API/fallback/difficulty/hint/scoring tests.
- SessionConfig translation tests.
- RPS personality/variant metadata tests.
- Hangman custom-attempt validation/bounds tests.
- Competitive vs Practice isolation tests.
- Statistics naming and aggregation tests.
- **Achievement integration tests** for applicable RPS/Hangman/Word Scramble triggers using real game results.

### Commit 4 — Snake, Progression & Advanced Hub Integration

Complete Snake and then expose the cross-game systems that depend on the migrated games.

Scope:
- Move Snake into `games/`.
- Preserve real-time controls and gameplay:
  - difficulty/speed
  - keyboard controls
  - food/growth
  - collision
  - pause/quit
  - power-ups
  - optional wrap-around
- Implement explicit Snake state.
- Implement Snake `GameResult` using its natural `quit` / `game_over` vocabulary.
- Preserve real-time terminal restoration behavior.
- Add Snake statistics and top-run tracking.
- Keep Snake state-focused tests rather than elaborate real-time loop mocks.
- **Snake does not support Custom Difficulty in V2.** Its standard Slow/Medium/Fast speed tiers remain the supported difficulty choices. The Advanced/Custom UI must therefore not appear for Snake.
- Implement cross-game meta-progression using the deliberately simple aggregate formula selected during implementation.
- Ensure meta-progression handles Snake and other non-win outcomes without synthetic wins.
- Implement difficulty auto-suggestion as advisory only.
- Implement the shared **Advanced Difficulty hub UI** for games whose registry capabilities declare Custom Difficulty support.
- The Advanced UI consumes the already-implemented game-side custom parameter definitions/validation from Commits 2 and 3; it does not duplicate game-specific bounds or validation logic.
- For a game with no meaningful custom parameters, Advanced/Custom is not shown.
- Implement Profile & Statistics export.
- Complete achievement triggers/persistence for any remaining game-specific cases, including Snake where applicable.
- Implement any remaining capability-specific hub presentation.

The Advanced Difficulty split is deliberate:
- **Commits 2–3:** game-side custom parameter support, validation, bounds, and `GameResult` metadata.
- **Commit 4:** shared hub presentation and routing of those existing capabilities.
- No custom-difficulty validation or bounds logic is reimplemented in Commit 4.

Tests required before commit:
- Snake state-transition tests.
- Snake persistence/statistics tests.
- Meta-progression tests, including Snake/non-win outcomes.
- Achievement trigger/persistence integration tests for remaining applicable cases.
- Difficulty auto-suggestion tests.
- Advanced hub routing tests showing Custom only for capable games.
- End-to-end custom-difficulty tests from Advanced hub → SessionConfig → game → GameResult for TTT, Connect Four, and Hangman.
- Export-format tests.
- Advanced hub UX tests.

### Commit 5 — Full Integration, Hardening & V2 Release

Bring the complete system together and do not introduce new architectural features.

Scope:
- Complete the final hub integration across all six games.
- Complete Quick Play.
- Complete Profile & Statistics navigation.
- Complete Settings integration.
- Complete capability-aware menus.
- Complete scoreboard/statistics/achievement/profile integration.
- Verify all six games run independently as well as through the hub.
- Verify the static registry is the single source of game registration.
- Verify no game-specific hardcoding has leaked into generic hub logic where capability/configuration abstractions already exist.
- Run the complete regression suite.
- Run syntax/import checks across the repository.
- Run persistence/integration tests.
- Verify `.gitignore` and V2 persistence/runtime files; do not assume the V1 `scoreboard.json` filename remains part of the V2 architecture.
- Update `README.md` and documentation to match the final V2 implementation.
- Perform the final architecture/scope audit against this locked gameplan.
- Confirm the project still respects the V2 scope boundary:
  no GUI, web application, online multiplayer, database-backed service, generic game engine, plugin ecosystem, or AI research platform.

Tests required before commit:
- Full repository test suite.
- Full six-game integration tests.
- Independent game execution tests.
- Hub navigation/configuration tests.
- Persistence regression tests.
- Statistics/achievements/meta-progression regression tests.
- Final documentation/structure audit.

### Five-Commit Rule

The V2 implementation is considered complete only after these five commits are completed in order:

```text
1. V2 Foundation & Core Architecture
                ↓
2. Board Games Migration
                ↓
3. Non-Real-Time Games Migration
                ↓
4. Snake, Progression & Advanced Hub Integration
                ↓
5. Full Integration, Hardening & V2 Release
```

Each commit is a meaningful milestone with a defined architectural purpose. Related implementation and tests belong in the same milestone, but the same feature must not be independently reimplemented in multiple commits.

Small fixes should be incorporated into the appropriate open milestone before it is committed. No sixth V2 feature commit should be created merely because a small issue or polish item appears.

The locked `gameplan.md` remains the source of truth for V2 scope and architecture. The five-commit plan controls **implementation grouping**, not permission to add new scope during development.
