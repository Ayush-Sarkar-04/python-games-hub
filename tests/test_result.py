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


def test_game_result_supports_game_specific_metadata():
    result = GameResult(
        game="connect_four",
        outcome="win",
        difficulty="custom",
        mode="competitive",
        metadata={"custom_settings": {"minimax_depth": 6}},
    )
    updated = result.with_metadata(personality="Balanced")
    assert updated.metadata["custom_settings"]["minimax_depth"] == 6
    assert updated.metadata["personality"] == "Balanced"
