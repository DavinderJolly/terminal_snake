import os
import platform
import random
import signal
from collections import deque
from typing import Optional

from pytimedinput import timedKey

from settings import MAP_HEIGHT
from settings import MAP_WIDTH


class ForeColors:
    """Foreground colors for the terminal."""

    RED: str = "\u001b[31m"
    GREEN: str = "\u001b[32m"
    BLUE: str = "\u001b[34m"
    CYAN: str = "\u001b[36m"
    BRIGHT_RED: str = "\u001b[31;1m"
    BRIGHT_GREEN: str = "\u001b[32;1m"
    BRIGHT_CYAN: str = "\u001b[36;1m"
    RESET: str = "\u001b[0m"


class Directions:
    """Unit vectors representing a direction."""

    LEFT: tuple[int, int] = (-1, 0)
    RIGHT: tuple[int, int] = (1, 0)
    DOWN: tuple[int, int] = (0, 1)
    UP: tuple[int, int] = (0, -1)


def wrap(pos: int, bound: int) -> int:
    """Wrap the snake around the edes of the map.

    Args:
        pos (int): The position to wrap.
        bound (int): The bound of the map.

    Returns:
        int: The wrapped position.
    """

    if pos <= 0:
        return bound - 2
    elif pos >= bound - 1:
        return 1
    else:
        return pos


def update_snake(
    snake: deque[tuple[int, int]],
    snake_body_set: set[tuple[int, int]],
    direction: tuple[int, int],
    ate_apple: bool,
) -> None:
    """Update the snake's position.

    Args:
        snake (deque[tuple[int, int]]): The snake's position.
        snake_body_set (set[tuple[int, int]]): The snake's body position.
        direction (tuple[int, int]): The direction of the snake.
        ate_apple (bool): Whether the snake has eaten the apple.
    """
    new_head_pos = (
        wrap(snake[0][0] + direction[0], MAP_WIDTH),
        wrap(snake[0][1] + direction[1], MAP_HEIGHT),
    )
    snake.appendleft(new_head_pos)
    snake_body_set.add(snake[1])
    if not ate_apple:
        removed = snake.pop()
        snake_body_set.remove(removed)


def print_map(
    width: int,
    height: int,
    snake_head: tuple[int, int],
    snake_body_set: set[tuple[int, int]],
    apple: tuple[int, int],
) -> None:
    """Print the map with the snake and the apple.

    Args:
        width (int): The width of the map.
        height (int): The height of the map.
        snake_head (tuple[int, int]): The snake's head position.
        snake_body_set (set[tuple[int, int]]): The snake's body position.
        apple (tuple[int, int]): The apple's position.
    """
    for y in range(height):
        for x in range(width):
            output = ""
            if x in (0, MAP_WIDTH - 1) or y in (0, MAP_HEIGHT - 1):
                output = ForeColors.BRIGHT_CYAN + "█" + ForeColors.RESET
            elif (x, y) == apple:
                output = ForeColors.BRIGHT_RED + "○" + ForeColors.RESET
            elif (x, y) == snake_head:
                output = ForeColors.BLUE + "⬤" + ForeColors.RESET
            elif (x, y) in snake_body_set:
                output = ForeColors.BRIGHT_GREEN + "⬤" + ForeColors.RESET
            else:
                output = " "
            print(output, end="")
        print()


def change_direction(current_dir: tuple[int, int], key: str) -> tuple[int, int]:
    """Change the direction of the snake.

    Args:
        current_dir (tuple[int, int]): The current direction of the snake.
        key (str): The key pressed by the user.

    Returns:
        tuple[int, int]: The new direction of the snake.
    """
    if key == "w" and current_dir != Directions.DOWN:
        return Directions.UP
    elif key == "s" and current_dir != Directions.UP:
        return Directions.DOWN
    elif key == "a" and current_dir != Directions.RIGHT:
        return Directions.LEFT
    elif key == "d" and current_dir != Directions.LEFT:
        return Directions.RIGHT
    return current_dir


def get_random_pos() -> tuple[int, int]:
    """Get a random position on the map.

    Returns:
        tuple[int, int]: The random position.
    """
    return (random.randrange(1, MAP_WIDTH - 1), random.randrange(1, MAP_HEIGHT - 1))


def get_apple_pos(
    snake_head: tuple[int, int], snake_body_set: set[tuple[int, int]]
) -> tuple[int, int]:
    """Get a random position on the map for the apple which is not inside the snake.

    Args:
        snake_head (tuple[int, int]): The snake's head position.
        snake_body_set (set[tuple[int, int]]): The snake's body position.

    Returns:
        tuple[int, int]: The apple's position.
    """
    new_pos = get_random_pos()
    while new_pos != snake_head and new_pos in snake_body_set:
        new_pos = get_random_pos()
    return new_pos


def clear_screen() -> None:
    """Clear the screen."""
    print("\033c", end="")


def clear_map() -> None:
    """Clear the map."""
    # offset according to extra newlines printed from quit message, the input, etc
    offset = 3
    print("\033[F" * (MAP_HEIGHT + offset), end="")


def show_cursor(show: bool) -> None:
    """Show or hide the cursor.

    Args:
        show (bool): True to show the cursor, False to hide it.
    """
    if show:
        print("\u001b[?25h")
    else:
        print("\u001b[?25l")


def exit_game(score: Optional[int] = 0, error: Optional[str] = None) -> None:
    """Exit the game.

    Args:
        score (Optional[int]): The score of the game.
        error (Optional[str]): The error message if game exit due to SIGINT or SIGTERM.
    """
    if error is None:
        show_cursor(True)
        clear_screen()
        print(f"{ForeColors.BRIGHT_GREEN}you scored: {score}{ForeColors.RESET}")
        raise SystemExit()
    else:
        show_cursor(True)
        clear_screen()
        raise SystemExit(error)


def handle_signals() -> None:
    """Handle the signals."""
    signal.signal(signal.SIGINT, lambda *_: exit_game(error="Game interupted"))
    signal.signal(signal.SIGTERM, lambda *_: exit_game(error="Game terminated"))


def main() -> None:
    """Entry point function."""
    snake: deque[tuple[int, int]] = deque(
        [
            (5, (MAP_HEIGHT // 2)),
            (4, (MAP_HEIGHT // 2)),
            (3, (MAP_HEIGHT // 2)),
        ]
    )
    snake_head = snake[0]
    snake_body_set = set([snake[i] for i in range(1, len(snake))])

    apple = get_apple_pos(snake_head, snake_body_set)
    ate_apple = False
    score = 0
    direction = Directions.RIGHT

    if platform.system() == "Windows":
        # windows clearfix to make ansi work outside of windows terminal
        os.system("cls")
    else:
        clear_screen()
    while True:
        handle_signals()
        show_cursor(False)
        clear_map()

        print("Press 'q' to quit")
        print_map(MAP_WIDTH, MAP_HEIGHT, snake_head, snake_body_set, apple)

        key_pressed, timed_out = timedKey(
            "\u001b[2K", timeout=0.2, allowCharacters="wasdq"  # type: ignore
        )

        if not timed_out:
            if key_pressed == "q":
                exit_game(score)
            else:
                direction = change_direction(direction, key_pressed)

        # mutate the snake and snake body set
        update_snake(snake, snake_body_set, direction, ate_apple)
        snake_head = snake[0]
        ate_apple = False

        if snake_head == apple:
            apple = get_apple_pos(snake[0], snake_body_set)
            ate_apple = True
            score += 1

        if snake_head in snake_body_set:
            exit_game(score)


if __name__ == "__main__":
    main()
