"""Events module for XBoing."""

from typing import Tuple

import pygame


class XBoingEvent:
    """Base class for all XBoing game events."""


class AmmoFiredEvent(XBoingEvent):
    """Event fired when ammo is used (e.g., bullet shot)."""

    sound_effect = "shoot"

    def __init__(self, ammo: int):
        self.ammo = ammo


class AmmoCollectedEvent(XBoingEvent):
    """Event fired when ammo is collected."""

    sound_effect = "ammo"

    def __init__(self, ammo: int = 4):
        self.ammo = ammo


class BlockHitEvent(XBoingEvent):
    """Event: Ball hit a block."""

    sound_effect = "touch"


class UIButtonClickEvent(XBoingEvent):
    """Event: UI button or menu click."""

    sound_effect = "click"


class PowerUpCollectedEvent(XBoingEvent):
    """Event: Power-up collected."""

    sound_effect = "powerup"


class GameOverEvent(XBoingEvent):
    """Event: Game over."""

    sound_effect = "game_over"


class BallShotEvent(XBoingEvent):
    """Event: Ball launched from paddle."""

    sound_effect = "ballshot"


class BallLostEvent(XBoingEvent):
    """Event: Ball lost (missed by paddle)."""

    sound_effect = "balllost"


class BombExplodedEvent(XBoingEvent):
    """Event: Bomb block exploded."""

    sound_effect = "bomb"


class ApplauseEvent(XBoingEvent):
    """Event: Level complete, applause sound."""

    sound_effect = "applause"


class BonusCollectedEvent(XBoingEvent):
    """Event: Bonus collected."""

    sound_effect = "bonus"


class PaddleHitEvent(XBoingEvent):
    """Event: Ball hit the paddle."""

    sound_effect = "paddle"


class WallHitEvent(XBoingEvent):
    """Event: Ball hit the wall (for special wall collision sound handling)."""

    sound_effect = "boing"


class ScoreChangedEvent(XBoingEvent):
    """Event: Score changed (for UI updates)."""

    def __init__(self, score: int) -> None:
        """Initialize with the new score value."""
        self.score: int = score


class LivesChangedEvent(XBoingEvent):
    """Event: Lives changed (gain or loss, for UI updates)."""

    def __init__(self, lives: int) -> None:
        """Initialize with the new lives value."""
        self.lives: int = lives


class LevelChangedEvent(XBoingEvent):
    """Event: Level changed (for UI updates)."""

    def __init__(self, level: int) -> None:
        """Initialize with the new level value."""
        self.level: int = level


class TimerUpdatedEvent(XBoingEvent):
    """Event: Timer updated (for UI updates)."""

    def __init__(self, time_remaining: int) -> None:
        """Initialize with the new time remaining value."""
        self.time_remaining: int = time_remaining


class MessageChangedEvent(XBoingEvent):
    """Event: Message window content changed (for UI updates)."""

    def __init__(
        self,
        message: str,
        color: Tuple[int, int, int] = (0, 255, 0),
        alignment: str = "left",
    ) -> None:
        """Initialize with the message, color, and alignment."""
        self.message: str = message
        self.color: Tuple[int, int, int] = color
        self.alignment: str = alignment


class SpecialReverseChangedEvent(XBoingEvent):
    """Event: Special 'reverse' state changed."""

    sound_effect = "warp"

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialStickyChangedEvent(XBoingEvent):
    """Event: Special 'sticky' state changed (for UI and sound)."""

    sound_effect = "sticky"

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialSaveChangedEvent(XBoingEvent):
    """Event: Special 'save' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialFastGunChangedEvent(XBoingEvent):
    """Event: Special 'fastgun' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialNoWallChangedEvent(XBoingEvent):
    """Event: Special 'nowall' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialKillerChangedEvent(XBoingEvent):
    """Event: Special 'killer' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialX2ChangedEvent(XBoingEvent):
    """Event: Special 'x2' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialX4ChangedEvent(XBoingEvent):
    """Event: Special 'x4' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class LevelCompleteEvent(XBoingEvent):
    """Event: Level completed."""


class PaddleGrowEvent(XBoingEvent):
    """Event: Paddle grew (expanded) in size (for UI updates, feedback, and sound).

    Args:
        size (int): The new paddle size (e.g., width or enum/int).
        at_max (bool): True if the paddle is at its maximum size.

    """

    sound_effect = "wzzz"

    def __init__(self, size: int, at_max: bool = False) -> None:
        self.size: int = size
        self.at_max: bool = at_max


class PaddleShrinkEvent(XBoingEvent):
    """Event: Paddle shrank (reduced) in size (for UI updates, feedback, and sound).

    Args:
        size (int): The new paddle size (e.g., width or enum/int).
        at_min (bool): True if the paddle is at its minimum size.

    """

    sound_effect = "wzzz2"

    def __init__(self, size: int, at_min: bool = False) -> None:
        self.size: int = size
        self.at_min: bool = at_min


def post_level_title_message(level_title: str) -> None:
    """Post a MessageChangedEvent for the given level title with standard color and alignment."""
    pygame.event.post(
        pygame.event.Event(
            pygame.USEREVENT,
            {
                "event": MessageChangedEvent(
                    level_title, color=(0, 255, 0), alignment="left"
                )
            },
        )
    )


SPECIAL_EVENT_MAP = {
    "reverse": SpecialReverseChangedEvent,
    "sticky": SpecialStickyChangedEvent,
    "save": SpecialSaveChangedEvent,
    "fastgun": SpecialFastGunChangedEvent,
    "nowall": SpecialNoWallChangedEvent,
    "killer": SpecialKillerChangedEvent,
    "x2": SpecialX2ChangedEvent,
    "x4": SpecialX4ChangedEvent,
}
