import os
import random
import sys
import time
from engine.game import SessionConfig
from engine.result import GameResult
from engine.state import GameState
from engine.utils import display_title
ROWS, COLUMNS = 20, 30
DIFFICULTIES = {
    "easy": ("Easy", 0.18),
    "medium": ("Medium", 0.12),
    "hard": ("Hard", 0.08),
}
SPEED_INCREMENT, MIN_SPEED = 0.003, 0.045
FOOD_SCORE, BONUS_SCORE = 10, 30
SLOW_DURATION, POWERUP_CHANCE = 5.0, 0.18
PAUSE_POLL_INTERVAL = 0.03
INITIAL_SNAKE = [
    (ROWS // 2, COLUMNS // 2),
    (ROWS // 2, COLUMNS // 2 - 1),
    (ROWS // 2, COLUMNS // 2 - 2),
]
DIRECTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}
OPPOSITE = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
def create_food(snake):
    available = [
        (row, column)
        for row in range(ROWS)
        for column in range(COLUMNS)
        if (row, column) not in snake
    ]
    return random.choice(available)
def display_board(snake, food, score, powerup=None, powerup_type=None):
    head, body = snake[0], set(snake[1:])
    print("+" + "---" * COLUMNS + "+")
    for row in range(ROWS):
        line = "|"
        for column in range(COLUMNS):
            position = (row, column)
            symbol = (
                "@" if position == head else
                "O" if position in body else
                "*" if position == food else
                ("+" if powerup_type == "bonus" else "-") if position == powerup else " "
            )
            line += f" {symbol} "
        print(line + "|")
    print("+" + "---" * COLUMNS + "+")
    print(f"Score: {score}")
    print("Controls: W/A/S/D or Arrow Keys | P = Pause | Q = Quit")
    print("Power-ups: + = Bonus Score | - = Slow Down")
def setup_terminal():
    if os.name == "nt":
        return None
    import termios
    import tty
    fd = sys.stdin.fileno()
    original = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    return original
def restore_terminal(original):
    if os.name != "nt" and original is not None:
        import termios
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, original)
def read_key():
    if os.name == "nt":
        import msvcrt
        if not msvcrt.kbhit():
            return None
        key = msvcrt.getch()
        if key in (b"\x00", b"\xe0"):
            return {
                b"H": "UP", b"P": "DOWN", b"K": "LEFT", b"M": "RIGHT"
            }.get(msvcrt.getch())
        return key.decode("utf-8", errors="ignore").lower()
    import select
    ready, _, _ = select.select([sys.stdin], [], [], 0)
    if not ready:
        return None
    key = sys.stdin.read(1)
    if key == "\x1b":
        return {
            "[A": "UP", "[B": "DOWN", "[C": "RIGHT", "[D": "LEFT"
        }.get(sys.stdin.read(2))
    return key.lower()
def get_direction(key):
    return {
        "w": "UP", "a": "LEFT", "s": "DOWN", "d": "RIGHT",
        "UP": "UP", "DOWN": "DOWN", "LEFT": "LEFT", "RIGHT": "RIGHT",
    }.get(key)
def move_snake(snake, direction, wrap):
    row, column = snake[0]
    dr, dc = DIRECTIONS[direction]
    head = (row + dr, column + dc)
    if wrap:
        head = (head[0] % ROWS, head[1] % COLUMNS)
    snake.insert(0, head)
    return head
class SnakeGame:
    name = "Snake"
    description = "Classic real-time terminal Snake"
    def setup(self, config: SessionConfig) -> GameState:
        if config.game != "snake":
            raise ValueError("SnakeGame requires game='snake'")
        if config.difficulty not in DIFFICULTIES:
            raise ValueError(f"Unsupported Snake difficulty: {config.difficulty}")
        return GameState(
            game="snake",
            data={
                "snake": list(INITIAL_SNAKE),
                "direction": "RIGHT",
                "food": create_food(INITIAL_SNAKE),
                "powerup": None,
                "powerup_type": None,
                "score": 0,
                "speed": DIFFICULTIES[config.difficulty][1],
                "slow_until": 0.0,
                "wrap": bool(config.options.get("wrap", False)),
            },
        )
    def play(self, state: GameState, config: SessionConfig) -> GameResult:
        state.set_status("playing")
        data = state.data
        original_terminal = setup_terminal()
        try:
            while True:
                os.system("cls" if os.name == "nt" else "clear")
                display_title("SNAKE")
                print(f"Difficulty: {DIFFICULTIES[config.difficulty][0]}\n")
                display_board(
                    data["snake"], data["food"], data["score"],
                    data["powerup"], data["powerup_type"],
                )
                key = read_key()
                if key == "q":
                    return self._finish(state, config, "quit")
                if key == "p":
                    self._pause()
                    continue
                new_direction = get_direction(key)
                if new_direction and new_direction != OPPOSITE[data["direction"]]:
                    data["direction"] = new_direction
                head = move_snake(data["snake"], data["direction"], data["wrap"])
                if not data["wrap"] and not (
                    0 <= head[0] < ROWS and 0 <= head[1] < COLUMNS
                ):
                    return self._finish(state, config, "game_over")
                if head in data["snake"][1:]:
                    return self._finish(state, config, "game_over")
                state.record_move({"direction": data["direction"], "position": head})
                if head == data["food"]:
                    data["score"] += FOOD_SCORE
                    data["food"] = create_food(data["snake"])
                    data["speed"] = max(MIN_SPEED, data["speed"] - SPEED_INCREMENT)
                    if random.random() < POWERUP_CHANCE:
                        data["powerup"] = create_food(data["snake"] + [data["food"]])
                        data["powerup_type"] = random.choice(("bonus", "slow"))
                elif data["powerup"] and head == data["powerup"]:
                    if data["powerup_type"] == "bonus":
                        data["score"] += BONUS_SCORE
                    else:
                        data["slow_until"] = time.time() + SLOW_DURATION
                    data["powerup"] = None
                    data["powerup_type"] = None
                else:
                    data["snake"].pop()
                speed = data["speed"] * 1.5 if time.time() < data["slow_until"] else data["speed"]
                time.sleep(speed)
        finally:
            restore_terminal(original_terminal)
    def _pause(self):
        print("\nGAME PAUSED\nPress P to continue.")
        while read_key() != "p":
            time.sleep(PAUSE_POLL_INTERVAL)
    def _finish(self, state, config, outcome):
        state.set_status(outcome)
        score = state.data["score"]
        print("\n" + "=" * 52)
        print("                    GAME OVER" if outcome == "game_over" else "                     QUIT")
        print("=" * 52)
        print(f"Difficulty : {DIFFICULTIES[config.difficulty][0]}")
        print(f"Final Score: {score}")
        return GameResult(
            game="snake",
            outcome=outcome,
            difficulty=config.difficulty,
            mode=config.mode,
            score=score,
            moves=state.moves,
            metadata={"wrap": state.data["wrap"]},
        )
def main():
    game = SnakeGame()
    while True:
        print("\nSelect Difficulty")
        print("1. Easy\n2. Medium\n3. Hard")
        difficulty = {"1": "easy", "2": "medium", "3": "hard"}.get(
            input("Enter choice: ").strip()
        )
        if not difficulty:
            print("Invalid choice. Please select 1, 2, or 3.")
            continue
        wrap = input("\nEnable wrap-around walls? (y/n): ").strip().lower()
        if wrap not in {"y", "n"}:
            print("Please enter Y or N.")
            continue
        config = SessionConfig(
            game="snake",
            difficulty=difficulty,
            options={"wrap": wrap == "y"},
        )
        result = game.play(game.setup(config), config)
        if result.outcome == "quit" or input("\nPlay again? (Y/N): ").strip().lower() != "y":
            print("\nThanks for playing Snake.")
            break
if __name__ == "__main__":
    main()