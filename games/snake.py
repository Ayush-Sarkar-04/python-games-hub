import os
import random
import sys
import time
ROWS = 20
COLUMNS = 30
EASY_SPEED = 0.18
MEDIUM_SPEED = 0.12
HARD_SPEED = 0.08
SPEED_INCREMENT = 0.003
MIN_SPEED = 0.045
FOOD_SCORE = 10
BONUS_SCORE = 30
SLOW_DURATION = 5.0
POWERUP_CHANCE = 0.18
PAUSE_POLL_INTERVAL = 0.03
INITIAL_SNAKE = [(ROWS // 2, COLUMNS // 2),
                 (ROWS // 2, COLUMNS // 2 - 1),
                 (ROWS // 2, COLUMNS // 2 - 2)]
DIRECTIONS = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1),
}
OPPOSITE_DIRECTIONS = {
    "UP": "DOWN",
    "DOWN": "UP",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
}
EASY = "1"
MEDIUM = "2"
HARD = "3"

DIFFICULTIES = {
    EASY: ("Easy", EASY_SPEED),
    MEDIUM: ("Medium", MEDIUM_SPEED),
    HARD: ("Hard", HARD_SPEED),
}
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")
def display_title():
    print("=" * 52)
    print("                      S N A K E")
    print("=" * 52)
    print("Classic terminal Snake")
    print()
def create_food(snake):
    available_positions = [
        (row, column)
        for row in range(ROWS)
        for column in range(COLUMNS)
        if (row, column) not in snake
    ]
    return random.choice(available_positions)
def display_board(snake, food, score, powerup=None, powerup_type=None):
    snake_head = snake[0]
    snake_body = set(snake[1:])
    print("+" + "---" * COLUMNS + "+")
    for row in range(ROWS):
        line = "|"
        for column in range(COLUMNS):
            position = (row, column)
            if position == snake_head:
                symbol = "@"
            elif position in snake_body:
                symbol = "O"
            elif position == food:
                symbol = "*"
            elif position == powerup:
                symbol = "+" if powerup_type == "bonus" else "-"
            else:
                symbol = " "
            line += f" {symbol} "
        line += "|"
        print(line)
    print("+" + "---" * COLUMNS + "+")
    print(f"Score: {score}")
    print("Controls: W/A/S/D or Arrow Keys | P = Pause | Q = Quit")
    print("Power-ups: + = Bonus Score | - = Slow Down")
def choose_difficulty():
    while True:
        clear_screen()
        display_title()
        print("Select Difficulty")
        print("-" * 52)
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        print()
        choice = input("Enter choice: ").strip()
        if choice in DIFFICULTIES:
            return DIFFICULTIES[choice]
        print("\nInvalid choice. Please select 1, 2, or 3.")
        time.sleep(1)
def setup_terminal():
    if os.name == "nt":
        return None
    import termios
    import tty
    file_descriptor = sys.stdin.fileno()
    original_settings = termios.tcgetattr(file_descriptor)
    tty.setcbreak(file_descriptor)
    return original_settings
def restore_terminal(original_settings):
    if os.name == "nt" or original_settings is None:
        return
    import termios
    file_descriptor = sys.stdin.fileno()
    termios.tcsetattr(
        file_descriptor,
        termios.TCSADRAIN,
        original_settings,
    )
def read_key():
    if os.name == "nt":
        import msvcrt
        if not msvcrt.kbhit():
            return None
        key = msvcrt.getch()
        if key in (b"\x00", b"\xe0"):
            arrow_key = msvcrt.getch()
            return {
                b"H": "UP",
                b"P": "DOWN",
                b"K": "LEFT",
                b"M": "RIGHT",
            }.get(arrow_key)
        try:
            return key.decode("utf-8").lower()
        except UnicodeDecodeError:
            return None
    import select
    ready, _, _ = select.select([sys.stdin], [], [], 0)
    if not ready:
        return None
    key = sys.stdin.read(1)
    if key == "\x1b":
        sequence = sys.stdin.read(2)
        return {
            "[A": "UP",
            "[B": "DOWN",
            "[C": "RIGHT",
            "[D": "LEFT",
        }.get(sequence)
    return key.lower()
def get_direction(key):
    key_map = {
        "w": "UP",
        "a": "LEFT",
        "s": "DOWN",
        "d": "RIGHT",
    }
    if key in key_map:
        return key_map[key]
    if key in DIRECTIONS:
        return key
    return None
def move_snake(snake, direction):
    row_change, column_change = DIRECTIONS[direction]
    head_row, head_column = snake[0]
    new_head = (
        head_row + row_change,
        head_column + column_change,
    )
    snake.insert(0, new_head)
    return new_head
def collision_detected(snake, wrap=False):
    head_row, head_column = snake[0]
    if wrap:
        snake[0] = (head_row % ROWS, head_column % COLUMNS)
    elif not (0 <= head_row < ROWS and 0 <= head_column < COLUMNS):
        return True
    return snake[0] in snake[1:]
def choose_wrap_mode():
    while True:
        choice = input("\nEnable wrap-around walls? (y/n): ").strip().lower()
        if choice in ("y", "n"):
            return choice == "y"
        print("Please enter Y or N.")
def display_pause():
    print()
    print("GAME PAUSED")
    print("Press P to continue.")
def play_game(difficulty_name, base_speed, wrap=False):
    snake = list(INITIAL_SNAKE)
    direction = "RIGHT"
    food = create_food(snake)
    powerup = None
    powerup_type = None
    score = 0
    speed = base_speed
    slow_until = 0
    original_terminal_settings = setup_terminal()
    try:
        while True:
            clear_screen()
            display_title()
            print(f"Difficulty: {difficulty_name}")
            print()
            display_board(snake, food, score, powerup, powerup_type)
            key = read_key()
            if key == "q":
                return "quit", score
            if key == "p":
                display_pause()
                while True:
                    pause_key = read_key()
                    if pause_key == "p":
                        break
                    if pause_key == "q":
                        return "quit", score
                    time.sleep(PAUSE_POLL_INTERVAL)
            new_direction = get_direction(key)
            if (
                new_direction
                and new_direction != OPPOSITE_DIRECTIONS[direction]
            ):
                direction = new_direction
            move_snake(snake, direction)
            if collision_detected(snake, wrap):
                return "game_over", score
            if snake[0] == food:
                score += FOOD_SCORE
                food = create_food(snake)
                speed = max(MIN_SPEED, speed - SPEED_INCREMENT)
                if random.random() < POWERUP_CHANCE:
                    powerup = create_food(snake + [food])
                    powerup_type = random.choice(("bonus", "slow"))
            elif powerup and snake[0] == powerup:
                if powerup_type == "bonus":
                    score += BONUS_SCORE
                else:
                    slow_until = time.time() + SLOW_DURATION
                powerup = None
                powerup_type = None
            else:
                snake.pop()
            current_speed = speed * 1.5 if time.time() < slow_until else speed
            time.sleep(current_speed)
    finally:
        restore_terminal(original_terminal_settings)
def display_game_over(score, difficulty_name):
    clear_screen()
    display_title()
    print("=" * 52)
    print("                    GAME OVER")
    print("=" * 52)
    print()
    print(f"Difficulty : {difficulty_name}")
    print(f"Final Score: {score}")
    print()
def play_again():
    while True:
        choice = input("Play again? (Y/N): ").strip().lower()
        if choice in ("y", "n"):
            return choice == "y"
        print("Please enter Y or N.")
def main(record_result=None):
    while True:
        difficulty_name, base_speed = choose_difficulty()
        wrap = choose_wrap_mode()
        status, score = play_game(difficulty_name, base_speed, wrap)
        if record_result:
            record_result("snake", status, score)
        if status == "quit":
            clear_screen()
            print("Thanks for playing Snake.")
            return
        display_game_over(score, difficulty_name)
        if not play_again():
            print("\nThanks for playing Snake.")
            return
if __name__ == "__main__":
    main()
