"""Manages ball objects and their state in XBoing."""

from typing import Iterator, List, Optional

from .ball import Ball


class BallManager:
    """Manages the canonical list of Ball objects in play.

    Provides methods to add, remove, reset, and iterate balls.
    """

    def __init__(self) -> None:
        """Initialize the BallManager with an empty list of balls."""
        self._balls: List[Ball] = []

    @property
    def balls(self) -> List[Ball]:
        """Return the list of balls (read/write for legacy compatibility)."""
        return self._balls

    def __iter__(self) -> Iterator[Ball]:
        """Return an iterator over the managed balls."""
        return iter(self._balls)

    def add_ball(self, ball: Ball) -> None:
        """Add a ball to the manager."""
        self._balls.append(ball)

    def remove_ball(self, ball: Ball) -> None:
        """Remove a ball from the manager."""
        self._balls.remove(ball)

    def clear(self) -> None:
        """Remove all balls from the manager."""
        self._balls.clear()

    def reset(self, initial_ball: Optional[Ball] = None) -> None:
        """Clear all balls and optionally add a new one."""
        self._balls.clear()
        if initial_ball is not None:
            self._balls.append(initial_ball)

    def has_ball_in_play(self) -> bool:
        """Return True if there is at least one ball that is active and not stuck to the paddle (i.e., in play)."""
        return any(ball.active and not ball.stuck_to_paddle for ball in self._balls)

    def __len__(self) -> int:
        """Return the number of balls currently managed."""
        return len(self._balls)

    def available_balls(self) -> int:
        """Return the number of balls currently managed (available for play)."""
        return len(self._balls)

    def active_ball(self) -> bool:
        """Return True if there is at least one active ball in play."""
        return any(ball.active for ball in self._balls)

    def number_of_active_balls(self) -> int:
        """Return the number of active balls in play."""
        return sum(1 for ball in self._balls if ball.active)

    def remove_inactive_balls(self) -> None:
        """Remove all balls that are not active, in place."""
        self._balls[:] = [ball for ball in self._balls if ball.is_active()]
