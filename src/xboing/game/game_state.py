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
    XBoingEvent,
)


class LevelState:
    """Tracks per-level state, such as level number, bonus coins collected, and timer."""

    def __init__(self, level_num: int = 1, time_bonus: int = 0) -> None:
        """Initialize LevelState with the given level number and time bonus."""
        self.level_num: int = level_num
        self.bonus_coins_collected: int = 0
        self.time_bonus_limit: int = time_bonus  # The starting time for the level
        self.timer: int = time_bonus  # The current time remaining (seconds)
        self._timer_ms_accum: float = 0.0  # Accumulate ms between frames
        self.level_complete: bool = False

    def set_level_complete(self) -> None:
        """Set the level complete flag."""
        self.level_complete = True

    def is_level_complete(self) -> bool:
        """Return True if the level is complete, False otherwise."""
        return self.level_complete

    def add_bonus_time(self, time_bonus: int) -> List[XBoingEvent]:
        """Add time bonus to the level."""
        self.time_bonus_limit += time_bonus
        self.timer += time_bonus
        return [TimerUpdatedEvent(self.get_bonus_time())]

    def set_bonus_time(self, time_bonus: int) -> None:
        """Set the time bonus limit for the level and reset the timer."""
        self.time_bonus_limit = time_bonus
        self.timer = time_bonus
        self._timer_ms_accum = 0.0

    def decrement_bonus_time(self, delta_ms: float) -> None:
        """Decrement the timer by delta_ms milliseconds, 1 second at a time."""
        if self.timer <= 0:
            return
        self._timer_ms_accum += delta_ms
        while self._timer_ms_accum >= 1000.0 and self.timer > 0:
            self.timer -= 1
            self._timer_ms_accum -= 1000.0

    def get_bonus_time(self) -> int:
        """Return the current time remaining (seconds)."""
        return self.timer

    def get_bonus_coins_collected(self) -> int:
        """Return the number of bonus coins collected at this level."""
        return self.bonus_coins_collected

    def increment_bonus_coins_collected(self, amount: int = 1) -> None:
        """Increment the number of bonus coins collected at this level."""
        self.bonus_coins_collected += amount

    def calculate_all_bonuses(self, bullets: int) -> int:
        """Calculate the level bonus based on the level number."""
        level_bonus = self.calculate_level_bonus()
        timer_bonus = self.calculate_time_bonus()
        bullet_bonus = self.calculate_bullet_bonus(bullets)
        coin_bonus = self.calculate_coin_bonus()
        super_bonus = self.calculate_super_bonus()
        return level_bonus + timer_bonus + bullet_bonus + coin_bonus + super_bonus

    def get_time_bonus(self) -> int:
        """Return the starting time bonus for the level (seconds)."""
        return self.time_bonus_limit

    def calculate_super_bonus(self) -> int:
        """Calculate the super bonus based on the number of bonus coins collected."""
        super_bonus = 50000 if self.bonus_coins_collected > 8 else 0
        return super_bonus

    def calculate_coin_bonus(self) -> int:
        """Calculate the coin bonus based on the number of bonus coins collected."""
        coin_bonus: int = self.bonus_coins_collected * 3000
        return coin_bonus

    @staticmethod
    def calculate_bullet_bonus(bullets: int) -> int:
        """Calculate the bullet bonus based on the number of bullets fired."""
        bullet_bonus: int = bullets * 500
        return bullet_bonus

    def calculate_time_bonus(self) -> int:
        """Calculate the timer bonus based on the current time remaining (seconds)."""
        timer_bonus: int = self.get_bonus_time() * 100
        return timer_bonus

    def calculate_level_bonus(self) -> int:
        """Calculate the level bonus based on the level number."""
        level_bonus: int = self.level_num * 100
        return level_bonus


# Initial ammo count
INITIAL_AMMO_COUNT = 4


class GameState:
    """Manages the current state of the game, including score, lives, level, timer, and special flags.

    Provides methods to update the state and generate corresponding events.
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
    level_state: LevelState

    def __init__(self) -> None:
        """Initialize the GameState with default values and event mappings."""
        self.logger = logging.getLogger("xboing.GameState")
        self.score = 0
        self.lives = 3
        self.level = 1
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
        self.ammo = INITIAL_AMMO_COUNT
        self.level_state = LevelState(level_num=self.level)

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
        """Set the ammo count and return a list of change events."""
        self.ammo = ammo
        self.logger.info(f"Ammo set to {self.ammo}")
        return [AmmoCollectedEvent(self.ammo)]

    # --- Score methods ---

    def add_score(self, points: int) -> List[Any]:
        """Add points to the score and return a list of change events."""
        self.score += points
        self.logger.info(f"Score increased by {points}, new score: {self.score}")
        return [ScoreChangedEvent(self.score)]

    def _set_score(self, score: int) -> List[Any]:
        """Set the score and return a list of change events."""
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
        """Decrement lives and return a list of change events."""
        self.lives -= 1
        self.logger.info(f"Life lost, remaining lives: {self.lives}")
        if self.lives <= 0:
            self.set_game_over(True)
            return [LivesChangedEvent(0), GameOverEvent()]
        return [LivesChangedEvent(self.lives)]

    def _set_lives(self, lives: int) -> List[Any]:
        """Set the number of lives and return a list of change events."""
        self.lives = lives
        self.logger.info(f"Lives set to {self.lives}")
        return [LivesChangedEvent(self.lives)]

    # --- Levels methods ---

    def set_level(self, level: int) -> List[Any]:
        """Set the level and return a list of change events."""
        if self.level == level:
            return []
        self.level = level
        self.level_state = LevelState(level_num=level)
        self.logger.info(f"Level set to {self.level}")
        return [LevelChangedEvent(self.level)]

    # --- Timer methods ---

    def set_timer(self, time_remaining: int) -> List[Any]:
        """Set the timer and return a list of change events."""
        self.level_state.set_bonus_time(time_remaining)
        self.logger.debug(f"Timer set to {self.level_state.get_bonus_time()}")
        return [TimerUpdatedEvent(self.level_state.get_bonus_time())]

    # --- Special methods ---

    def set_special(self, name: str, value: bool) -> List[Any]:
        """Set a special flag and return a list of change events."""
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
        """Set the game-over flag and return a list of change events."""
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
        """Reset the game state, load the level, set the bonus timer from
        level manager, and return all change events.
        """
        self.logger.info("Full game state restart")
        all_events = []

        self.game_over = False
        all_events += self._set_ammo(4)
        all_events += self._set_lives(3)
        all_events += self._set_score(0)
        all_events += self.set_level(
            1
        )  # Could also be another level if -l flag is used
        for name in self.specials:
            all_events += self.set_special(name, False)

        level_manager.load_level(self.level)
        level_info = level_manager.get_level_info()
        level_title = level_info["title"]
        time_bonus = level_info.get("time_bonus", 0)
        all_events += self.set_timer(time_bonus)
        all_events.append(
            MessageChangedEvent(level_title, color=(0, 255, 0), alignment="left")
        )
        return all_events

    def start_new_level(self, level_num: int) -> None:
        """Reset level state for a new level."""
        self.level_state = LevelState(level_num=level_num)
        self.level = level_num
        self.logger.info(f"Started new level: {level_num}")

    def get_level_num(self) -> int:
        """Return the current level number (from LevelState)."""
        return self.level_state.level_num
