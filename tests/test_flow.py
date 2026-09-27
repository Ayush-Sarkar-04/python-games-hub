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
    from main import GAME_CLASSES, choose_game_options

    class FakeHangman:
        def __init__(self):
            self.words = {
                "animals": {"name": "Animals", "words": ["Cat"]},
                "sports": {"name": "Sports", "words": ["Golf"]},
            }

    monkeypatch.setitem(GAME_CLASSES, "hangman", FakeHangman)
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
