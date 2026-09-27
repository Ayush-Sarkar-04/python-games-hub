import pytest
from engine.achievements import AchievementStore
from engine.profiles import Profile, ProfileStore
from engine.settings import SettingsStore
from engine.statistics import StatisticsStore


def test_profile_store_round_trip(tmp_path):
    store = ProfileStore(tmp_path / "profile.json")
    store.save(Profile(name="Player", level=2, xp=10))
    assert store.load() == Profile(name="Player", level=2, xp=10)


def test_statistics_store_handles_game_specific_stats(tmp_path):
    store = StatisticsStore(tmp_path / "statistics.json")
    data = {"snake": {"games": 1, "best_score": 90}}
    store.save(data)
    assert store.load() == data


def test_achievement_store_round_trip(tmp_path):
    store = AchievementStore(tmp_path / "achievements.json")
    data = {"first_win": {"unlocked": True, "unlocked_at": "2026-09-27T00:00:00"}}
    store.save(data)
    assert store.load() == data


def test_settings_store_merges_defaults(tmp_path):
    store = SettingsStore(tmp_path / "settings.json")
    store.save({"banner_style": "classic"})
    settings = store.load()
    assert settings["banner_style"] == "classic"
    assert settings["auto_suggest_difficulty"] is True


def test_achievement_definition_and_evaluator_consume_game_result():
    from engine.achievements import AchievementDefinition, AchievementEvaluator
    from engine.result import GameResult

    definition = AchievementDefinition(
        id="first_win",
        name="First Win",
        description="Win a competitive game.",
    )
    evaluator = AchievementEvaluator(
        definitions=(definition,),
        rules={"first_win": lambda result: result.mode == "competitive" and result.outcome == "win"},
    )
    result = GameResult(
        game="tic_tac_toe",
        outcome="win",
        difficulty="easy",
        mode="competitive",
    )

    assert evaluator.evaluate(result) == ["first_win"]


def test_achievement_definition_requires_schema_fields():
    from engine.achievements import AchievementDefinition

    with pytest.raises(ValueError):
        AchievementDefinition(id="", name="First Win", description="Win a game.")


def test_settings_store_rejects_invalid_field_types(tmp_path):
    store = SettingsStore(tmp_path / "settings.json")
    store.save({"banner_style": 12345, "auto_suggest_difficulty": "yes"})
    settings = store.load()
    assert settings == {
        "banner_style": "default",
        "auto_suggest_difficulty": True,
    }


def test_tic_tac_toe_result_reaches_achievement_evaluator(monkeypatch):
    from engine.achievements import BOARD_GAME_ACHIEVEMENT_EVALUATOR
    from engine.game import SessionConfig
    from games.tic_tac_toe import TicTacToeGame

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
    assert BOARD_GAME_ACHIEVEMENT_EVALUATOR.evaluate(result) == []


def test_connect_four_achievement_evaluator_accepts_competitive_result():
    from engine.achievements import BOARD_GAME_ACHIEVEMENT_EVALUATOR
    from engine.result import GameResult

    result = GameResult(
        game="connect_four",
        outcome="win",
        difficulty="custom",
        mode="competitive",
        metadata={"win_streak": 10, "configuration": {"custom_settings": {"minimax_depth": 6}}},
    )
    assert set(BOARD_GAME_ACHIEVEMENT_EVALUATOR.evaluate(result)) == {
        "first_victory",
        "connect_four_10_win_streak",
    }


def test_achievement_evaluator_does_not_repeat_unlocked_achievement():
    from engine.achievements import BOARD_GAME_ACHIEVEMENT_EVALUATOR
    from engine.result import GameResult

    result = GameResult(
        game="tic_tac_toe",
        outcome="win",
        difficulty="hard",
        mode="competitive",
    )
    assert BOARD_GAME_ACHIEVEMENT_EVALUATOR.evaluate(result, {"first_victory"}) == []


def test_commit3_statistics_aggregate_competitive_results_only():
    from engine.result import GameResult
    from engine.statistics import update_statistics

    statistics = {}
    rps_result = GameResult(
        game="rock_paper_scissors",
        outcome="win",
        difficulty="hard",
        mode="competitive",
        score=3,
        metadata={
            "configuration": {
                "personality": "unpredictable",
                "variant": "extended",
                "match_type": "match",
            },
            "win_streak": 2,
            "best_streak": 4,
        },
    )
    practice_result = GameResult(
        game="hangman",
        outcome="win",
        difficulty="easy",
        mode="practice",
        metadata={"mistakes": 0, "win_streak": 0, "best_streak": 0},
    )

    statistics = update_statistics(statistics, rps_result)
    statistics = update_statistics(statistics, practice_result)

    assert statistics["rock_paper_scissors"] == {
        "matches": 1,
        "wins": 1,
        "win_streak": 2,
        "best_streak": 4,
        "results_by_personality": {
            "unpredictable": {"wins": 1},
        },
        "lizard_spock_matches": 1,
    }
    assert "hangman" not in statistics


def test_commit3_statistics_track_hangman_and_word_scramble_records():
    from engine.result import GameResult
    from engine.statistics import update_statistics

    statistics = {}
    statistics = update_statistics(
        statistics,
        GameResult(
            game="hangman",
            outcome="win",
            difficulty="medium",
            mode="competitive",
            metadata={"mistakes": 2, "win_streak": 1, "best_streak": 1},
        ),
    )
    statistics = update_statistics(
        statistics,
        GameResult(
            game="hangman",
            outcome="win",
            difficulty="hard",
            mode="competitive",
            metadata={"mistakes": 0, "win_streak": 2, "best_streak": 2},
        ),
    )
    statistics = update_statistics(
        statistics,
        GameResult(
            game="word_scramble",
            outcome="win",
            difficulty="easy",
            mode="competitive",
            score=3,
            metadata={"attempts": 1, "win_streak": 1, "best_streak": 1},
        ),
    )
    statistics = update_statistics(
        statistics,
        GameResult(
            game="word_scramble",
            outcome="win",
            difficulty="hard",
            mode="competitive",
            score=1,
            metadata={"attempts": 3, "win_streak": 2, "best_streak": 2},
        ),
    )

    assert statistics["hangman"]["games"] == 2
    assert statistics["hangman"]["wins"] == 2
    assert statistics["hangman"]["fewest_mistakes"] == 0
    assert statistics["word_scramble"]["rounds"] == 2
    assert statistics["word_scramble"]["wins"] == 2
    assert statistics["word_scramble"]["fewest_attempts"] == 1


def test_commit3_achievement_triggers_from_real_result_shapes():
    from engine.achievements import NON_REAL_TIME_ACHIEVEMENT_EVALUATOR
    from engine.result import GameResult

    hangman = GameResult(
        game="hangman",
        outcome="win",
        difficulty="easy",
        mode="competitive",
        metadata={"mistakes": 0},
    )
    rps = GameResult(
        game="rock_paper_scissors",
        outcome="win",
        difficulty="hard",
        mode="competitive",
        metadata={"configuration": {"variant": "extended"}},
    )
    scramble = GameResult(
        game="word_scramble",
        outcome="win",
        difficulty="easy",
        mode="competitive",
        score=3,
        metadata={"attempts": 1},
    )

    assert NON_REAL_TIME_ACHIEVEMENT_EVALUATOR.evaluate(hangman) == ["perfect_hangman"]
    assert NON_REAL_TIME_ACHIEVEMENT_EVALUATOR.evaluate(rps) == ["rps_lizard_spock_win"]
    assert NON_REAL_TIME_ACHIEVEMENT_EVALUATOR.evaluate(scramble) == ["word_scramble_first_try"]


def test_commit3_achievements_exclude_practice_results():
    from engine.achievements import NON_REAL_TIME_ACHIEVEMENT_EVALUATOR
    from engine.result import GameResult

    result = GameResult(
        game="word_scramble",
        outcome="win",
        difficulty="easy",
        mode="practice",
        metadata={"attempts": 1},
    )

    assert NON_REAL_TIME_ACHIEVEMENT_EVALUATOR.evaluate(result) == []
