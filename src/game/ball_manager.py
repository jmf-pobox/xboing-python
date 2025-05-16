from typing import Iterator, List, Optional

from .ball import Ball


class BallManager:
    """
    Manages the canonical list of Ball objects in play.
    Provides methods to add, remove, reset, and iterate balls.
    """

    def __init__(self) -> None:
        self._balls: List[Ball] = []

    @property
    def balls(self) -> List[Ball]:
        """Return the list of balls (read/write for legacy compatibility)."""
        return self._balls

    def __iter__(self) -> Iterator[Ball]:
        return iter(self._balls)

    def add_ball(self, ball: Ball) -> None:
        self._balls.append(ball)

    def remove_ball(self, ball: Ball) -> None:
        self._balls.remove(ball)

    def clear(self) -> None:
        self._balls.clear()

    def reset(self, initial_ball: Optional[Ball] = None) -> None:
        """Clear all balls and optionally add a new one."""
        self._balls.clear()
        if initial_ball is not None:
            self._balls.append(initial_ball)

    def get_active_balls(self) -> List[Ball]:
        return [ball for ball in self._balls if ball.active]

    def __len__(self) -> int:
        return len(self._balls)

    def available_balls(self) -> int:
        """
        Return the number of balls currently managed (available for play).
        """
        return len(self._balls)

    def active_ball(self) -> bool:
        """
        Return True if there is at least one active ball in play.
        """
        return any(ball.active for ball in self._balls)

    def number_of_active_balls(self) -> int:
        """
        Return the number of active balls in play.
        """
        return sum(1 for ball in self._balls if ball.active)
