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

    assert statistics["rock_paper_scissors"]["matches"] == 1
    assert statistics["rock_paper_scissors"]["wins"] == 1
    assert statistics["rock_paper_scissors"]["win_streak"] == 2
    assert statistics["rock_paper_scissors"]["best_streak"] == 4
    assert statistics["rock_paper_scissors"]["results_by_personality"] == {
        "unpredictable": {"wins": 1},
    }
    assert statistics["rock_paper_scissors"]["lizard_spock_matches"] == 1
    assert statistics["rock_paper_scissors"]["recent_results"] == [
        {"difficulty": "hard", "outcome": "win", "score": 3}
    ]
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


def test_statistics_cover_board_games_and_snake():
    from engine.result import GameResult
    from engine.statistics import update_statistics

    stats = {}
    for game in ("tic_tac_toe", "connect_four"):
        stats = update_statistics(
            stats,
            GameResult(game=game, outcome="win", difficulty="hard", mode="competitive", score=3, moves=5),
        )
    stats = update_statistics(
        stats,
        GameResult(game="snake", outcome="game_over", difficulty="medium", mode="competitive", score=240, moves=20),
    )

    assert stats["tic_tac_toe"]["wins"] == 1
    assert stats["connect_four"]["wins"] == 1
    assert stats["snake"]["best_score"] == 240
    assert stats["snake"]["top_runs"][0]["score"] == 240


def test_difficulty_suggestion_is_advisory():
    from engine.statistics import suggest_difficulty

    recent = [
        {"difficulty": "medium", "outcome": "win", "score": 2}
        for _ in range(5)
    ]
    assert suggest_difficulty("tic_tac_toe", {"tic_tac_toe": {"recent_results": recent}}) == "hard"


def test_profile_progression_excludes_practice_and_quit():
    from engine.profiles import Profile, update_profile
    from engine.result import GameResult

    profile = Profile()
    updated, style = update_profile(
        profile,
        GameResult(game="snake", outcome="game_over", difficulty="easy", mode="competitive", score=50),
    )
    assert updated.xp == 1
    assert updated.level == 1
    assert style is None

    practice, _ = update_profile(
        updated,
        GameResult(game="tic_tac_toe", outcome="win", difficulty="hard", mode="practice"),
    )
    assert practice == updated

    quit_profile, _ = update_profile(
        updated,
        GameResult(game="snake", outcome="quit", difficulty="easy", mode="competitive"),
    )
    assert quit_profile == updated


def test_achievement_unlock_persists(tmp_path):
    from engine.achievements import AchievementStore, unlock_achievements
    from engine.result import GameResult

    store = AchievementStore(tmp_path / "achievements.json")
    result = GameResult(
        game="snake",
        outcome="game_over",
        difficulty="hard",
        mode="competitive",
        score=250,
    )
    earned = unlock_achievements(
        store,
        result,
        {"snake": {"games": 1}},
    )
    assert "snake_200" in earned
    assert store.load()["snake_200"]["unlocked"] is True


def test_all_six_achievement_uses_competitive_history():
    from engine.achievements import ALL_ACHIEVEMENT_EVALUATOR
    from engine.result import GameResult

    result = GameResult(
        game="snake",
        outcome="game_over",
        difficulty="medium",
        mode="competitive",
        score=10,
    )
    assert "all_six_games" in ALL_ACHIEVEMENT_EVALUATOR.evaluate(
        result,
        context={"games_played": {
            "tic_tac_toe", "connect_four", "hangman",
            "rock_paper_scissors", "word_scramble", "snake"
        }},
    )


def test_export_summary(tmp_path):
    from main import export_summary
    from engine.profiles import Profile

    path = export_summary(
        Profile(name="Player", level=2, xp=12),
        {"snake": {"best_score": 240}},
        {"snake_200": {"unlocked": True}},
        tmp_path / "player_summary.md",
    )
    content = path.read_text(encoding="utf-8")
    assert "# Python Games Hub — Player Summary" in content
    assert "Snake 200" in content
    assert "best score" in content.lower()


def test_settings_store_rejects_unknown_banner_style(tmp_path):
    from engine.settings import SettingsStore

    store = SettingsStore(tmp_path / "settings.json")
    store.save({"banner_style": "rainbow", "auto_suggest_difficulty": False})
    assert store.load() == {
        "banner_style": "default",
        "auto_suggest_difficulty": False,
    }
