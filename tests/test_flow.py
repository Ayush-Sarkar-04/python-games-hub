from main import choose_session_config
def test_choose_session_config_uses_hub_owned_input():
    answers = iter(["1"])
    config = choose_session_config("tic_tac_toe", input_func=lambda _: next(answers))
    assert config.game == "tic_tac_toe"
    assert config.difficulty == "easy"
def test_choose_session_mode_supports_practice(monkeypatch):
    from main import choose_session_mode
    answers = iter(["2"])
    mode = choose_session_mode(input_func=lambda _: next(answers))
    assert mode == "practice"


def test_choose_game_options_tic_tac_toe(monkeypatch):
    from main import choose_game_options

    answers = iter(["2"])
    options = choose_game_options("tic_tac_toe", input_func=lambda _: next(answers))
    assert options == {"player_mode": "player", "personality": "Balanced"}


def test_choose_game_options_tic_tac_toe_personality():
    from main import choose_game_options

    answers = iter(["1", "3"])
    options = choose_game_options("tic_tac_toe", input_func=lambda _: next(answers))
    assert options == {"player_mode": "computer", "personality": "Defensive"}


def test_choose_game_options_connect_four():
    from main import choose_game_options

    answers = iter(["2", "2"])
    options = choose_game_options("connect_four", input_func=lambda _: next(answers))
    assert options == {"player_mode": "player", "first_player": "O"}


def test_choose_game_options_hangman(monkeypatch):
    from main import GAME_REGISTRY, GameDefinition, choose_game_options

    class FakeHangman:
        def __init__(self):
            self.words = {
                "animals": {"name": "Animals", "words": ["Cat"]},
                "sports": {"name": "Sports", "words": ["Golf"]},
            }

    original = GAME_REGISTRY["hangman"]
    monkeypatch.setitem(
        GAME_REGISTRY,
        "hangman",
        GameDefinition(
            original.name,
            original.description,
            original.module,
            FakeHangman,
            original.capabilities,
            original.modes,
            original.difficulties,
            original.configuration_options,
            original.custom_parameters,
        ),
    )
    options = choose_game_options("hangman", input_func=lambda _: "2")
    assert options == {"category": "sports"}


def test_choose_game_options_snake_wrap():
    from main import choose_game_options

    assert choose_game_options("snake", input_func=lambda _: "2") == {"wrap": True}


def test_choose_session_config_keeps_custom_out_of_standard_menu():
    from main import choose_session_config
    answers = iter(["1"])
    config = choose_session_config("tic_tac_toe", input_func=lambda _: next(answers))
    assert config.difficulty == "easy"


def test_build_session_config_accepts_board_game_custom_settings():
    from main import build_session_config
    config = build_session_config(
        "connect_four", "custom", custom_settings={"minimax_depth": 6}
    )
    assert config.difficulty == "custom"
    assert config.custom_settings == {"minimax_depth": 6}


def test_choose_session_config_offers_advanced_custom():
    from main import choose_session_config
    answers = iter(["4", "6"])
    config = choose_session_config("connect_four", input_func=lambda _: next(answers))
    assert config.difficulty == "custom"
    assert config.custom_settings == {"minimax_depth": 6}


def test_choose_session_config_does_not_offer_custom_for_snake():
    from main import choose_session_config
    answers = iter(["3"])
    config = choose_session_config("snake", input_func=lambda _: next(answers))
    assert config.difficulty == "hard"


def test_process_result_persists_statistics_profile_and_achievement(tmp_path):
    from main import process_result
    from engine.achievements import AchievementStore
    from engine.profiles import ProfileStore
    from engine.statistics import StatisticsStore
    from engine.result import GameResult

    result = GameResult(
        game="word_scramble",
        outcome="win",
        difficulty="easy",
        mode="competitive",
        score=3,
        metadata={"attempts": 1},
    )
    profile_store = ProfileStore(tmp_path / "profile.json")
    statistics_store = StatisticsStore(tmp_path / "statistics.json")
    achievement_store = AchievementStore(tmp_path / "achievements.json")
    processed = process_result(
        result,
        profile_store=profile_store,
        statistics_store=statistics_store,
        achievement_store=achievement_store,
    )
    assert processed["profile"].xp == 2
    assert statistics_store.load()["word_scramble"]["wins"] == 1
    assert "word_scramble_first_try" in processed["achievements"]
    assert achievement_store.load()["word_scramble_first_try"]["unlocked"] is True


def test_registry_is_single_source_for_game_classes():
    from main import GAME_REGISTRY
    assert all(definition.game_class for definition in GAME_REGISTRY.values())


def test_settings_menu_only_offers_unlocked_styles(tmp_path):
    from main import settings_menu
    from engine.profiles import Profile
    from engine.settings import SettingsStore

    store = SettingsStore(tmp_path / "settings.json")
    answers = iter(["1", "1", "3"])
    settings = settings_menu(
        store,
        Profile(name="Player", level=1, xp=0, unlocked_styles=("default",)),
        input_func=lambda _: next(answers),
    )
    assert settings["banner_style"] == "default"
