import random
from engine.game import SessionConfig
from engine.result import GameResult
from engine.state import GameState
from engine.utils import display_title
STANDARD_CHOICES = {"1": "rock", "2": "paper", "3": "scissors"}
EXTENDED_CHOICES = {**STANDARD_CHOICES, "4": "lizard", "5": "spock"}
STANDARD_MOVES = list(STANDARD_CHOICES.values())
EXTENDED_MOVES = list(EXTENDED_CHOICES.values())
BEATS = {
    "rock": {"scissors", "lizard"},
    "paper": {"rock", "spock"},
    "scissors": {"paper", "lizard"},
    "lizard": {"paper", "spock"},
    "spock": {"rock", "scissors"},
}
# Unpredictable is the deliberately chosen Hard mapping; it is not an objective equivalence.
DIFFICULTY_PERSONALITY = {"easy": "balanced", "medium": "adaptive", "hard": "unpredictable"}
def get_player_choice(extended):
    choices = EXTENDED_CHOICES if extended else STANDARD_CHOICES
    print("\nChoose your move:")
    for key, move in choices.items():
        print(f"  {key}. {move.title()}")
    while True:
        choice = input("\nYour choice: ").strip()
        if choice in choices:
            return choices[choice]
        print(f"Invalid choice! Please choose 1-{len(choices)}.")
def get_round_winner(player, computer):
    if player == computer:
        return "draw"
    return "player" if computer in BEATS[player] else "computer"
def display_round_result(player, computer, result):
    print("\n" + "-" * 42)
    print(f"You      : {player.title()}")
    print(f"Computer : {computer.title()}")
    print("-" * 42)
    print({"player": "Result   : YOU WIN!", "computer": "Result   : COMPUTER WINS!", "draw": "Result   : DRAW!"}[result])
def choose_computer_move(history, moves, personality):
    if not history or personality == "balanced":
        return random.choice(moves)
    if personality == "adaptive":
        target = max(moves, key=history.count)
        if random.random() < 0.60:
            moves = [move for move in moves if target in BEATS[move]]
    elif random.random() < 0.30:
        target = history[-1]
        moves = [move for move in moves if target in BEATS[move]]
    return random.choice(moves)
class RockPaperScissorsGame:
    name = "Rock Paper Scissors"
    description = "Classic hand game with an optional Lizard & Spock variant"
    def __init__(self):
        self.win_streak = 0
        self.best_streak = 0
    def setup(self, config: SessionConfig) -> GameState:
        if config.game != "rock_paper_scissors":
            raise ValueError("RockPaperScissorsGame requires game='rock_paper_scissors'")
        if config.difficulty not in DIFFICULTY_PERSONALITY:
            raise ValueError(f"Unsupported RPS difficulty: {config.difficulty}")
        personality = config.options.get("personality", DIFFICULTY_PERSONALITY[config.difficulty])
        if personality not in {"balanced", "adaptive", "unpredictable"}:
            raise ValueError("Unsupported RPS personality")
        variant = config.options.get("variant", "standard")
        match_type = config.options.get("match_type", "single")
        rounds = config.options.get("rounds", 1)
        if variant not in {"standard", "extended"}:
            raise ValueError("variant must be 'standard' or 'extended'")
        if match_type not in {"single", "match"}:
            raise ValueError("match_type must be 'single' or 'match'")
        if match_type == "match" and (not isinstance(rounds, int) or not 2 <= rounds <= 10):
            raise ValueError("RPS rounds must be between 2 and 10")
        return GameState(
            game="rock_paper_scissors",
            data={
                "extended": variant == "extended",
                "personality": personality,
                "match_type": match_type,
                "rounds": rounds,
                "history": [],
                "player_score": 0,
                "computer_score": 0,
            },
        )
    def play(self, state: GameState, config: SessionConfig) -> GameResult:
        state.set_status("playing")
        data = state.data
        moves = EXTENDED_MOVES if data["extended"] else STANDARD_MOVES
        display_title("ROCK PAPER SCISSORS")
        print(f"Computer personality: {data['personality'].title()}")
        if data["extended"]:
            print("Variant: Lizard & Spock")
        for number in range(1, data["rounds"] + 1):
            if data["match_type"] == "match":
                print(f"\n{'=' * 42}\nROUND {number}/{data['rounds']}\n{'=' * 42}")
            player = get_player_choice(data["extended"])
            computer = choose_computer_move(data["history"], moves, data["personality"])
            data["history"].append(player)
            state.record_move({"player": player, "computer": computer})
            result = get_round_winner(player, computer)
            display_round_result(player, computer, result)
            if result == "player":
                data["player_score"] += 1
            elif result == "computer":
                data["computer_score"] += 1
            if data["match_type"] == "match":
                print(f"Score: You {data['player_score']} | Computer {data['computer_score']}")
        if data["player_score"] > data["computer_score"]:
            outcome = "win"
        elif data["computer_score"] > data["player_score"]:
            outcome = "loss"
        else:
            outcome = "draw"
        return self._finish(state, config, outcome)
    def _finish(self, state, config, outcome):
        data = state.data
        state.set_status(outcome)
        if config.is_competitive:
            if outcome == "win":
                self.win_streak += 1
                self.best_streak = max(self.best_streak, self.win_streak)
            elif outcome == "loss":
                self.win_streak = 0
        print("\n" + "=" * 42)
        print("MATCH RESULT" if data["match_type"] == "match" else "GAME RESULT")
        print("=" * 42)
        print(f"You: {data['player_score']} | Computer: {data['computer_score']}")
        score = {"win": 3, "draw": 1, "loss": 0}[outcome]
        return GameResult(
            game="rock_paper_scissors",
            outcome=outcome,
            difficulty=config.difficulty,
            mode=config.mode,
            score=score,
            moves=state.moves,
            metadata={
                "configuration": {
                    "personality": data["personality"],
                    "variant": "extended" if data["extended"] else "standard",
                    "match_type": data["match_type"],
                    "rounds": data["rounds"],
                },
                "player_score": data["player_score"],
                "computer_score": data["computer_score"],
                "win_streak": self.win_streak,
                "best_streak": self.best_streak,
            },
        )
def main():
    game = RockPaperScissorsGame()
    while True:
        display_title("ROCK PAPER SCISSORS")
        print("\n1. Standard\n2. Lizard & Spock")
        variant = input("Choose variant: ").strip()
        if variant not in {"1", "2"}:
            print("Invalid choice!")
            continue
        print("\n1. Single Game\n2. Best of...")
        match_type = input("Choose: ").strip()
        if match_type not in {"1", "2"}:
            print("Invalid choice!")
            continue
        rounds = 1
        if match_type == "2":
            try:
                rounds = int(input("Number of rounds (2-10): ").strip())
                if not 2 <= rounds <= 10:
                    raise ValueError
            except ValueError:
                print("Please choose a number from 2 to 10.")
                continue
        print("\n1. Easy\n2. Medium\n3. Hard")
        difficulty = {"1": "easy", "2": "medium", "3": "hard"}.get(input("Choose difficulty: ").strip())
        if not difficulty:
            print("Invalid choice!")
            continue
        config = SessionConfig(
            game="rock_paper_scissors",
            difficulty=difficulty,
            options={
                "variant": "extended" if variant == "2" else "standard",
                "match_type": "match" if match_type == "2" else "single",
                "rounds": rounds,
            },
        )
        game.play(game.setup(config), config)
        if input("\nPlay again? (y/n): ").strip().lower() != "y":
            print("\nThanks for playing!")
            break
if __name__ == "__main__":
    main()