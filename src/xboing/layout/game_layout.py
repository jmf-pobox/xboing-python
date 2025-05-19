"""GameLayout and GameWindow: Define and manage the spatial window hierarchy and region layout for XBoing."""

from dataclasses import dataclass
import logging
import os
from typing import Any, List, Optional, Tuple

import pygame

from xboing.utils.asset_loader import load_image
from xboing.utils.asset_paths import get_backgrounds_dir


@dataclass
class Rect:
    """A simple rectangle class representing a window or region."""

    x: int
    y: int
    width: int
    height: int

    @property
    def rect(self) -> pygame.Rect:
        """Return a pygame.Rect representation of this rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def center(self) -> Tuple[int, int]:
        """Return the center (x, y) of the rectangle."""
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def centerx(self) -> int:
        """Return the x-coordinate of the center of the rectangle."""
        return self.x + self.width // 2

    @property
    def centery(self) -> int:
        """Return the y-coordinate of the center of the rectangle."""
        return self.y + self.height // 2


class GameWindow:
    """Represents a game window or region within the main surface."""

    rect: Rect
    name: str
    parent: Optional["GameWindow"]
    bg_color: Optional[Tuple[int, int, int]]
    bg_surface: Optional[pygame.Surface]
    children: List["GameWindow"]
    visible: bool
    MIN_COLOR_TUPLE_LEN = 3  # Minimum length for an RGB color tuple

    def __init__(
        self,
        rect: Rect,
        name: str = "",
        parent: Optional["GameWindow"] = None,
        bg_color: Optional[Tuple[int, int, int]] = None,
    ) -> None:
        """Initialize a GameWindow.

        Args:
        ----
            rect: The rectangle defining the window's position and size.
            name: The name of the window.
            parent: The parent GameWindow, if any.
            bg_color: The background color as an (R, G, B) tuple, if any.

        """
        self.rect = rect
        self.name = name
        self.parent = parent
        self.bg_color = bg_color
        self.bg_surface = None
        self.children = []
        self.visible = True
        if parent:
            parent.add_child(self)

    def add_child(self, child: "GameWindow") -> None:
        """Add a child GameWindow to this window."""
        self.children.append(child)

    def set_background(self, bg: Any) -> None:
        """Set the background color or surface for this window."""
        if isinstance(bg, tuple) and len(bg) >= self.MIN_COLOR_TUPLE_LEN:
            self.bg_color = bg
            self.bg_surface = None
        elif isinstance(bg, pygame.Surface):
            self.bg_surface = bg

    def set_background_pixmap(self, pixmap: Optional[pygame.Surface]) -> None:
        """Set a tiled background pixmap for this window."""
        if not pixmap:
            return
        bg = pygame.Surface((self.rect.width, self.rect.height))
        for y in range(0, self.rect.height, pixmap.get_height()):
            for x in range(0, self.rect.width, pixmap.get_width()):
                bg.blit(pixmap, (x, y))
        self.bg_surface = bg

    def draw(self, surface: pygame.Surface) -> None:
        """Draw this window and its children onto the given surface."""
        if not self.visible:
            return
        if self.bg_surface:
            surface.blit(self.bg_surface, (self.rect.x, self.rect.y))
        elif self.bg_color:
            pygame.draw.rect(surface, self.bg_color, self.rect.rect)
        for child in self.children:
            child.draw(surface)


class GameLayout:
    """Manages the game window layout and provides access to all UI region rectangles."""

    def __init__(self, width: int, height: int) -> None:
        """Initialize the GameLayout with the given width and height."""
        self.logger = logging.getLogger("xboing.GameLayout")
        self.width = width
        self.height = height
        self.play_width = 495
        self.play_height = 580
        self.main_width = 70
        self.main_height = 130
        self._create_windows()

    def _create_windows(self) -> None:
        """Create all GameWindow regions for the layout."""
        self.main_window = GameWindow(
            Rect(0, 0, self.width, self.height),
            name="mainWindow",
            bg_color=(0, 0, 0),
        )
        offset_x = self.main_width // 2
        score_width = 224
        mess_height = 30
        self.score_window = GameWindow(
            Rect(offset_x, 10, score_width, 42),
            name="scoreWindow",
            parent=self.main_window,
            bg_color=None,
        )
        self.level_window = GameWindow(
            Rect(
                score_width + offset_x + 25,
                5,
                self.play_width + offset_x - 20 - score_width,
                52,
            ),
            name="levelWindow",
            parent=self.main_window,
            bg_color=None,
        )
        self.play_window = GameWindow(
            Rect(offset_x, 60, self.play_width, self.play_height),
            name="playWindow",
            parent=self.main_window,
            bg_color=(0, 0, 0),
        )
        self.mess_window = GameWindow(
            Rect(
                offset_x + 35,
                50 + self.play_height + 10,
                self.play_width // 2,
                mess_height,
            ),
            name="messWindow",
            parent=self.main_window,
            bg_color=None,
        )
        self.special_window = GameWindow(
            Rect(
                offset_x + self.play_width // 2 + 10,
                65 + self.play_height + 10,
                180,
                mess_height + 5,
            ),
            name="specialWindow",
            parent=self.main_window,
            bg_color=None,
        )
        self.time_window = GameWindow(
            Rect(
                offset_x - 5 + self.play_width // 2 + 10 + 180 + 5,
                65 + self.play_height + 10,
                self.play_width // 8,
                mess_height + 5,
            ),
            name="timeWindow",
            parent=self.main_window,
            bg_color=None,
        )

    def load_backgrounds(self, background_dir: Optional[str] = None) -> None:
        """Load background images for the main and play windows."""
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

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the entire layout onto the given surface."""
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

    def set_play_background(self, bg_type: int) -> None:
        """Set the play area background to a specific type by loading the corresponding image."""
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
