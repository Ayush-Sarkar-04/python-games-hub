from main import GAME_REGISTRY, build_session_config


def test_registry_uses_stable_game_identifiers():
    assert "tic_tac_toe" in GAME_REGISTRY
    assert "connect_four" in GAME_REGISTRY
    assert "minesweeper" in GAME_REGISTRY
    assert "1" not in GAME_REGISTRY


def test_registry_declares_capabilities():
    assert "replay" in GAME_REGISTRY["tic_tac_toe"].capabilities
    assert "custom_difficulty" in GAME_REGISTRY["tic_tac_toe"].capabilities
    assert "custom_difficulty" in GAME_REGISTRY["connect_four"].capabilities
    assert "run_history" in GAME_REGISTRY["snake"].capabilities
    assert "custom_difficulty" not in GAME_REGISTRY["snake"].capabilities


def test_custom_difficulty_supported_for_board_games():
    assert build_session_config(
        "tic_tac_toe", "custom", custom_settings={"minimax_depth": 5}
    ).difficulty == "custom"
    assert build_session_config(
        "connect_four", "custom", custom_settings={"minimax_depth": 5}
    ).difficulty == "custom"


def test_custom_difficulty_rejected_when_capability_is_absent():
    try:
        build_session_config("snake", "custom")
    except ValueError as exc:
        assert "custom difficulty" in str(exc)
    else:
        raise AssertionError("Expected custom difficulty to be rejected")


def test_practice_session_is_explicit():
    config = build_session_config("tic_tac_toe", "easy", mode="practice")
    assert config.mode == "practice"
    assert not config.is_competitive


def test_hangman_declares_custom_difficulty():
    assert "custom_difficulty" in GAME_REGISTRY["hangman"].capabilities


def test_registry_contains_all_game_classes():
    assert {definition.game_class.__name__ for definition in GAME_REGISTRY.values()} == {
        "TicTacToeGame",
        "ConnectFourGame",
        "HangmanGame",
        "RockPaperScissorsGame",
        "WordScrambleGame",
        "SnakeGame",
        "MinesweeperGame",
        "TypingTestGame",
        "MastermindGame",
    }


def test_all_registered_games_accept_hub_session_configuration():
    from main import GAME_REGISTRY, build_session_config

    options = {
        "tic_tac_toe": {"player_mode": "computer", "personality": "Balanced"},
        "connect_four": {"player_mode": "computer", "first_player": "X"},
        "hangman": {"category": "animals"},
        "rock_paper_scissors": {"variant": "standard", "match_type": "single", "rounds": 1},
        "word_scramble": {},
        "snake": {"wrap": False},
        "minesweeper": {},
        "typing_test": {},
        "mastermind": {},
    }
    for game, definition in GAME_REGISTRY.items():
        config = build_session_config(game, "medium", options=options[game])
        instance = (
            definition.game_class({"animals": {"name": "Animals", "words": ["cat"]}})
            if game == "hangman"
            else definition.game_class()
        )
        state = instance.setup(config)
        assert state.game == game


def test_registry_definitions_do_not_store_redundant_module_paths():
    assert all(not hasattr(definition, "module") for definition in GAME_REGISTRY.values())
