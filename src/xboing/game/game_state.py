"""Defines the GameState class for managing XBoing's game state and transitions."""

import logging
from typing import Any, Dict, List

from xboing.engine.events import (
    SPECIAL_EVENT_MAP,
    AmmoCollectedEvent,
    AmmoFiredEvent,
    GameOverEvent,
    LevelChangedEvent,
    LivesChangedEvent,
    MessageChangedEvent,
    ScoreChangedEvent,
    TimerUpdatedEvent,
)


class GameState:
    """Manages the current state of the game, including score, lives, level, timer, and special flags.

    Provides methods to update state and generate corresponding events.
    """

    logger: logging.Logger
    ammo: int
    event_map: Dict[str, Any]
    game_over: bool
    lives: int
    level: int
    score: int
    specials: Dict[str, bool]
    timer: int

    def __init__(self) -> None:
        """Initialize the GameState with default values and event mappings."""
        self.logger = logging.getLogger("xboing.GameState")
        self.score = 0
        self.lives = 3
        self.level = 1
        self.timer = 0
        self.game_over = False
        self.specials = {
            "reverse": False,
            "sticky": False,
            "save": False,
            "fastgun": False,
            "nowall": False,
            "killer": False,
            "x2": False,
            "x4": False,
        }
        self._event_map = SPECIAL_EVENT_MAP
        self.ammo = 4  # Initial ammo count matches original C version

    # --- Ammo methods ---

    def add_ammo(self, amount: int = 4) -> List[Any]:
        """Add ammo up to the maximum of 20.

        Args:
        ----
            amount (int): The amount of ammo to add. Defaults to 4.

        Returns:
        -------
            List[Any]: A list of change events (AmmoCollectedEvent).

        """
        old_ammo = self.ammo
        self.ammo = min(self.ammo + amount, 20)
        if self.ammo != old_ammo:
            self.logger.info(f"Ammo added, remaining ammo: {self.ammo}")
            return [AmmoCollectedEvent(self.ammo)]
        return []

    def fire_ammo(self) -> List[Any]:
        """Decrement ammo and return a list of change events (AmmoFiredEvent)."""
        if self.ammo > 0:
            self.ammo -= 1
            self.logger.info(f"Ammo fired, remaining ammo: {self.ammo}")
            return [AmmoFiredEvent(self.ammo)]
        self.logger.info("No ammo left to fire.")
        return []

    def get_ammo(self) -> int:
        """Return the current ammo count."""
        return self.ammo

    def _set_ammo(self, ammo: int) -> List[Any]:
        """Set the ammo count and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        self.ammo = ammo
        self.logger.info(f"Ammo set to {self.ammo}")
        return [AmmoCollectedEvent(self.ammo)]

    # --- Score methods ---

    def add_score(self, points: int) -> List[Any]:
        """Add points to the score and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        self.score += points
        self.logger.info(f"Score increased by {points}, new score: {self.score}")
        return [ScoreChangedEvent(self.score)]

    def _set_score(self, score: int) -> List[Any]:
        """Set the score and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        self.score = score
        self.logger.info(f"Score set to {self.score}")
        return [ScoreChangedEvent(self.score)]

    # --- Lives methods ---

    def get_lives(self) -> int:
        """Return the current number of lives."""
        if self.lives is not None:
            return self.lives
        return 0

    def lose_life(self) -> List[Any]:
        """Decrement lives and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        self.lives -= 1
        self.logger.info(f"Life lost, remaining lives: {self.lives}")
        if self.lives <= 0:
            self.set_game_over(True)
            return [LivesChangedEvent(0), GameOverEvent()]
        return [LivesChangedEvent(self.lives)]

    def _set_lives(self, lives: int) -> List[Any]:
        """Set the number of lives and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        self.lives = lives
        self.logger.info(f"Lives set to {self.lives}")
        return [LivesChangedEvent(self.lives)]

    # --- Levels methods ---

    def set_level(self, level: int) -> List[Any]:
        """Set the level and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        self.level = level
        self.logger.info(f"Level set to {self.level}")
        return [LevelChangedEvent(self.level)]

    # --- Timer methods ---

    def set_timer(self, time_remaining: int) -> List[Any]:
        """Set the timer and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        self.timer = time_remaining
        self.logger.debug(f"Timer set to {self.timer}")
        return [TimerUpdatedEvent(self.timer)]

    # --- Special methods ---

    def set_special(self, name: str, value: bool) -> List[Any]:
        """Set a special flag and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        if name in self.specials and self.specials[name] != value:
            self.specials[name] = value
            self.logger.info(f"Special '{name}' set to {value}")
            return [self._event_map[name](value)]
        return []

    def get_special(self, name: str) -> bool:
        """Get the value of a special flag."""
        return self.specials.get(name, False)

    # --- Game lifecycle (over, restart) methods ---

    def set_game_over(self, value: bool) -> List[Any]:
        """Set the game over flag and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        if self.game_over != value:
            self.game_over = value
            self.logger.info(f"Game over set to {self.game_over}")
            if value:
                return [GameOverEvent()]
        return []

    def is_game_over(self) -> bool:
        """Return True if the game is over, False otherwise."""
        return self.game_over

    def full_restart(self, level_manager: Any) -> List[Any]:
        """Reset all game state, load the level, set timer from level manager, and return all change events.

        Does not fire events directly (side-effect free).
        """
        self.logger.info("Full game state restart")
        all_events = []

        self.game_over = False
        all_events += self._set_ammo(4)
        all_events += self._set_lives(3)
        all_events += self._set_score(0)
        all_events += self.set_level(1)
        for name in self.specials:
            all_events += self.set_special(name, False)

        level_manager.load_level(self.level)
        all_events += self.set_timer(level_manager.get_time_remaining())
        level_info = level_manager.get_level_info()
        level_title = level_info["title"]
        all_events.append(
            MessageChangedEvent(level_title, color=(0, 255, 0), alignment="left")
        )
        return all_events
