"""Tests for the Typing Test and Mastermind games."""

from engine.game import SessionConfig
from engine.result import GameResult
from engine.state import GameState


def test_typing_metrics_perfect_text():
    from games.typing_test import calculate_metrics

    metrics = calculate_metrics("hello world", "hello world", 60)
    assert metrics["correct_characters"] == 11
    assert metrics["accuracy"] == 100.0
    assert metrics["wpm"] == 2.2
    assert metrics["score"] == 2


def test_typing_metrics_penalize_incorrect_characters():
    from games.typing_test import calculate_metrics

    metrics = calculate_metrics("abcdef", "abcxef", 30)
    assert metrics["correct_characters"] == 5
    assert metrics["accuracy"] == 83.33
    assert metrics["wpm"] == 2.0
    assert metrics["score"] == 2


def test_typing_setup_uses_selected_difficulty_and_text():
    from games.typing_test import TypingTestGame

    config = SessionConfig(
        game="typing_test",
        difficulty="hard",
        mode="practice",
        options={"text": "Reliable typing under pressure."},
    )
    state = TypingTestGame().setup(config)
    assert isinstance(state, GameState)
    assert state.data["text"] == "Reliable typing under pressure."
    assert state.data["duration"] == 30


def test_typing_play_returns_metrics(monkeypatch):
    from games.typing_test import TypingTestGame

    config = SessionConfig(
        game="typing_test",
        difficulty="easy",
        mode="practice",
        options={"text": "hello"},
    )
    monkeypatch.setattr("games.typing_test.time.monotonic", lambda: 10.0)
    answers = iter(["hello"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    result = TypingTestGame().play(TypingTestGame().setup(config), config)
    assert isinstance(result, GameResult)
    assert result.outcome == "finished"
    assert result.metadata["accuracy"] == 100.0


def test_mastermind_generate_code_matches_difficulty():
    from games.mastermind import DIFFICULTIES, generate_code

    for difficulty, settings in DIFFICULTIES.items():
        code = generate_code(difficulty)
        assert len(code) == settings["length"]
        assert len(set(code)) == len(code)
        assert set(code).issubset(set(settings["colors"]))


def test_mastermind_evaluate_guess_counts_exact_and_misplaced():
    from games.mastermind import evaluate_guess

    code = ("R", "G", "B", "Y")
    assert evaluate_guess(code, ("R", "B", "Y", "G")) == (1, 3)
    assert evaluate_guess(code, code) == (4, 0)


def test_mastermind_rejects_invalid_guess():
    from games.mastermind import validate_guess

    try:
        validate_guess("R G B", "easy")
    except ValueError as exc:
        assert "exactly 4" in str(exc)
    else:
        raise AssertionError("Expected invalid length to be rejected")

    try:
        validate_guess("R R B Y", "easy")
    except ValueError as exc:
        assert "repeat" in str(exc)
    else:
        raise AssertionError("Expected repeated colors to be rejected")


def test_mastermind_setup_accepts_deterministic_code():
    from games.mastermind import MastermindGame

    config = SessionConfig(
        game="mastermind",
        difficulty="easy",
        mode="practice",
        options={"code": ("R", "G", "B", "Y")},
    )
    state = MastermindGame().setup(config)
    assert state.data["code"] == ("R", "G", "B", "Y")
    assert state.data["attempts"] == 0


def test_mastermind_play_can_win_on_first_guess(monkeypatch):
    from games.mastermind import MastermindGame

    config = SessionConfig(
        game="mastermind",
        difficulty="easy",
        mode="practice",
        options={"code": ("R", "G", "B", "Y")},
    )
    game = MastermindGame()
    state = game.setup(config)
    monkeypatch.setattr("builtins.input", lambda _: "R G B Y")
    result = game.play(state, config)
    assert result.outcome == "win"
    assert result.score == 100
    assert result.moves == 1
    assert result.metadata["attempts"] == 1


def test_mastermind_play_loses_after_max_attempts(monkeypatch):
    from games.mastermind import MastermindGame

    config = SessionConfig(
        game="mastermind",
        difficulty="easy",
        mode="practice",
        options={"code": ("R", "G", "B", "Y")},
    )
    game = MastermindGame()
    state = game.setup(config)
    answers = iter(["R G Y B"] * 10)
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    result = game.play(state, config)
    assert result.outcome == "loss"
    assert result.score == 0
    assert result.moves == 10
