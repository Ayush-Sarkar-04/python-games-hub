"""Terminal Minesweeper implementation for the Game Hub."""

import random
from collections import deque

from engine.game import SessionConfig
from engine.result import GameResult
from engine.state import GameState
from engine.utils import display_title


DIFFICULTIES = {
    "easy": {"name": "Easy", "rows": 9, "columns": 9, "mines": 10, "multiplier": 1},
    "medium": {"name": "Medium", "rows": 16, "columns": 16, "mines": 40, "multiplier": 2},
    "hard": {"name": "Hard", "rows": 16, "columns": 30, "mines": 99, "multiplier": 3},
}

HIDDEN = "##"
FLAGGED = "F "


def neighbors(row, column, rows, columns):
    for row_delta in (-1, 0, 1):
        for column_delta in (-1, 0, 1):
            if row_delta == 0 and column_delta == 0:
                continue
            neighbor = (row + row_delta, column + column_delta)
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < columns:
                yield neighbor


def generate_mines(rows, columns, mine_count, first_cell=None):
    cells = [(row, column) for row in range(rows) for column in range(columns)]
    excluded = {first_cell} if first_cell is not None else set()
    candidates = [cell for cell in cells if cell not in excluded]
    if mine_count > len(candidates):
        raise ValueError("mine count is too large for the board")
    return set(random.sample(candidates, mine_count))


def calculate_adjacent_mines(mines, rows, columns):
    counts = {}
    for row in range(rows):
        for column in range(columns):
            counts[(row, column)] = sum(
                neighbor in mines
                for neighbor in neighbors(row, column, rows, columns)
            )
    return counts


def reveal_cells(state, start):
    data = state.data
    rows, columns = data["rows"], data["columns"]
    mines = data["mines"]
    counts = data["counts"]
    revealed = data["revealed"]
    flagged = data["flagged"]

    if start in flagged or start in revealed:
        return set()
    if start in mines:
        revealed.add(start)
        return {start}

    newly_revealed = set()
    queue = deque([start])
    while queue:
        cell = queue.popleft()
        if cell in revealed or cell in flagged or cell in mines:
            continue
        revealed.add(cell)
        newly_revealed.add(cell)
        if counts[cell] == 0:
            queue.extend(neighbor for neighbor in neighbors(*cell, rows, columns) if neighbor not in revealed)
    return newly_revealed


def board_complete(state):
    safe_cells = state.data["rows"] * state.data["columns"] - len(state.data["mines"])
    return len(state.data["revealed"] - state.data["mines"]) >= safe_cells


def format_cell(state, cell):
    data = state.data
    if cell in data["flagged"]:
        return FLAGGED
    if cell not in data["revealed"]:
        return HIDDEN
    if cell in data["mines"]:
        return "* "
    count = data["counts"][cell]
    return ". " if count == 0 else f"{count} "


def display_instructions():
    print("\nHOW TO PLAY")
    print("Goal: reveal every safe cell without hitting a mine.")
    print("Numbers show how many mines touch that cell, including diagonals.")
    print("Flag cells you think contain mines. Press f again to remove a flag.")
    print("Symbols: ## = hidden | F = flag | . = no adjacent mines | 1-8 = nearby mines")
    print("Your first reveal is always safe.")
    print("\nCommands:")
    print("  r row column   Reveal a cell")
    print("  f row column   Flag / unflag a cell")
    print("  h              Show these instructions again")
    print("  q              Quit the game")
    print("  Full words also work: reveal 5 7, flag 5 7, help, quit")
    print("\nExample:  r 5 7   = reveal row 5, column 7")


def display_board(state):
    data = state.data
    rows, columns = data["rows"], data["columns"]
    header = "    " + " ".join(f"{column + 1:02}" for column in range(columns))
    print(header)
    print("    " + "-" * (columns * 3 - 1))
    for row in range(rows):
        cells = " ".join(format_cell(state, (row, column)) for column in range(columns))
        print(f"{row + 1:02} | {cells}")
    print(f"\nMines: {data['mine_count']} | Flags: {len(data['flagged'])} | Score: {data['score']}")
    print("Commands: r row column = reveal | f row column = flag | h = help | q = quit")


class MinesweeperGame:
    name = "Minesweeper"
    description = "Reveal safe cells, flag mines, and clear the board"

    def setup(self, config: SessionConfig) -> GameState:
        if config.game != "minesweeper":
            raise ValueError("MinesweeperGame requires game='minesweeper'")
        if config.difficulty not in DIFFICULTIES:
            raise ValueError(f"Unsupported Minesweeper difficulty: {config.difficulty}")

        difficulty = DIFFICULTIES[config.difficulty]
        rows, columns, mine_count = difficulty["rows"], difficulty["columns"], difficulty["mines"]
        provided_mines = config.options.get("mine_positions")
        if provided_mines is None:
            mines = set()
        else:
            mines = {tuple(cell) for cell in provided_mines}
            expected_cells = rows * columns
            if len(mines) != mine_count or any(
                not isinstance(cell, tuple) or len(cell) != 2
                or not all(isinstance(value, int) and not isinstance(value, bool) for value in cell)
                or not (0 <= cell[0] < rows and 0 <= cell[1] < columns)
                for cell in mines
            ):
                raise ValueError("mine_positions must contain exactly the configured number of valid cells")
            if len(mines) >= expected_cells:
                raise ValueError("mine_positions leaves no safe cells")

        return GameState(
            game="minesweeper",
            data={
                "rows": rows,
                "columns": columns,
                "mine_count": mine_count,
                "mines": mines,
                "counts": calculate_adjacent_mines(mines, rows, columns) if mines else {},
                "revealed": set(),
                "flagged": set(),
                "first_move": True,
                "score": 0,
            },
        )

    def play(self, state: GameState, config: SessionConfig) -> GameResult:
        state.set_status("playing")
        show_help = True
        while True:
            display_title("MINESWEEPER")
            print(f"Difficulty: {DIFFICULTIES[config.difficulty]['name']}")
            if show_help:
                display_instructions()
                show_help = False
            display_board(state)
            command = input("\nMove (example: r 5 7): ").strip().lower().split()

            aliases = {
                "reveal": "r",
                "flag": "f",
                "unflag": "f",
                "help": "h",
                "quit": "q",
            }
            if command:
                command[0] = aliases.get(command[0], command[0])

            if command == ["q"]:
                return self._finish(state, config, "quit")
            if command == ["h"]:
                display_instructions()
                continue
            if len(command) != 3 or command[0] not in {"r", "f"}:
                print("Invalid command. Use r row column, f row column, h, or q.")
                continue

            try:
                row, column = int(command[1]) - 1, int(command[2]) - 1
            except ValueError:
                print("Row and column must be numbers.")
                continue

            cell = (row, column)
            if not (0 <= row < state.data["rows"] and 0 <= column < state.data["columns"]):
                print("That cell is outside the board.")
                continue

            if command[0] == "f":
                if cell in state.data["revealed"]:
                    print("You cannot flag a revealed cell.")
                    continue
                if cell in state.data["flagged"]:
                    state.data["flagged"].remove(cell)
                else:
                    state.data["flagged"].add(cell)
                state.record_move({"action": "flag", "cell": cell})
                continue

            if cell in state.data["flagged"]:
                print("Unflag the cell before revealing it.")
                continue

            if state.data["first_move"]:
                if not state.data["mines"]:
                    state.data["mines"] = generate_mines(
                        state.data["rows"], state.data["columns"], state.data["mine_count"], cell
                    )
                    state.data["counts"] = calculate_adjacent_mines(
                        state.data["mines"], state.data["rows"], state.data["columns"]
                    )
                state.data["first_move"] = False

            if cell in state.data["revealed"]:
                print("That cell is already revealed.")
                continue

            state.record_move({"action": "reveal", "cell": cell})
            if cell in state.data["mines"]:
                state.data["revealed"].add(cell)
                return self._finish(state, config, "loss")

            newly_revealed = reveal_cells(state, cell)
            state.data["score"] = len(state.data["revealed"] - state.data["mines"]) * DIFFICULTIES[config.difficulty]["multiplier"]
            if newly_revealed:
                print(f"Revealed {len(newly_revealed)} safe cell(s).")
            if board_complete(state):
                return self._finish(state, config, "win")

    def _finish(self, state, config, outcome):
        state.set_status(outcome)
        if outcome == "win":
            state.data["score"] = (
                len(state.data["revealed"] - state.data["mines"])
                * DIFFICULTIES[config.difficulty]["multiplier"]
            )
        return GameResult(
            game="minesweeper",
            outcome=outcome,
            difficulty=config.difficulty,
            mode=config.mode,
            score=state.data["score"],
            moves=state.moves,
            metadata={
                "mines": state.data["mine_count"],
                "flags": len(state.data["flagged"]),
                "safe_cells_revealed": len(state.data["revealed"] - state.data["mines"]),
                "configuration": {
                    "rows": state.data["rows"],
                    "columns": state.data["columns"],
                },
            },
        )


def main():
    game = MinesweeperGame()
    print("\nSelect Difficulty")
    print("1. Easy\n2. Medium\n3. Hard")
    difficulty = {"1": "easy", "2": "medium", "3": "hard"}.get(input("Enter choice: ").strip())
    if not difficulty:
        print("Invalid choice.")
        return
    config = SessionConfig(game="minesweeper", difficulty=difficulty)
    game.play(game.setup(config), config)


if __name__ == "__main__":
    main()
