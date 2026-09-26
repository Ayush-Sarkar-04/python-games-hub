# Python Games Hub

Classic Python games rebuilt with smarter gameplay, multiple modes, and a unified persistent scoreboard.

## Games

| Game | Description |
|---|---|
| Tic-Tac-Toe | Classic 3x3 strategy game with Easy, Medium, and unbeatable Hard AI |
| Hangman | Word-guessing game with categories, difficulty levels, hints, and streak tracking |
| Rock Paper Scissors | Single game or Best-of mode with optional Lizard & Spock and computer personality |
| Word Scramble | Difficulty-based word scrambling with an online word source and local fallback |
| Connect Four | Player vs Computer or Player vs Player with Easy, Medium, and Hard AI |
| Snake | Real-time terminal Snake with difficulty levels, power-ups, pause, and optional wrap-around |

## Key Features

- Six independently runnable games
- Player vs Computer and/or Player vs Player modes where supported
- Difficulty levels on supported games
- Smarter computer opponents, including minimax-based Hard modes
- Persistent unified scoreboard
- Game-specific statistics
- Session streak tracking on supported games
- Replay support
- Input validation
- Network word sources with local fallbacks where applicable
- Standard-library implementation

## Unified Scoreboard

The Games Hub maintains a persistent `scoreboard.json` file beside `main.py`.

The scoreboard tracks game-appropriate statistics:

- **Tic-Tac-Toe:** played, wins, losses, draws
- **Hangman:** played, wins, losses
- **Rock Paper Scissors:** games/matches, wins, losses, draws
- **Word Scramble:** rounds, wins, losses
- **Connect Four:** played, wins, losses, draws
- **Snake:** games, best score, total score

`scoreboard.json` is local runtime data and should not be committed to Git.

## Controls

### Menu-Based Games

Tic-Tac-Toe, Hangman, Rock Paper Scissors, Word Scramble, and Connect Four use keyboard input through the terminal.

Each game validates player input and provides prompts for invalid selections.

### Snake

- **W / A / S / D** — Move
- **Arrow Keys** — Move
- **P** — Pause / Resume
- **Q** — Quit

## External Word Sources

Two games can use online word sources:

- **Hangman** loads category data from a remote JSON source and includes a local fallback.
- **Word Scramble** uses the Random Word API and includes difficulty-specific fallback words.

The games remain playable when the external word source is unavailable.

## Project Structure

```text
python-games-hub/
├── main.py
├── tic_tac_toe.py
├── hangman.py
├── rock_paper_scissors.py
├── word_scramble.py
├── connect_four.py
├── snake.py
├── README.md
└── .gitignore
```

`scoreboard.json` is created automatically at runtime and is intentionally ignored by Git.

## Requirements

The games use Python's standard library. No third-party Python package is required for the current game hub.

Python 3.10+ is recommended.

## Running the Hub

From the project directory:

```bash
python main.py
```

Each game can also be run independently:

```bash
python tic_tac_toe.py
python hangman.py
python rock_paper_scissors.py
python word_scramble.py
python connect_four.py
python snake.py
```

## Design Approach

The project keeps each game in its own module while `main.py` acts as the hub and scoreboard owner.

Games report completed results through an optional callback. This allows every game to remain independently runnable without creating circular imports between the game modules and the hub.

The project focuses on clean terminal gameplay, practical Python structure, and progressively smarter implementations rather than unnecessary frameworks or abstractions.

## Current Scope

The project is a standalone collection of terminal games designed as a Python development project and portfolio piece.

Future changes can focus on polish, testing, documentation, and usability rather than continuously adding gameplay complexity.
