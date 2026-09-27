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
