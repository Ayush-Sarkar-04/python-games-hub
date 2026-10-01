from games.tic_tac_toe import check_winner, get_winner


def test_web_adapter_uses_existing_winner_rules():
    board = ["X", "X", "X", " ", "O", " ", " ", " ", "O"]
    assert check_winner(board)
    assert get_winner(board) == "X"
