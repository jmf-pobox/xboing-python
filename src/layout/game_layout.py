"""
GameLayout and GameWindow: Define and manage the spatial window hierarchy and region layout for XBoing.
This is the authoritative source for all UI region positions and backgrounds.
"""

import logging
import os
from dataclasses import dataclass

import pygame

from utils.asset_loader import load_image
from utils.asset_paths import get_backgrounds_dir


@dataclass
class Rect:
    """A simple rectangle class representing a window or region."""

    x: int
    y: int
    width: int
    height: int

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def center(self):
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def centerx(self):
        return self.x + self.width // 2

    @property
    def centery(self):
        return self.y + self.height // 2


class GameWindow:
    """
    Represents a game window or region within the main surface.
    """

    def __init__(self, rect, name="", parent=None, bg_color=None):
        self.rect = rect
        self.name = name
        self.parent = parent
        self.bg_color = bg_color
        self.bg_surface = None
        self.children = []
        self.visible = True
        if parent:
            parent.add_child(self)

    def add_child(self, child):
        self.children.append(child)

    def set_background(self, bg):
        if isinstance(bg, tuple) and len(bg) >= 3:
            self.bg_color = bg
            self.bg_surface = None
        elif isinstance(bg, pygame.Surface):
            self.bg_surface = bg

    def set_background_pixmap(self, pixmap):
        if not pixmap:
            return
        bg = pygame.Surface((self.rect.width, self.rect.height))
        for y in range(0, self.rect.height, pixmap.get_height()):
            for x in range(0, self.rect.width, pixmap.get_width()):
                bg.blit(pixmap, (x, y))
        self.bg_surface = bg

    def draw(self, surface):
        if not self.visible:
            return
        if self.bg_surface:
            surface.blit(self.bg_surface, (self.rect.x, self.rect.y))
        elif self.bg_color:
            pygame.draw.rect(surface, self.bg_color, self.rect.rect)
        for child in self.children:
            child.draw(surface)


class GameLayout:
    """
    Manages the game window layout.
    """

    def __init__(self, width, height):
        self.logger = logging.getLogger("xboing.GameLayout")
        self.width = width
        self.height = height
        self.PLAY_WIDTH = 495
        self.PLAY_HEIGHT = 580
        self.MAIN_WIDTH = 70
        self.MAIN_HEIGHT = 130
        self._create_windows()

    def _create_windows(self):
        self.main_window = GameWindow(
            Rect(0, 0, self.width, self.height),
            name="mainWindow",
            bg_color=(0, 0, 0),
        )
        offsetX = self.MAIN_WIDTH // 2
        score_width = 224
        mess_height = 30
        self.score_window = GameWindow(
            Rect(offsetX, 10, score_width, 42),
            name="scoreWindow",
            parent=self.main_window,
            bg_color=None,
        )
        self.level_window = GameWindow(
            Rect(
                score_width + offsetX + 25,
                5,
                self.PLAY_WIDTH + offsetX - 20 - score_width,
                52,
            ),
            name="levelWindow",
            parent=self.main_window,
            bg_color=None,
        )
        self.play_window = GameWindow(
            Rect(offsetX, 60, self.PLAY_WIDTH, self.PLAY_HEIGHT),
            name="playWindow",
            parent=self.main_window,
            bg_color=(0, 0, 0),
        )
        self.mess_window = GameWindow(
            Rect(
                offsetX + 35,
                50 + self.PLAY_HEIGHT + 10,
                self.PLAY_WIDTH // 2,
                mess_height,
            ),
            name="messWindow",
            parent=self.main_window,
            bg_color=None,
        )
        self.special_window = GameWindow(
            Rect(
                offsetX + self.PLAY_WIDTH // 2 + 10,
                65 + self.PLAY_HEIGHT + 10,
                180,
                mess_height + 5,
            ),
            name="specialWindow",
            parent=self.main_window,
            bg_color=None,
        )
        self.time_window = GameWindow(
            Rect(
                offsetX - 5 + self.PLAY_WIDTH // 2 + 10 + 180 + 5,
                65 + self.PLAY_HEIGHT + 10,
                self.PLAY_WIDTH // 8,
                mess_height + 5,
            ),
            name="timeWindow",
            parent=self.main_window,
            bg_color=None,
        )

    def load_backgrounds(self, background_dir=None):
        if background_dir is None:
            background_dir = get_backgrounds_dir()
        self.logger.info(f"Loading backgrounds from: {background_dir}")
        bg_path = os.path.join(background_dir, "bgrnd.png")
        space_path = os.path.join(background_dir, "space.png")
        try:
            if os.path.exists(space_path):
                space_bg = load_image(space_path, alpha=False)
                self.main_window.set_background_pixmap(space_bg)
                self.logger.info(f"Loaded main background: {space_path}")
            else:
                self.main_window.set_background((20, 20, 30))
                self.logger.warning(
                    "Using fallback color for main background (space.png not found)"
                )
            if os.path.exists(bg_path):
                play_bg = load_image(bg_path, alpha=False)
                self.play_window.set_background_pixmap(play_bg)
                self.logger.info(f"Loaded play background: {bg_path}")
            else:
                self.play_window.set_background((40, 40, 50))
                self.logger.warning(
                    "Using fallback color for play background (bgrnd.png not found)"
                )
        except Exception as e:
            self.logger.error(f"Error loading background images: {e}")

    def draw(self, surface):
        self.main_window.draw(surface)

    def get_play_rect(self) -> pygame.Rect:
        """Return the play window rectangle as a pygame.Rect."""
        return self.play_window.rect.rect

    def get_score_rect(self) -> pygame.Rect:
        """Return the score window rectangle as a pygame.Rect."""
        return self.score_window.rect.rect

    def get_level_rect(self) -> pygame.Rect:
        """Return the level window rectangle as a pygame.Rect."""
        return self.level_window.rect.rect

    def get_message_rect(self) -> pygame.Rect:
        """Return the message window rectangle as a pygame.Rect."""
        return self.mess_window.rect.rect

    def get_timer_rect(self) -> pygame.Rect:
        """Return the timer window rectangle as a pygame.Rect."""
        return self.time_window.rect.rect

    def set_play_background(self, bg_type):
        backgrounds_dir = get_backgrounds_dir()
        bg_file = f"bgrnd{bg_type+2}.png"
        bg_path = os.path.join(backgrounds_dir, bg_file)
        if not os.path.exists(bg_path):
            self.logger.warning(f"Background image not found: {bg_path}")
            return
        try:
            bg_img = load_image(bg_path, alpha=False)
            self.play_window.set_background_pixmap(bg_img)
            self.logger.debug(f"Set play area background to: {bg_file}")
        except Exception as e:
            self.logger.error(f"Error loading background image: {e}")
