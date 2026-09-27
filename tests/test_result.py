import pytest

from engine.result import GameResult


def test_game_result_supports_snake_outcomes():
    result = GameResult(
        game="snake",
        outcome="game_over",
        difficulty="hard",
        mode="competitive",
        score=90,
    )
    assert result.outcome == "game_over"
    assert result.score == 90


def test_game_result_rejects_invalid_outcome():
    with pytest.raises(ValueError, match="Unsupported outcome"):
        GameResult(
            game="test",
            outcome="banana",
            difficulty="hard",
            mode="competitive",
        )


def test_game_result_requires_nested_configuration_metadata():
    result = GameResult(
        game="connect_four",
        outcome="win",
        difficulty="custom",
        mode="competitive",
        metadata={
            "configuration": {
                "custom_settings": {"minimax_depth": 6},
                "personality": "Balanced",
            }
        },
    )
    updated = result.with_metadata(personality="Aggressive")
    assert updated.metadata["configuration"]["custom_settings"]["minimax_depth"] == 6
    assert updated.metadata["configuration"]["personality"] == "Aggressive"


def test_game_result_rejects_flat_configuration_metadata():
    with pytest.raises(ValueError, match=r"metadata\['configuration'\]"):
        GameResult(
            game="connect_four",
            outcome="win",
            difficulty="custom",
            mode="competitive",
            metadata={"custom_settings": {"minimax_depth": 6}},
        )
