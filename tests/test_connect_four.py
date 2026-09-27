import pytest
from engine.game import SessionConfig
from engine.result import GameResult
from engine.state import GameState
from games.connect_four import (
    COLUMNS,
    HARD,
    ConnectFourGame,
    check_winner,
    computer_move,
    create_board,
    find_immediate_move,
    _display_replay,
    _hint_move,
)
def test_setup_creates_v2_game_state():
    game = ConnectFourGame()
    config = SessionConfig(
        game="connect_four",
        difficulty="hard",
        mode="practice",
    )
    state = game.setup(config)
    assert isinstance(state, GameState)
    assert state.game == "connect_four"
    assert state.status == "ready"
    assert state.data["board"] == create_board()
    assert state.data["current_player"] == "X"
    assert state.data["player_mode"] == "computer"
def test_gravity_and_immediate_win_are_preserved():
    board = create_board()
    for _ in range(3):
        board[5 - _][0] = "O"
    assert find_immediate_move(board, "O") == 0
    assert computer_move(board, HARD) == 0
def test_hint_does_not_mutate_board():
    board = create_board()
    board[5][3] = "X"
    board[4][3] = "O"
    original = [row[:] for row in board]
    hint = _hint_move(board, HARD, "X")
    assert hint in range(COLUMNS)
    assert board == original
def test_replay_does_not_mutate_recorded_history():
    history = [
        {"player": "X", "column": 0},
        {"player": "O", "column": 1},
        {"player": "X", "column": 0},
    ]
    original = [dict(move) for move in history]
    _display_replay(history)
    assert history == original
def test_v2_play_returns_result_and_records_only_committed_moves(monkeypatch):
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
    assert result.game == "connect_four"
    assert result.outcome == "win"
    assert result.mode == "practice"
    assert result.moves == 7
    assert state.moves == 7
    assert state.status == "win"
    assert state.move_history == [
        {"player": "X", "column": 0},
        {"player": "O", "column": 1},
        {"player": "X", "column": 0},
        {"player": "O", "column": 1},
        {"player": "X", "column": 0},
        {"player": "O", "column": 1},
        {"player": "X", "column": 0},
    ]
def test_practice_mode_does_not_change_competitive_streak(monkeypatch):
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
def test_invalid_game_rejected_by_setup():
    game = ConnectFourGame()
    with pytest.raises(ValueError):
        game.setup(SessionConfig(game="tic_tac_toe"))
