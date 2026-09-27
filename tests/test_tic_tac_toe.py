import pytest
from engine.game import SessionConfig
from engine.result import GameResult
from engine.state import GameState
from games.tic_tac_toe import (
    EASY,
    HARD,
    MEDIUM,
    TicTacToeGame,
    _display_replay,
    _hint_move,
    find_best_move,
)
def test_setup_creates_v2_game_state():
    game = TicTacToeGame()
    config = SessionConfig(
        game="tic_tac_toe",
        difficulty="hard",
        mode="practice",
    )
    state = game.setup(config)
    assert isinstance(state, GameState)
    assert state.game == "tic_tac_toe"
    assert state.status == "ready"
    assert state.data["board"] == [" "] * 9
    assert state.data["current_player"] == "X"
    assert state.data["player_mode"] == "computer"
    assert state.data["personality"] == "Balanced"
@pytest.mark.parametrize(
    ("difficulty", "expected"),
    [
        ("easy", EASY),
        ("medium", MEDIUM),
        ("hard", HARD),
    ],
)
def test_hub_difficulty_maps_to_existing_ttt_difficulty(
    difficulty, expected
):
    assert {
        "easy": EASY,
        "medium": MEDIUM,
        "hard": HARD,
    }[difficulty] == expected
def test_hard_ai_takes_immediate_winning_move():
    board = ["O", "O", " ", "X", "X", " ", " ", " ", " "]
    original = list(board)
    assert find_best_move(board) == 2
    assert board == original
def test_ai_hint_does_not_mutate_board():
    board = ["X", "O", " ", " ", "X", " ", " ", " ", "O"]
    original = list(board)
    hint = _hint_move(board, HARD, "Balanced")
    assert hint in range(9)
    assert board == original
def test_replay_does_not_mutate_recorded_history():
    history = [
        {"player": "X", "position": 0},
        {"player": "O", "position": 4},
        {"player": "X", "position": 1},
    ]
    original = [dict(move) for move in history]
    _display_replay(history)
    assert history == original
def test_v2_play_returns_game_result_and_records_committed_moves(monkeypatch):
    game = TicTacToeGame()
    config = SessionConfig(
        game="tic_tac_toe",
        difficulty="easy",
        mode="practice",
        options={
            "player_mode": "player",
            "personality": "Balanced",
        },
    )
    state = game.setup(config)
    answers = iter([
        "1",
        "2",
        "4",
        "5",
        "7",
        "n",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    result = game.play(state, config)
    assert isinstance(result, GameResult)
    assert result.game == "tic_tac_toe"
    assert result.outcome == "win"
    assert result.mode == "practice"
    assert result.moves == 5
    assert state.moves == 5
    assert state.status == "win"
    assert state.move_history == [
        {"player": "X", "position": 0},
        {"player": "O", "position": 1},
        {"player": "X", "position": 3},
        {"player": "O", "position": 4},
        {"player": "X", "position": 6},
    ]
def test_practice_mode_does_not_change_competitive_streak(monkeypatch):
    game = TicTacToeGame()
    config = SessionConfig(
        game="tic_tac_toe",
        difficulty="easy",
        mode="practice",
        options={
            "player_mode": "player",
            "personality": "Balanced",
        },
    )
    state = game.setup(config)
    answers = iter(["1", "2", "4", "5", "7", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    game.play(state, config)
    assert game.win_streak == 0
    assert game.best_streak == 0
def test_invalid_game_rejected_by_setup():
    game = TicTacToeGame()
    with pytest.raises(ValueError):
        game.setup(SessionConfig(game="connect_four"))