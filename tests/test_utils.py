from engine.utils import choose_from_menu, play_again


def test_choose_from_menu_retries_invalid_input():
    values = iter(["x", "2"])
    assert choose_from_menu("Choose: ", {"1", "2"}, input_func=lambda _: next(values)) == "2"


def test_play_again_accepts_valid_response():
    assert play_again(input_func=lambda _: "y") is True
