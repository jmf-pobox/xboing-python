from typing import Tuple


class BlockHitEvent:
    """Event: Ball hit a block."""

    pass


class UIButtonClickEvent:
    """Event: UI button or menu click."""

    pass


class PowerUpCollectedEvent:
    """Event: Power-up collected."""

    pass


class GameOverEvent:
    """Event: Game over."""

    pass


class BallShotEvent:
    """Event: Ball launched from paddle."""

    pass


class BallLostEvent:
    """Event: Ball lost (missed by paddle)."""

    pass


class BombExplodedEvent:
    """Event: Bomb block exploded."""

    pass


class ApplauseEvent:
    """Event: Level complete, applause sound."""

    pass


class BonusCollectedEvent:
    """Event: Bonus collected."""

    pass


class PaddleHitEvent:
    """Event: Ball hit the paddle."""

    pass


class WallHitEvent:
    """Event: Ball hit the wall (for special wall collision sound handling)."""

    pass


class ScoreChangedEvent:
    """Event: Score changed (for UI updates)."""

    def __init__(self, score: int) -> None:
        """Initialize with the new score value."""
        self.score: int = score


class LivesChangedEvent:
    """Event: Lives changed (gain or loss, for UI updates)."""

    def __init__(self, lives: int) -> None:
        """Initialize with the new lives value."""
        self.lives: int = lives


class LevelChangedEvent:
    """Event: Level changed (for UI updates)."""

    def __init__(self, level: int) -> None:
        """Initialize with the new level value."""
        self.level: int = level


class TimerUpdatedEvent:
    """Event: Timer updated (for UI updates)."""

    def __init__(self, time_remaining: int) -> None:
        """Initialize with the new time remaining value."""
        self.time_remaining: int = time_remaining


class MessageChangedEvent:
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


class SpecialReverseChangedEvent:
    """Event: Special 'reverse' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialStickyChangedEvent:
    """Event: Special 'sticky' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialSaveChangedEvent:
    """Event: Special 'save' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialFastGunChangedEvent:
    """Event: Special 'fastgun' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialNoWallChangedEvent:
    """Event: Special 'nowall' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialKillerChangedEvent:
    """Event: Special 'killer' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialX2ChangedEvent:
    """Event: Special 'x2' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class SpecialX4ChangedEvent:
    """Event: Special 'x4' state changed."""

    def __init__(self, active: bool) -> None:
        """Initialize with the active state."""
        self.active: bool = active


class LevelCompleteEvent:
    """Event: Level completed."""

    pass
