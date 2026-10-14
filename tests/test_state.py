from engine.state import GameState


def test_only_committed_moves_are_recorded():
    state = GameState(game="tic_tac_toe")
    state.record_move({"player": "X", "position": 4})
    assert state.moves == 1
    assert state.move_history == [{"player": "X", "position": 4}]
