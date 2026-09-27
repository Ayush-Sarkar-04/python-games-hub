from main import GAME_REGISTRY, build_session_config


def test_registry_uses_stable_game_identifiers():
    assert "tic_tac_toe" in GAME_REGISTRY
    assert "connect_four" in GAME_REGISTRY
    assert "1" not in GAME_REGISTRY


def test_registry_declares_capabilities():
    assert "replay" in GAME_REGISTRY["tic_tac_toe"].capabilities
    assert "run_history" in GAME_REGISTRY["snake"].capabilities
    assert "custom_difficulty" not in GAME_REGISTRY["snake"].capabilities


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
