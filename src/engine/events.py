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

    def __init__(self, score):
        self.score = score


class LivesChangedEvent:
    """Event: Lives changed (gain or loss, for UI updates)."""

    def __init__(self, lives):
        self.lives = lives


class LevelChangedEvent:
    """Event: Level changed (for UI updates)."""

    def __init__(self, level):
        self.level = level


class TimerUpdatedEvent:
    """Event: Timer updated (for UI updates)."""

    def __init__(self, time_remaining):
        self.time_remaining = time_remaining


class MessageChangedEvent:
    """Event: Message window content changed (for UI updates)."""

    def __init__(self, message, color=(0, 255, 0), alignment="left"):
        self.message = message
        self.color = color
        self.alignment = alignment


class SpecialReverseChangedEvent:
    def __init__(self, active: bool):
        self.active = active


class SpecialStickyChangedEvent:
    def __init__(self, active: bool):
        self.active = active


class SpecialSaveChangedEvent:
    def __init__(self, active: bool):
        self.active = active


class SpecialFastGunChangedEvent:
    def __init__(self, active: bool):
        self.active = active


class SpecialNoWallChangedEvent:
    def __init__(self, active: bool):
        self.active = active


class SpecialKillerChangedEvent:
    def __init__(self, active: bool):
        self.active = active


class SpecialX2ChangedEvent:
    def __init__(self, active: bool):
        self.active = active


class SpecialX4ChangedEvent:
    def __init__(self, active: bool):
        self.active = active


class LevelCompleteEvent:
    pass
