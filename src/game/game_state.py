import logging
import pygame

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
    def __init__(self):
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

    def add_score(self, points):
        self.score += points
        self.logger.info(f"Score increased by {points}, new score: {self.score}")
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": ScoreChangedEvent(self.score)}))

    def set_score(self, score):
        self.score = score
        self.logger.info(f"Score set to {self.score}")
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": ScoreChangedEvent(self.score)}))

    def lose_life(self):
        self.lives -= 1
        self.logger.info(f"Life lost, remaining lives: {self.lives}")
        if self.lives <= 0:
            self.set_game_over(True)
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": GameOverEvent()}))
        else:
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": LivesChangedEvent(self.lives)}))

    def set_lives(self, lives):
        self.lives = lives
        self.logger.info(f"Lives set to {self.lives}")
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": LivesChangedEvent(self.lives)}))

    def set_level(self, level):
        self.level = level
        self.logger.info(f"Level set to {self.level}")
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": LevelChangedEvent(self.level)}))

    def set_timer(self, time_remaining):
        self.timer = time_remaining
        self.logger.debug(f"Timer set to {self.timer}")
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": TimerUpdatedEvent(self.timer)}))

    def set_special(self, name, value):
        if name in self.specials and self.specials[name] != value:
            self.specials[name] = value
            self.logger.info(f"Special '{name}' set to {value}")
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": self._event_map[name](value)}))

    def get_special(self, name):
        return self.specials.get(name, False)

    def set_game_over(self, value: bool):
        if self.game_over != value:
            self.game_over = value
            self.logger.info(f"Game over set to {self.game_over}")
            if value:
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": GameOverEvent()}))

    def is_game_over(self):
        return self.game_over

    def restart(self):
        self.logger.info("Game state restarted")
        self.game_over = False
        self.set_score(0)
        self.set_lives(3)
        self.set_level(1)
        self.set_timer(0)
        self.set_game_over(False)
        for name in self.specials:
            self.set_special(name, False)

    def full_restart(self, level_manager):
        """
        Reset all game state, load the level, set timer from level manager, and fire the level title message.
        """
        self.logger.info("Full game state restart")
        self.game_over = False
        self.set_score(0)
        self.set_lives(3)
        self.set_level(1)
        for name in self.specials:
            self.set_special(name, False)
        level_manager.load_level(self.level)
        self.set_timer(level_manager.get_time_remaining())
        level_info = level_manager.get_level_info()
        level_title = level_info["title"]
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": MessageChangedEvent(level_title, color=(0, 255, 0), alignment="left")}))

    # Optionally, add more methods for other state changes as needed
