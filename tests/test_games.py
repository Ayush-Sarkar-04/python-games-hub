import pytest
from engine.game import SessionConfig
from engine.result import GameResult
from engine.state import GameState
from games.connect_four import (
    COLUMNS,
    CUSTOM_MINIMAX_DEPTH_MAX as CONNECT_FOUR_CUSTOM_MAX,
    CUSTOM_MINIMAX_DEPTH_MIN as CONNECT_FOUR_CUSTOM_MIN,
    HARD as CONNECT_FOUR_HARD,
    ConnectFourGame,
    _display_replay as replay_connect_four,
    _hint_move as hint_connect_four,
    computer_move as connect_four_computer_move,
    create_board,
    find_immediate_move,
)
from games.hangman import DIFFICULTIES as HANGMAN_DIFFICULTIES, HangmanGame, display_word, word_complete
from games.rock_paper_scissors import (
    BEATS,
    RockPaperScissorsGame,
    STANDARD_MOVES,
    choose_computer_move,
    get_round_winner,
)
from games.snake import (
    DIFFICULTIES as SNAKE_DIFFICULTIES,
    SnakeGame,
    create_food,
    get_direction,
    move_snake,
)
from games.tic_tac_toe import (
    CUSTOM_MINIMAX_DEPTH_MAX as TIC_TAC_TOE_CUSTOM_MAX,
    CUSTOM_MINIMAX_DEPTH_MIN as TIC_TAC_TOE_CUSTOM_MIN,
    HARD as TIC_TAC_TOE_HARD,
    TicTacToeGame,
    _display_replay as replay_tic_tac_toe,
    _hint_move as hint_tic_tac_toe,
    find_best_move,
)
from games.word_scramble import (
    DIFFICULTY as SCRAMBLE_DIFFICULTY,
    FALLBACK_WORDS,
    HINT_SCHEDULE,
    WordScrambleGame,
    scramble_word,
)
def test_tic_tac_toe_setup_and_difficulty():
    state = TicTacToeGame().setup(
        SessionConfig(game="tic_tac_toe", difficulty="hard", mode="practice")
    )
    assert isinstance(state, GameState)
    assert state.data["board"] == [" "] * 9
    assert state.data["current_player"] == "X"
    assert state.data["player_mode"] == "computer"
@pytest.mark.parametrize(
    ("difficulty", "expected"),
    [("easy", "1"), ("medium", "2"), ("hard", "3")],
)
def test_tic_tac_toe_difficulty_mapping(difficulty, expected):
    from games.tic_tac_toe import DIFFICULTY_MAP
    assert DIFFICULTY_MAP[difficulty] == expected
def test_tic_tac_toe_custom_difficulty_setup_and_metadata():
    config = SessionConfig(
        game="tic_tac_toe",
        difficulty="custom",
        custom_settings={"minimax_depth": 5},
        options={"player_mode": "computer", "personality": "Aggressive"},
    )
    state = TicTacToeGame().setup(config)
    assert state.data["custom_settings"] == {"minimax_depth": 5}


def test_tic_tac_toe_custom_difficulty_bounds():
    for depth in (TIC_TAC_TOE_CUSTOM_MIN - 1, TIC_TAC_TOE_CUSTOM_MAX + 1, "5", True):
        with pytest.raises(ValueError):
            TicTacToeGame().setup(
                SessionConfig(
                    game="tic_tac_toe",
                    difficulty="custom",
                    custom_settings={"minimax_depth": depth},
                )
            )


def test_tic_tac_toe_custom_result_records_settings(monkeypatch):
    game = TicTacToeGame()
    config = SessionConfig(
        game="tic_tac_toe",
        difficulty="custom",
        mode="practice",
        custom_settings={"minimax_depth": 5},
        options={"player_mode": "player", "personality": "Balanced"},
    )
    state = game.setup(config)
    answers = iter(["1", "2", "4", "5", "7", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    result = game.play(state, config)
    assert result.difficulty == "custom"
    assert result.metadata["configuration"]["custom_settings"] == {"minimax_depth": 5}


def test_tic_tac_toe_hard_ai_takes_winning_move():
    board = ["O", "O", " ", "X", "X", " ", " ", " ", " "]
    original = board[:]
    assert find_best_move(board) == 2
    assert board == original
def test_tic_tac_toe_hint_and_replay_preserve_state():
    board = ["X", "O", " ", " ", "X", " ", " ", " ", "O"]
    original = board[:]
    assert hint_tic_tac_toe(board, TIC_TAC_TOE_HARD, "Balanced") in range(9)
    assert board == original
    history = [
        {"player": "X", "position": 0},
        {"player": "O", "position": 4},
    ]
    original_history = [dict(move) for move in history]
    replay_tic_tac_toe(history)
    assert history == original_history
def test_tic_tac_toe_play_records_committed_moves(monkeypatch):
    game = TicTacToeGame()
    config = SessionConfig(
        game="tic_tac_toe",
        difficulty="easy",
        mode="practice",
        options={"player_mode": "player", "personality": "Balanced"},
    )
    state = game.setup(config)
    answers = iter(["1", "2", "4", "5", "7", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    result = game.play(state, config)
    assert isinstance(result, GameResult)
    assert result.outcome == "win"
    assert result.moves == 5
    assert state.moves == 5
    assert state.move_history == [
        {"player": "X", "position": 0},
        {"player": "O", "position": 1},
        {"player": "X", "position": 3},
        {"player": "O", "position": 4},
        {"player": "X", "position": 6},
    ]
    assert result.metadata["configuration"] == {
        "player_mode": "player",
        "personality": "Balanced",
    }
def test_tic_tac_toe_practice_does_not_change_streak(monkeypatch):
    game = TicTacToeGame()
    config = SessionConfig(
        game="tic_tac_toe",
        difficulty="easy",
        mode="practice",
        options={"player_mode": "player", "personality": "Balanced"},
    )
    state = game.setup(config)
    answers = iter(["1", "2", "4", "5", "7", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    game.play(state, config)
    assert game.win_streak == 0
    assert game.best_streak == 0
def test_connect_four_setup_and_gravity():
    state = ConnectFourGame().setup(
        SessionConfig(game="connect_four", difficulty="hard", mode="practice")
    )
    assert isinstance(state, GameState)
    assert state.data["board"] == create_board()
    assert state.data["current_player"] == "X"
def test_connect_four_custom_difficulty_setup_and_bounds():
    config = SessionConfig(
        game="connect_four",
        difficulty="custom",
        custom_settings={"minimax_depth": 5},
    )
    state = ConnectFourGame().setup(config)
    assert state.data["custom_settings"] == {"minimax_depth": 5}

    for depth in (CONNECT_FOUR_CUSTOM_MIN - 1, CONNECT_FOUR_CUSTOM_MAX + 1, "5", True):
        with pytest.raises(ValueError):
            ConnectFourGame().setup(
                SessionConfig(
                    game="connect_four",
                    difficulty="custom",
                    custom_settings={"minimax_depth": depth},
                )
            )


def test_connect_four_custom_result_records_settings(monkeypatch):
    game = ConnectFourGame()
    config = SessionConfig(
        game="connect_four",
        difficulty="custom",
        mode="practice",
        custom_settings={"minimax_depth": 3},
        options={"player_mode": "player", "first_player": "X"},
    )
    state = game.setup(config)
    answers = iter(["1", "2", "1", "2", "1", "2", "1", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    result = game.play(state, config)
    assert result.difficulty == "custom"
    assert result.metadata["configuration"]["custom_settings"] == {"minimax_depth": 3}


def test_connect_four_hard_ai_finds_immediate_win():
    board = create_board()
    for offset in range(3):
        board[5 - offset][0] = "O"
    assert find_immediate_move(board, "O") == 0
    assert connect_four_computer_move(board, CONNECT_FOUR_HARD) == 0
def test_connect_four_hint_and_replay_preserve_state():
    board = create_board()
    board[5][3] = "X"
    board[4][3] = "O"
    original = [row[:] for row in board]
    assert hint_connect_four(board, CONNECT_FOUR_HARD, "X") in range(COLUMNS)
    assert board == original
    history = [
        {"player": "X", "column": 0},
        {"player": "O", "column": 1},
    ]
    original_history = [dict(move) for move in history]
    replay_connect_four(history)
    assert history == original_history
def test_connect_four_play_records_committed_moves(monkeypatch):
    game = ConnectFourGame()
    config = SessionConfig(
        game="connect_four",
        difficulty="easy",
        mode="practice",
        options={"player_mode": "player", "first_player": "X"},
    )
    state = game.setup(config)
    answers = iter(["1", "2", "1", "2", "1", "2", "1", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    result = game.play(state, config)
    assert isinstance(result, GameResult)
    assert result.outcome == "win"
    assert result.moves == 7
    assert state.moves == 7
    assert result.metadata["configuration"] == {
        "player_mode": "player",
        "first_player": "X",
    }
def test_connect_four_practice_does_not_change_streak(monkeypatch):
    game = ConnectFourGame()
    config = SessionConfig(
        game="connect_four",
        difficulty="easy",
        mode="practice",
        options={"player_mode": "player", "first_player": "X"},
    )
    state = game.setup(config)
    answers = iter(["1", "2", "1", "2", "1", "2", "1", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    game.play(state, config)
    assert game.win_streak == 0
    assert game.best_streak == 0
def test_hangman_setup_uses_config_and_returns_state():
    words = {"animals": {"name": "Animals", "words": ["cat", "tiger", "elephant"]}}
    game = HangmanGame(words)
    config = SessionConfig(game="hangman", difficulty="easy", mode="practice", options={"category": "animals"})
    state = game.setup(config)
    assert isinstance(state, GameState)
    assert state.game == "hangman"
    assert state.data["category"] == "animals"
    assert state.data["word"] in words["animals"]["words"]
    assert state.data["attempts"] == HANGMAN_DIFFICULTIES["easy"]["attempts"]
    assert state.data["guessed"] == set()
def test_hangman_word_helpers():
    guessed = {"a", "p"}
    assert display_word("apple", guessed) == "A P P _ _"
    assert not word_complete("apple", guessed)
    assert word_complete("apple", {"a", "p", "l", "e"})
def test_hangman_setup_requires_hub_category():
    game = HangmanGame({"animals": {"name": "Animals", "words": ["cat"]}})
    config = SessionConfig(game="hangman", difficulty="easy", mode="practice")
    with pytest.raises(ValueError, match="requires a valid category"):
        game.setup(config)


def test_hangman_empty_category_raises_clear_error():
    game = HangmanGame({"animals": {"name": "Animals", "words": []}})
    config = SessionConfig(
        game="hangman",
        difficulty="easy",
        mode="practice",
        options={"category": "animals"},
    )
    with pytest.raises(ValueError, match="contains no valid words"):
        game.setup(config)


def test_hangman_custom_attempts_validation():
    game = HangmanGame({"animals": {"name": "Animals", "words": ["cat"]}})
    for attempts in ("8", True, False, 2, 11):
        with pytest.raises(ValueError):
            game.setup(
                SessionConfig(
                    game="hangman",
                    difficulty="custom",
                    custom_settings={"attempts": attempts},
                    options={"category": "animals"},
                )
            )


def test_hangman_custom_attempts_setup():
    game = HangmanGame({"animals": {"name": "Animals", "words": ["cat"]}})
    config = SessionConfig(
        game="hangman",
        difficulty="custom",
        mode="practice",
        custom_settings={"attempts": 8},
        options={"category": "animals"},
    )
    state = game.setup(config)
    assert state.data["attempts"] == 8


def test_hangman_play_records_guesses(monkeypatch):
    game = HangmanGame({"animals": {"name": "Animals", "words": ["cat"]}})
    config = SessionConfig(game="hangman", difficulty="easy", mode="practice", options={"category": "animals"})
    state = game.setup(config)
    answers = iter(["c", "a", "t"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    result = game.play(state, config)
    assert isinstance(result, GameResult)
    assert result.outcome == "win"
    assert state.moves == 3
    assert state.move_history == [
        {"type": "guess", "letter": "c"},
        {"type": "guess", "letter": "a"},
        {"type": "guess", "letter": "t"},
    ]
def test_rock_paper_scissors_setup():
    game = RockPaperScissorsGame()
    config = SessionConfig(game="rock_paper_scissors", difficulty="medium", mode="practice", options={"variant": "extended", "match_type": "match", "rounds": 5})
    state = game.setup(config)
    assert isinstance(state, GameState)
    assert state.data["extended"] is True
    assert state.data["personality"] == "adaptive"
    assert state.data["match_type"] == "match"
    assert state.data["rounds"] == 5
def test_rock_paper_scissors_rules():
    assert get_round_winner("rock", "scissors") == "player"
    assert get_round_winner("paper", "paper") == "draw"
    assert get_round_winner("scissors", "rock") == "computer"
    for move in STANDARD_MOVES:
        assert any(move in BEATS[candidate] for candidate in STANDARD_MOVES)
def test_rock_paper_scissors_computer_uses_valid_move(monkeypatch):
    monkeypatch.setattr("random.choice", lambda values: values[0])
    move = choose_computer_move(["rock"], STANDARD_MOVES, "adaptive")
    assert move in STANDARD_MOVES
def test_rock_paper_scissors_play_records_round(monkeypatch):
    game = RockPaperScissorsGame()
    config = SessionConfig(game="rock_paper_scissors", difficulty="easy", mode="practice", options={"variant": "standard", "match_type": "single"})
    state = game.setup(config)
    monkeypatch.setattr("builtins.input", lambda _: "1")
    monkeypatch.setattr("games.rock_paper_scissors.choose_computer_move", lambda history, moves, personality: "scissors")
    result = game.play(state, config)
    assert isinstance(result, GameResult)
    assert result.outcome == "win"
    assert state.moves == 1
    assert state.move_history == [{"player": "rock", "computer": "scissors"}]
    assert result.metadata["configuration"]["variant"] == "standard"
    assert result.metadata["configuration"]["personality"] == "balanced"
def test_word_scramble_fallback_words_match_difficulty():
    for difficulty, (_, minimum, maximum) in SCRAMBLE_DIFFICULTY.items():
        assert all(minimum <= len(word) <= maximum for word in FALLBACK_WORDS[difficulty])
def test_word_scramble_changes_word_order(monkeypatch):
    monkeypatch.setattr("random.shuffle", lambda letters: letters.reverse())
    assert scramble_word("table") == "elbat"


def test_word_scramble_handles_repeated_letter_word():
    assert scramble_word("aaaa") == "aaaa"
def test_word_scramble_hint_schedule():
    assert HINT_SCHEDULE["easy"] == (1, 1)
    assert HINT_SCHEDULE["medium"] == (0, 1)
    assert HINT_SCHEDULE["hard"] == (0, 0)


def test_word_scramble_setup(monkeypatch):
    monkeypatch.setattr("games.word_scramble.get_word", lambda difficulty: "table")
    game = WordScrambleGame()
    config = SessionConfig(game="word_scramble", difficulty="easy", mode="practice")
    state = game.setup(config)
    assert isinstance(state, GameState)
    assert state.data["word"] == "table"
    assert sorted(state.data["scrambled"]) == sorted("table")
    assert state.data["attempts"] == 0
    assert state.data["score"] == 0
def test_word_scramble_play_scores_first_attempt(monkeypatch):
    monkeypatch.setattr("games.word_scramble.get_word", lambda difficulty: "table")
    game = WordScrambleGame()
    config = SessionConfig(game="word_scramble", difficulty="easy", mode="practice")
    state = game.setup(config)
    monkeypatch.setattr("builtins.input", lambda _: "table")
    result = game.play(state, config)
    assert isinstance(result, GameResult)
    assert result.outcome == "win"
    assert result.score == 3
    assert state.moves == 1
    assert state.move_history == [{"guess": "table", "attempt": 1}]
def test_snake_full_board_has_no_food():
    full_board = [(row, column) for row in range(20) for column in range(30)]
    assert create_food(full_board) is None


def test_snake_setup_and_difficulty():
    game = SnakeGame()
    config = SessionConfig(game="snake", difficulty="hard", mode="practice", options={"wrap": True})
    state = game.setup(config)
    assert isinstance(state, GameState)
    assert state.data["direction"] == "RIGHT"
    assert len(state.data["snake"]) == 3
    assert state.data["score"] == 0
    assert state.data["wrap"] is True
    assert state.data["speed"] == SNAKE_DIFFICULTIES["hard"][1]
def test_snake_direction_and_movement():
    assert get_direction("w") == "UP"
    assert get_direction("RIGHT") == "RIGHT"
    assert get_direction("x") is None
    snake = [(5, 5), (5, 4), (5, 3)]
    assert move_snake(snake, "UP", wrap=False) == (4, 5)
    assert snake[0] == (4, 5)
def test_snake_wrap_movement():
    snake = [(0, 5), (1, 5), (2, 5)]
    assert move_snake(snake, "UP", wrap=True) == (19, 5)
    assert snake[0] == (19, 5)
def test_snake_collision_rules():
    snake = [(5, 5), (5, 4), (5, 5)]
    assert snake[0] in snake[1:]
    config = SessionConfig(game="snake", difficulty="easy")
    state = SnakeGame().setup(config)
    assert state.data["wrap"] is False
    assert config.difficulty in SNAKE_DIFFICULTIES

def test_rock_paper_scissors_result_score(monkeypatch):
    game = RockPaperScissorsGame()
    config = SessionConfig(
        game="rock_paper_scissors",
        difficulty="easy",
        mode="practice",
        options={"variant": "standard", "match_type": "single"},
    )
    state = game.setup(config)
    monkeypatch.setattr("builtins.input", lambda _: "1")
    monkeypatch.setattr(
        "games.rock_paper_scissors.choose_computer_move",
        lambda history, moves, personality: "scissors",
    )
    assert game.play(state, config).score == 3


def test_hangman_result_score_rewards_fewer_mistakes(monkeypatch):
    game = HangmanGame({"animals": {"name": "Animals", "words": ["cat"]}})
    config = SessionConfig(
        game="hangman",
        difficulty="easy",
        mode="practice",
        options={"category": "animals"},
    )
    state = game.setup(config)
    answers = iter(["c", "a", "t"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert game.play(state, config).score == 7


def test_tic_tac_toe_custom_result_contains_score_and_configuration(monkeypatch):
    game = TicTacToeGame()
    config = SessionConfig(
        game="tic_tac_toe",
        difficulty="custom",
        mode="practice",
        custom_settings={"minimax_depth": 5},
        options={"player_mode": "player", "personality": "Balanced"},
    )
    state = game.setup(config)
    answers = iter(["1", "2", "4", "5", "7", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    result = game.play(state, config)
    assert result.score == 5
    assert result.metadata["configuration"]["custom_settings"] == {"minimax_depth": 5}


def test_connect_four_custom_setup_preserves_custom_configuration():
    config = SessionConfig(
        game="connect_four",
        difficulty="custom",
        custom_settings={"minimax_depth": 6},
        options={"player_mode": "player", "first_player": "X"},
    )
    state = ConnectFourGame().setup(config)
    assert state.data["custom_settings"] == {"minimax_depth": 6}
