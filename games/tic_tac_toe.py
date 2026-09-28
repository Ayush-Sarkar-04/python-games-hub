"""Tic-Tac-Toe game implementation and V2 adapter.

TicTacToeGame is the canonical implementation used by both the hub and standalone entry point.
"""

import random
from copy import deepcopy
from time import sleep

from engine.game import SessionConfig
from engine.result import GameResult
from engine.state import GameState
from engine.utils import choose_from_menu, play_again

EASY = "1"
MEDIUM = "2"
HARD = "3"

DIFFICULTY_MAP = {
    "easy": EASY,
    "medium": MEDIUM,
    "hard": HARD,
}

CUSTOM_MINIMAX_DEPTH_MIN = 1
CUSTOM_MINIMAX_DEPTH_MAX = 9

WINNING_COMBINATIONS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]


def display_title():
    print("\n" + "=" * 42)
    print("              TIC-TAC-TOE")
    print("=" * 42)


def display_board(board):
    print()
    cells = [
        str(index + 1) if value == " " else value
        for index, value in enumerate(board)
    ]
    print("          |       |")
    print(f"       {cells[0]:^5}|{cells[1]:^7}|{cells[2]:^5}")
    print("     ------+-------+------")
    print(f"       {cells[3]:^5}|{cells[4]:^7}|{cells[5]:^5}")
    print("     ------+-------+------")
    print(f"       {cells[6]:^5}|{cells[7]:^7}|{cells[8]:^5}")
    print()


def get_winner(board):
    for a, b, c in WINNING_COMBINATIONS:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None


def check_winner(board):
    return get_winner(board) is not None


def get_player_move(board, player):
    while True:
        choice = input(f"Player {player}, choose a position (1-9): ").strip()
        try:
            position = int(choice) - 1
        except ValueError:
            print("Invalid input! Please enter a number from 1 to 9.")
            continue
        if position < 0 or position > 8:
            print("Invalid position! Please choose a number from 1 to 9.")
            continue
        if board[position] != " ":
            print("Position already taken! Choose another position.")
            continue
        return position


def get_empty_positions(board):
    return [i for i in range(9) if board[i] == " "]


def find_winning_move(board, player):
    for position in get_empty_positions(board):
        board[position] = player
        if check_winner(board):
            board[position] = " "
            return position
        board[position] = " "
    return None


def _line_score(line):
    if line.count("O") == 2 and line.count(" ") == 1:
        return 2
    if line.count("O") == 1 and line.count(" ") == 2:
        return 1
    if line.count("X") == 2 and line.count(" ") == 1:
        return -2
    if line.count("X") == 1 and line.count(" ") == 2:
        return -1
    return 0


def evaluate_board(board):
    return sum(_line_score([board[index] for index in combination]) for combination in WINNING_COMBINATIONS)


def minimax(board, maximizing, depth=None):
    winner = get_winner(board)
    if winner == "O":
        return 1
    if winner == "X":
        return -1

    empty_positions = get_empty_positions(board)
    if not empty_positions or depth == 0:
        return 0 if not depth else evaluate_board(board)

    if maximizing:
        best_score = -float("inf")
        for position in empty_positions:
            board[position] = "O"
            score = minimax(board, False, None if depth is None else depth - 1)
            board[position] = " "
            best_score = max(best_score, score)
        return best_score

    best_score = float("inf")
    for position in empty_positions:
        board[position] = "X"
        score = minimax(board, True, None if depth is None else depth - 1)
        board[position] = " "
        best_score = min(best_score, score)
    return best_score


def find_best_move(board, personality="Balanced", depth=None):
    best_score = -float("inf")
    best_moves = []

    for position in get_empty_positions(board):
        board[position] = "O"
        score = minimax(board, False, None if depth is None else depth - 1)
        board[position] = " "
        if score > best_score:
            best_score = score
            best_moves = [position]
        elif score == best_score:
            best_moves.append(position)

    if personality == "Aggressive":
        preferred = [position for position in (4, 0, 2, 6, 8) if position in best_moves]
    elif personality == "Defensive":
        preferred = [position for position in (0, 2, 6, 8, 4) if position in best_moves]
    else:
        preferred = best_moves

    preferred = preferred or best_moves
    return random.choice(preferred)


def choose_personality():
    personalities = {
        "1": "Balanced",
        "2": "Aggressive",
        "3": "Defensive",
    }
    while True:
        print("\nChoose Computer Personality")
        print("1. Balanced")
        print("2. Aggressive")
        print("3. Defensive")
        choice = input("\nChoose: ").strip()
        if choice in personalities:
            return personalities[choice]
        print("Invalid choice! Please choose 1, 2, or 3.")


def computer_move(board, difficulty, personality="Balanced", custom_depth=None):
    empty_positions = get_empty_positions(board)

    if difficulty == EASY:
        return random.choice(empty_positions)

    winning_move = find_winning_move(board, "O")
    if winning_move is not None:
        return winning_move

    blocking_move = find_winning_move(board, "X")
    if blocking_move is not None:
        return blocking_move

    if difficulty == MEDIUM:
        if personality == "Aggressive":
            center = 4
            if center in empty_positions and random.random() < 0.7:
                return center
        elif personality == "Defensive":
            blocking_move = find_winning_move(board, "X")
            if blocking_move is not None:
                return blocking_move
        return random.choice(empty_positions)

    # Hard remains unbeatable; personality only changes tie-breaking preference.
    return find_best_move(board, personality, custom_depth)


def display_result(message):
    print("\n" + "=" * 42)
    print("                 GAME OVER")
    print("=" * 42)
    print(f"                 {message}")
    print("=" * 42)


def choose_difficulty():
    """Choose a standard difficulty for standalone execution."""
    print("\nChoose Difficulty")
    print("1. Easy")
    print("2. Medium")
    print("3. Hard")
    return choose_from_menu(
        "Choose difficulty: ",
        {EASY, MEDIUM, HARD},
    )


def _hint_move(board, difficulty, personality, custom_depth=None):
    """Calculate a hint without changing the real board."""
    simulated_board = deepcopy(board)
    if difficulty == EASY:
        return random.choice(get_empty_positions(simulated_board))
    return computer_move(simulated_board, difficulty, personality, custom_depth)


def _display_replay(move_history, delay=0.0):
    """Replay committed moves only; AI simulations are never in history."""
    board = [" "] * 9
    for move in move_history:
        board[move["position"]] = move["player"]
        display_board(board)
        if delay > 0:
            sleep(delay)


def _get_v2_player_move(state, player, difficulty, personality, hint_used, custom_depth=None):
    while True:
        choice = input(
            f"Player {player}, choose a position (1-9)"
            f"{' or H for hint' if not hint_used else ''}: "
        ).strip().lower()

        if choice == "h" and not hint_used:
            hint = _hint_move(state.data["board"], difficulty, personality, custom_depth)
            print(f"Hint: position {hint + 1}.")
            return None, True

        try:
            position = int(choice) - 1
        except ValueError:
            print("Invalid input! Please enter a number from 1 to 9.")
            continue

        if position < 0 or position > 8:
            print("Invalid position! Please choose a number from 1 to 9.")
            continue
        if state.data["board"][position] != " ":
            print("Position already taken! Choose another position.")
            continue
        return position, hint_used


class TicTacToeGame:
    """V2 adapter around the existing Tic-Tac-Toe rules and AI."""

    name = "Tic-Tac-Toe"
    description = "Classic 3x3 strategy game"
    CUSTOM_PARAMETERS = {"minimax_depth": (1, 9, "Minimax depth")}

    @classmethod
    def validate_custom_settings(cls, settings):
        depth = settings.get("minimax_depth")
        if isinstance(depth, bool) or not isinstance(depth, int):
            raise ValueError("Tic-Tac-Toe custom minimax_depth must be an integer")
        if not CUSTOM_MINIMAX_DEPTH_MIN <= depth <= CUSTOM_MINIMAX_DEPTH_MAX:
            raise ValueError("Tic-Tac-Toe custom minimax_depth must be between 1 and 9")
        return {"minimax_depth": depth}

    def __init__(self):
        self.win_streak = 0
        self.best_streak = 0

    def setup(self, config: SessionConfig) -> GameState:
        if config.game != "tic_tac_toe":
            raise ValueError("TicTacToeGame requires game='tic_tac_toe'")
        if config.difficulty not in DIFFICULTY_MAP and config.difficulty != "custom":
            raise ValueError(
                f"Unsupported Tic-Tac-Toe difficulty: {config.difficulty}"
            )

        custom_settings = {}
        if config.difficulty == "custom":
            custom_settings = self.validate_custom_settings(config.custom_settings)

        player_mode = config.options.get("player_mode", "computer")
        if player_mode not in {"computer", "player"}:
            raise ValueError("player_mode must be 'computer' or 'player'")

        personality = config.options.get("personality", "Balanced")
        if personality not in {"Balanced", "Aggressive", "Defensive"}:
            raise ValueError("Unsupported Tic-Tac-Toe personality")

        return GameState(
            game="tic_tac_toe",
            status="ready",
            data={
                "board": [" "] * 9,
                "current_player": "X",
                "player_mode": player_mode,
                "personality": personality,
                "hint_used": False,
                "custom_settings": custom_settings,
            },
            metadata={"difficulty": config.difficulty},
        )

    def play(self, state: GameState, config: SessionConfig) -> GameResult:
        difficulty = DIFFICULTY_MAP.get(config.difficulty, HARD)
        custom_depth = state.data["custom_settings"].get("minimax_depth")
        board = state.data["board"]
        player_mode = state.data["player_mode"]
        personality = state.data["personality"]

        state.set_status("playing")
        display_title()

        if player_mode == "computer":
            print(f"You are X. Computer is O. Personality: {personality}")
        if config.mode == "practice":
            print("Practice Mode: this session does not count toward competitive streaks.")

        for _ in range(9):
            display_board(board)
            player = state.data["current_player"]

            if player_mode == "computer" and player == "O":
                position = computer_move(board, difficulty, personality, custom_depth)
                print(f"Computer chooses position {position + 1}.")
            else:
                while True:
                    position, hint_used = _get_v2_player_move(
                        state,
                        player,
                        difficulty,
                        personality,
                        state.data["hint_used"],
                        custom_depth,
                    )
                    if position is not None:
                        state.data["hint_used"] = hint_used
                        break
                    state.data["hint_used"] = hint_used

            board[position] = player
            state.record_move({"player": player, "position": position})

            if check_winner(board):
                display_board(board)
                if player_mode == "computer" and player == "O":
                    outcome = "loss"
                    message = "Computer wins!"
                else:
                    outcome = "win"
                    message = f"Player {player} wins!"

                display_result(message)
                state.set_status(outcome)

                if config.is_competitive and player_mode == "computer":
                    if outcome == "win":
                        self.win_streak += 1
                        self.best_streak = max(self.best_streak, self.win_streak)
                    else:
                        self.win_streak = 0

                configuration = {"player_mode": player_mode, "personality": personality}
                if custom_depth is not None:
                    configuration["custom_settings"] = {"minimax_depth": custom_depth}

                result = GameResult(
                    game="tic_tac_toe",
                    outcome=outcome,
                    difficulty=config.difficulty,
                    mode=config.mode,
                    score=self._score(config.difficulty, outcome, custom_depth),
                    moves=state.moves,
                    metadata={
                        "configuration": configuration,
                        "hint_used": state.data["hint_used"],
                        "win_streak": self.win_streak,
                        "best_streak": self.best_streak,
                    },
                )
                return self._finish_with_optional_replay(result, state)

            state.data["current_player"] = "O" if player == "X" else "X"

        display_board(board)
        display_result("It's a draw!")
        state.set_status("draw")

        if config.is_competitive and player_mode == "computer":
            self.win_streak = 0

        configuration = {"player_mode": player_mode, "personality": personality}
        if custom_depth is not None:
            configuration["custom_settings"] = {"minimax_depth": custom_depth}

        result = GameResult(
            game="tic_tac_toe",
            outcome="draw",
            difficulty=config.difficulty,
            mode=config.mode,
            score=self._score(config.difficulty, "draw", custom_depth),
            moves=state.moves,
            metadata={
                "configuration": configuration,
                "hint_used": state.data["hint_used"],
                "win_streak": self.win_streak,
                "best_streak": self.best_streak,
            },
        )
        return self._finish_with_optional_replay(result, state)

    @staticmethod
    def _score(difficulty, outcome, custom_depth):
        if outcome != "win":
            return 0
        if difficulty == "custom":
            return min(custom_depth, 5)
        return {"easy": 1, "medium": 2, "hard": 3}[difficulty]

    def _finish_with_optional_replay(self, result, state):
        """Offer replay without changing the recorded result or state."""
        choice = input("\nReplay this game? (y/n): ").strip().lower()
        if choice == "y":
            print("\nREPLAY")
            _display_replay(state.move_history)
        return result


def main(record_result=None):
    """Standalone entry point using the canonical V2 game implementation."""
    game = TicTacToeGame()

    while True:
        display_title()
        print("\n1. Player vs Computer")
        print("2. Player vs Player")
        print("3. Exit")
        choice = input("\nChoose: ").strip()

        if choice == "3":
            print("\nThanks for playing Tic-Tac-Toe!")
            break
        if choice not in {"1", "2"}:
            print("\nInvalid choice! Please choose 1, 2, or 3.")
            continue

        if choice == "1":
            difficulty = choose_difficulty()
            personality = choose_personality()
            options = {"player_mode": "computer", "personality": personality}
            print(f"\nYou are X. Computer is O. Personality: {personality}")
        else:
            difficulty = MEDIUM
            options = {"player_mode": "player", "personality": "Balanced"}
            print("\nPlayer X goes first.")

        config = SessionConfig(
            game="tic_tac_toe",
            difficulty={EASY: "easy", MEDIUM: "medium", HARD: "hard"}[difficulty],
            options=options,
        )
        result = game.play(game.setup(config), config)

        if record_result:
            record_result("tic_tac_toe", result.outcome)

        if not play_again():
            print("\nThanks for playing Tic-Tac-Toe!")
            break


if __name__ == "__main__":
    main()
