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
    """

    if pos <= 0:
        return bound - 2
    elif pos >= bound - 1:
        return 1
    else:
        return pos


def hit_apple(
    head: tuple[int, int], direction: tuple[int, int], apple: tuple[int, int]
) -> bool:
    """Check if the snake has hit the apple.

    Args:
        head (tuple[int, int]): The snake's head position.
        direction (tuple[int, int]): The direction of the snake.
        apple (tuple[int, int]): The apple's position.
    """
    new_head_pos = (
        wrap(head[0] + direction[0], MAP_WIDTH),
        wrap(head[1] + direction[1], MAP_HEIGHT),
    )

    return new_head_pos == apple


def hit_self(snake: deque[tuple[int, int]]) -> bool:
    """Check if the snake has hit itself.

    Args:
        snake (deque[tuple[int, int]]): The snake's position.
    """
    return len(snake) > 3 and snake[0] in [snake[i] for i in range(3, len(snake))]


def update_snake(
    snake: deque[tuple[int, int]], direction: tuple[int, int]
) -> deque[tuple[int, int]]:
    """Update the snake's position.

    Args:
        snake (deque[tuple[int, int]]): The snake's position.
        direction (tuple[int, int]): The direction of the snake.
    """
    new_head_pos = (
        wrap(snake[0][0] + direction[0], MAP_WIDTH),
        wrap(snake[0][1] + direction[1], MAP_HEIGHT),
    )
    new_snake = snake.copy()
    new_snake.appendleft(new_head_pos)
    new_snake.pop()
    return new_snake


def print_map(
    cells: list[tuple[int, int]], snake: deque[tuple[int, int]], apple: tuple[int, int]
) -> None:
    """Print the map with the snake and the apple.

    Args:
        cells (list[tuple[int, int]]): The map.
        snake (deque[tuple[int, int]]): The snake's position.
        apple (tuple[int, int]): The apple's position.
    """
    for cell in cells:
        output = ""
        if cell[0] in (0, MAP_WIDTH - 1) or cell[1] in (0, MAP_HEIGHT - 1):
            output = ForeColors.BRIGHT_CYAN + "█" + ForeColors.RESET
        elif cell == apple:
            output = ForeColors.BRIGHT_RED + "○" + ForeColors.RESET
        elif cell == snake[0]:
            output = ForeColors.BLUE + "⬤" + ForeColors.RESET
        elif cell in [snake[i] for i in range(1, len(snake))]:
            output = ForeColors.BRIGHT_GREEN + "⬤" + ForeColors.RESET
        else:
            output = " "
        print(output, end="")
        if cell[0] == MAP_WIDTH - 1:
            print()


def change_direction(current_dir: tuple[int, int], key: str) -> tuple[int, int]:
    """Change the direction of the snake.

    Args:
        current_dir (tuple[int, int]): The current direction of the snake.
        key (str): The key pressed by the user.
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
    """Get a random position on the map."""
    return (random.randrange(1, MAP_WIDTH - 1), random.randrange(1, MAP_HEIGHT - 1))


def get_apple_pos(snake: deque[tuple[int, int]]):
    """Get a random position on the map for the apple which is not inside the snake.

    Args:
        snake (deque[tuple[int, int]]): The snake's position.
    """
    new_pos = get_random_pos()
    while new_pos in snake:
        new_pos = get_random_pos()
    return new_pos


def clear_screen() -> None:
    """Clear the screen."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def clear_map() -> None:
    """Clear the map."""
    print("\033[F" * (MAP_HEIGHT + 5))


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
    cells = [(col, row) for row in range(MAP_HEIGHT) for col in range(MAP_WIDTH)]
    snake: deque[tuple[int, int]] = deque(
        [
            (5, (MAP_HEIGHT // 2)),
            (4, (MAP_HEIGHT // 2)),
            (3, (MAP_HEIGHT // 2)),
        ]
    )
    apple = get_apple_pos(snake)
    score = 0
    direction = Directions.RIGHT

    clear_screen()
    while True:
        handle_signals()
        show_cursor(False)
        clear_map()

        print("Press 'q' to quit")
        print_map(cells, snake, apple)

        key_pressed, timed_out = timedKey(
            "\u001b[2K", timeout=0.3, allowCharacters="wasdq"  # type: ignore
        )

        if not timed_out:
            if key_pressed == "q":
                exit_game(score)
            else:
                direction = change_direction(direction, key_pressed)

        if hit_apple(snake[0], direction, apple):
            snake.append(snake[-1])
            apple = get_apple_pos(snake)
            score += 1

        if hit_self(snake):
            exit_game(score)

        snake = update_snake(snake, direction)


if __name__ == "__main__":
    main()
