import pytest

from engine.game import SessionConfig


def test_session_config_defaults_to_competitive():
    config = SessionConfig(game="tic_tac_toe")
    assert config.is_competitive
    assert config.mode == "competitive"


def test_session_config_rejects_invalid_mode():
    with pytest.raises(ValueError):
        SessionConfig(game="tic_tac_toe", mode="ranked")


def test_session_config_accepts_custom_settings():
    config = SessionConfig(
        game="connect_four",
        difficulty="custom",
        custom_settings={"minimax_depth": 6},
    )
    assert config.custom_settings["minimax_depth"] == 6
