from main import choose_session_config


def test_choose_session_config_uses_hub_owned_input(monkeypatch):
    answers = iter(["1"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    config = choose_session_config("tic_tac_toe", input_func=lambda _: next(answers))
    assert config.game == "tic_tac_toe"
    assert config.difficulty == "easy"
