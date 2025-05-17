"""Defines the GameState class for managing XBoing's game state and transitions."""

import logging
from typing import Any, Dict, List

from engine.events import (
    GameOverEvent,
    LevelChangedEvent,
    LivesChangedEvent,
    MessageChangedEvent,
    ScoreChangedEvent,
    SpecialFastGunChangedEvent,
    SpecialKillerChangedEvent,
    SpecialNoWallChangedEvent,
    SpecialReverseChangedEvent,
    SpecialSaveChangedEvent,
    SpecialStickyChangedEvent,
    SpecialX2ChangedEvent,
    SpecialX4ChangedEvent,
    TimerUpdatedEvent,
)


class GameState:
    """Manages the current state of the game, including score, lives, level, timer, and special flags.

    Provides methods to update state and generate corresponding events.
    """

    logger: logging.Logger
    score: int
    lives: int
    level: int
    timer: int
    game_over: bool
    specials: Dict[str, bool]
    _event_map: Dict[str, Any]

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
        self._event_map = {
            "reverse": SpecialReverseChangedEvent,
            "sticky": SpecialStickyChangedEvent,
            "save": SpecialSaveChangedEvent,
            "fastgun": SpecialFastGunChangedEvent,
            "nowall": SpecialNoWallChangedEvent,
            "killer": SpecialKillerChangedEvent,
            "x2": SpecialX2ChangedEvent,
            "x4": SpecialX4ChangedEvent,
        }

    def add_score(self, points: int) -> List[Any]:
        """Add points to the score and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        self.score += points
        self.logger.info(f"Score increased by {points}, new score: {self.score}")
        return [ScoreChangedEvent(self.score)]

    def set_score(self, score: int) -> List[Any]:
        """Set the score and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        self.score = score
        self.logger.info(f"Score set to {self.score}")
        return [ScoreChangedEvent(self.score)]

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

    def set_lives(self, lives: int) -> List[Any]:
        """Set the number of lives and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        self.lives = lives
        self.logger.info(f"Lives set to {self.lives}")
        return [LivesChangedEvent(self.lives)]

    def set_level(self, level: int) -> List[Any]:
        """Set the level and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        self.level = level
        self.logger.info(f"Level set to {self.level}")
        return [LevelChangedEvent(self.level)]

    def set_timer(self, time_remaining: int) -> List[Any]:
        """Set the timer and return a list of change events.

        Does not fire events directly (side-effect free).
        """
        self.timer = time_remaining
        self.logger.debug(f"Timer set to {self.timer}")
        return [TimerUpdatedEvent(self.timer)]

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

    def restart(self) -> List[Any]:
        """Reset the game state and return a list of all change events.

        Does not fire events directly (side-effect free).
        """
        self.logger.info("Game state restarted")
        all_events = []
        self.game_over = False
        all_events += self.set_score(0)
        all_events += self.set_lives(3)
        all_events += self.set_level(1)
        all_events += self.set_timer(0)
        all_events += self.set_game_over(False)
        for name in self.specials:
            all_events += self.set_special(name, False)
        return all_events

    def full_restart(self, level_manager: Any) -> List[Any]:
        """Reset all game state, load the level, set timer from level manager, and return all change events.

        Does not fire events directly (side-effect free).
        """
        self.logger.info("Full game state restart")
        all_events = []

        self.game_over = False
        all_events += self.set_score(0)
        all_events += self.set_lives(3)
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

    def get_lives(self) -> int:
        """Return the current number of lives."""
        if self.lives is not None:
            return self.lives
        return 0
