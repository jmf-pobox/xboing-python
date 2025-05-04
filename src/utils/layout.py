"""
Layout and window management utilities for XBoing.

This module provides classes and functions to create and manage the game
window layout, mimicking the original XBoing window hierarchy.
"""

import os
from dataclasses import dataclass

import pygame

from src.utils.asset_paths import get_backgrounds_dir


@dataclass
class Rect:
    """A simple rectangle class representing a window or region."""

    x: int
    y: int
    width: int
    height: int

    @property
    def rect(self):
        """Get a pygame Rect object for this rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def center(self):
        """Get the center coordinates of this rectangle."""
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def centerx(self):
        """Get the center x coordinate of this rectangle."""
        return self.x + self.width // 2

    @property
    def centery(self):
        """Get the center y coordinate of this rectangle."""
        return self.y + self.height // 2


class GameWindow:
    """
    Represents a game window or region within the main surface.

    This class is used to mimic the original XBoing window hierarchy
    by creating virtual windows within the main Pygame surface.
    """

    def __init__(self, rect, name="", parent=None, bg_color=None):
        """
        Initialize a game window.

        Args:
            rect (Rect): The position and size of the window
            name (str): Window name for debugging
            parent (GameWindow): Parent window if this is a child window
            bg_color (tuple): RGB background color
        """
        self.rect = rect
        self.name = name
        self.parent = parent
        self.bg_color = bg_color
        self.bg_surface = None
        self.children = []
        self.visible = True

        # Add this window to its parent's children
        if parent:
            parent.add_child(self)

    def add_child(self, child):
        """Add a child window."""
        self.children.append(child)

    def set_background(self, bg):
        """
        Set the window background.

        Args:
            bg: Either a color tuple (r,g,b) or a surface to use as background
        """
        if isinstance(bg, tuple) and len(bg) >= 3:
            # It's a color
            self.bg_color = bg
            self.bg_surface = None
        elif isinstance(bg, pygame.Surface):
            # It's a surface
            self.bg_surface = bg

    def set_background_pixmap(self, pixmap):
        """
        Set a tiled background pixmap for the window.

        Args:
            pixmap (pygame.Surface): Image to tile as background
        """
        if not pixmap:
            return

        # Create a surface for the tiled background
        bg = pygame.Surface((self.rect.width, self.rect.height))

        # Tile the background image
        for y in range(0, self.rect.height, pixmap.get_height()):
            for x in range(0, self.rect.width, pixmap.get_width()):
                bg.blit(pixmap, (x, y))

        self.bg_surface = bg

    def draw(self, surface):
        """
        Draw this window and all its children.

        Args:
            surface (pygame.Surface): The surface to draw on
        """
        if not self.visible:
            return

        # Draw this window's background
        if self.bg_surface:
            # Use background surface
            surface.blit(self.bg_surface, (self.rect.x, self.rect.y))
        elif self.bg_color:
            # Use solid color
            pygame.draw.rect(surface, self.bg_color, self.rect.rect)

        # Draw children
        for child in self.children:
            child.draw(surface)


class GameLayout:
    """
    Manages the game window layout.

    This class creates and manages the hierarchy of game windows,
    mimicking the original XBoing window structure.
    """

    def __init__(self, width, height):
        """
        Initialize the game layout.

        Args:
            width (int): Main window width
            height (int): Main window height
        """
        self.width = width
        self.height = height

        # Constants matching the original XBoing layout
        self.PLAY_WIDTH = 495  # Original game's play area width
        self.PLAY_HEIGHT = 580  # Original game's play area height
        self.MAIN_WIDTH = 70  # Width of side panel
        self.MAIN_HEIGHT = 130  # Height of additional UI elements

        # Create the window hierarchy
        self._create_windows()

    def _create_windows(self):
        """Create the window hierarchy."""
        # Main window (entire screen)
        self.main_window = GameWindow(
            Rect(0, 0, self.width, self.height),
            name="mainWindow",
            bg_color=(0, 0, 0),  # Black background
        )

        # Layout constants - these match the original XBoing values
        offsetX = self.MAIN_WIDTH // 2
        offsetY = self.MAIN_HEIGHT // 2
        score_width = 224
        mess_height = 30

        # Score window
        self.score_window = GameWindow(
            Rect(offsetX, 10, score_width, 42),
            name="scoreWindow",
            parent=self.main_window,
            bg_color=None,  # Transparent/parent background
        )

        # Level window
        self.level_window = GameWindow(
            Rect(
                score_width + offsetX + 25,
                5,
                self.PLAY_WIDTH + offsetX - 20 - score_width,
                52,
            ),
            name="levelWindow",
            parent=self.main_window,
            bg_color=None,  # Transparent/parent background
        )

        # Play window (main game area)
        self.play_window = GameWindow(
            Rect(offsetX, 60, self.PLAY_WIDTH, self.PLAY_HEIGHT),
            name="playWindow",
            parent=self.main_window,
            bg_color=(0, 0, 0),  # Black by default
        )

        # Message window
        self.mess_window = GameWindow(
            Rect(
                offsetX, 65 + self.PLAY_HEIGHT + 10, self.PLAY_WIDTH // 2, mess_height
            ),
            name="messWindow",
            parent=self.main_window,
            bg_color=None,  # Transparent/parent background
        )

        # Special window (for bonus displays)
        self.special_window = GameWindow(
            Rect(
                offsetX + self.PLAY_WIDTH // 2 + 10,
                65 + self.PLAY_HEIGHT + 10,
                180,
                mess_height + 5,
            ),
            name="specialWindow",
            parent=self.main_window,
            bg_color=None,  # Transparent/parent background
        )

        # Time window
        self.time_window = GameWindow(
            Rect(
                offsetX + self.PLAY_WIDTH // 2 + 10 + 180 + 5,
                65 + self.PLAY_HEIGHT + 10,
                self.PLAY_WIDTH // 8,
                mess_height + 5,
            ),
            name="timeWindow",
            parent=self.main_window,
            bg_color=None,  # Transparent/parent background
        )

    def load_backgrounds(self, background_dir=None):
        """
        Load background images.

        Args:
            background_dir (str, optional): Directory containing background images.
                If None, uses the default backgrounds directory.
        """
        # Use the provided background directory or get the default
        if background_dir is None:
            background_dir = get_backgrounds_dir()

        print(f"Loading backgrounds from: {background_dir}")

        # Determine background image paths
        bg_path = os.path.join(background_dir, "bgrnd.png")
        space_path = os.path.join(background_dir, "space.png")

        # Load backgrounds if available
        try:
            # Load main background (space)
            if os.path.exists(space_path):
                space_bg = pygame.image.load(space_path).convert()
                self.main_window.set_background_pixmap(space_bg)
                print(f"Loaded main background: {space_path}")
            else:
                self.main_window.set_background((20, 20, 30))  # Dark blue-gray fallback
                print("Using fallback color for main background (space.png not found)")

            # Load play window background
            if os.path.exists(bg_path):
                play_bg = pygame.image.load(bg_path).convert()
                self.play_window.set_background_pixmap(play_bg)
                print(f"Loaded play background: {bg_path}")
            else:
                self.play_window.set_background((40, 40, 50))  # Darker fallback
                print("Using fallback color for play background (bgrnd.png not found)")

        except pygame.error as e:
            print(f"Error loading background images: {e}")

    def draw(self, surface):
        """
        Draw the entire window hierarchy.

        Args:
            surface (pygame.Surface): The surface to draw on
        """
        self.main_window.draw(surface)

    def get_play_rect(self):
        """Get the rectangle for the play area."""
        return self.play_window.rect.rect

    def get_score_rect(self):
        """Get the rectangle for the score area."""
        return self.score_window.rect.rect

    def get_level_rect(self):
        """Get the rectangle for the level info area."""
        return self.level_window.rect.rect

    def get_message_rect(self):
        """Get the rectangle for the message area."""
        return self.mess_window.rect.rect

    def set_play_background(self, bg_type):
        """
        Set the play area background.

        Args:
            bg_type (int): Background type (0-5)
        """
        # Get background directory path
        backgrounds_dir = get_backgrounds_dir()

        # Determine the background file
        # Map background types correctly to file names:
        # bg_type 0 -> bgrnd2.png (BACKGROUND_2 in original game)
        # bg_type 1 -> bgrnd3.png (BACKGROUND_3 in original game)
        # bg_type 2 -> bgrnd4.png (BACKGROUND_4 in original game)
        # bg_type 3 -> bgrnd5.png (BACKGROUND_5 in original game)

        # The pattern is: bg_type + 2 for the number in the filename
        bg_file = f"bgrnd{bg_type+2}.png"

        bg_path = os.path.join(backgrounds_dir, bg_file)

        # Check if the file exists
        if not os.path.exists(bg_path):
            print(f"Warning: Background image not found: {bg_path}")
            return

        try:
            # Load the background image
            bg_img = pygame.image.load(bg_path).convert()

            # Set the play window background
            self.play_window.set_background_pixmap(bg_img)
            print(f"Set play area background to: {bg_file}")
        except Exception as e:
            print(f"Error loading background image: {e}")
