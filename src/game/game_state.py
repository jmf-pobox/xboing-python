from engine.events import (
    GameOverEvent,
    LevelChangedEvent,
    LivesChangedEvent,
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
    def __init__(self, event_bus):
        self.event_bus = event_bus
        self.score = 0
        self.lives = 3
        self.level = 1
        self.timer = 0
        self.game_over = False
        self.specials = {
            'reverse': False,
            'sticky': False,
            'save': False,
            'fastgun': False,
            'nowall': False,
            'killer': False,
            'x2': False,
            'x4': False,
        }
        self._event_map = {
            'reverse': SpecialReverseChangedEvent,
            'sticky': SpecialStickyChangedEvent,
            'save': SpecialSaveChangedEvent,
            'fastgun': SpecialFastGunChangedEvent,
            'nowall': SpecialNoWallChangedEvent,
            'killer': SpecialKillerChangedEvent,
            'x2': SpecialX2ChangedEvent,
            'x4': SpecialX4ChangedEvent,
        }

    def add_score(self, points):
        self.score += points
        self.event_bus.fire(ScoreChangedEvent(self.score))

    def set_score(self, score):
        self.score = score
        self.event_bus.fire(ScoreChangedEvent(self.score))

    def lose_life(self):
        self.lives -= 1
        self.event_bus.fire(LivesChangedEvent(self.lives))

    def set_lives(self, lives):
        self.lives = lives
        self.event_bus.fire(LivesChangedEvent(self.lives))

    def set_level(self, level):
        self.level = level
        self.event_bus.fire(LevelChangedEvent(self.level))

    def set_timer(self, time_remaining):
        self.timer = time_remaining
        self.event_bus.fire(TimerUpdatedEvent(self.timer))

    def set_special(self, name, value):
        if name in self.specials and self.specials[name] != value:
            self.specials[name] = value
            self.event_bus.fire(self._event_map[name](value))

    def get_special(self, name):
        return self.specials.get(name, False)

    def set_game_over(self, value: bool):
        if self.game_over != value:
            self.game_over = value
            if value:
                self.event_bus.fire(GameOverEvent())

    def is_game_over(self):
        return self.game_over

    def restart(self):
        self.game_over = False
        self.set_score(0)
        self.set_lives(3)
        self.set_level(1)
        self.set_timer(0)
        self.set_game_over(False)
        for name in self.specials:
            self.set_special(name, False)

    # Optionally, add more methods for other state changes as needed 