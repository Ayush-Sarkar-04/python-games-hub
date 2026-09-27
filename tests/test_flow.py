from main import choose_session_config
def test_choose_session_config_uses_hub_owned_input(monkeypatch):
    answers = iter(["1"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    config = choose_session_config("tic_tac_toe", input_func=lambda _: next(answers))
    assert config.game == "tic_tac_toe"
    assert config.difficulty == "easy"
def test_choose_session_mode_supports_practice(monkeypatch):
    from main import choose_session_mode
    answers = iter(["2"])
    mode = choose_session_mode(input_func=lambda _: next(answers))
    assert mode == "practice"
