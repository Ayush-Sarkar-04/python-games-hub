"""Shared terminal input and display helpers."""

from typing import Iterable


def display_title(title: str, width: int = 64, style: str = "default") -> None:
    if style == "minimal":
        print(f"\n{title}")
        return
    if style == "compact":
        width = min(width, max(42, len(title) + 8))
    if style == "classic":
        print("\n" + "*" * width)
        print(title.center(width))
        print("*" * width)
        return
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)


def choose_from_menu(
    prompt: str,
    options: Iterable[str],
    *,
    input_func=input,
) -> str:

    valid = {str(option) for option in options}
    while True:
        choice = input_func(prompt).strip()
        if choice in valid:
            return choice
        print("Invalid choice. Please choose a listed option.")


def play_again(*, input_func=input) -> bool:
    while True:
        choice = input_func("\nPlay again? (y/n): ").strip().lower()
        if choice in {"y", "n"}:
            return choice == "y"
        print("Invalid input! Enter y or n.")


