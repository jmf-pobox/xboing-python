"""Paddle implementation for XBoing.

This module contains the paddle class that manages the player-controlled paddle
and its interactions with the game, matching the original XBoing implementation.
"""

import logging
import os
from typing import Any, Dict, Optional

import pygame

from xboing.game.game_shape import GameShape
from xboing.utils.asset_paths import get_paddles_dir

# Setup logging
logger = logging.getLogger("xboing.paddle")


class Paddle(GameShape):
    """The player-controlled paddle."""

    # Paddle sizes - match original XBoing constants
    SIZE_SMALL = 0  # Corresponds to PADDLE_SMALL in original
    SIZE_MEDIUM = 1  # Corresponds to PADDLE_MEDIUM in original
    SIZE_LARGE = 2  # Corresponds to PADDLE_HUGE in original

    # Distance from bottom of play area to paddle (original XBoing value)
    DIST_BASE = 30  # Matches the original C code's DIST_BASE constant

    def __init__(self, x: int, y: int, speed: int = 10) -> None:
        """Initialize the paddle at SIZE_LARGE with correct dimensions.

        Args:
            x (int): Starting X position
            y (int): Y position (usually fixed)
            speed (int): Movement speed in pixels per frame

        """
        self.size = self.SIZE_LARGE  # Start with the large paddle
        # Temporarily use large paddle dimensions for base class init
        temp_width, temp_height = 70, 15  # Fallback if assets not loaded yet
        super().__init__(x, y, temp_width, temp_height)
        self.speed = speed
        self.moving = False
        self.direction = 0  # -1 for left, 0 for none, 1 for right
        self.sticky = False  # For the sticky powerup
        self.old_x = x  # For replicating the original paddle movement logic

        # Load paddle sprites
        self._load_sprites()

        # Update rect to match actual loaded dimensions
        self.update_rect()

    def _load_sprites(self) -> None:
        """Load paddle sprites from assets."""
        paddle_dir = get_paddles_dir()
        logger.info(f"Loading paddle sprites from: {paddle_dir}")

        try:
            # Load the paddle images
            small_path = os.path.join(paddle_dir, "padsml.png")
            medium_path = os.path.join(paddle_dir, "padmed.png")
            large_path = os.path.join(paddle_dir, "padhuge.png")

            logger.info(f"Loading small paddle: {small_path}")
            logger.info(f"Loading medium paddle: {medium_path}")
            logger.info(f"Loading large paddle: {large_path}")

            # Check if files exist
            if not os.path.exists(small_path):
                logger.error(f"Small paddle sprite not found: {small_path}")
            if not os.path.exists(medium_path):
                logger.error(f"Medium paddle sprite not found: {medium_path}")
            if not os.path.exists(large_path):
                logger.error(f"Large paddle sprite not found: {large_path}")

            # Load the paddle images
            self.paddle_images: Optional[Dict[int, pygame.Surface]] = {
                self.SIZE_SMALL: pygame.image.load(small_path).convert_alpha(),
                self.SIZE_MEDIUM: pygame.image.load(medium_path).convert_alpha(),
                self.SIZE_LARGE: pygame.image.load(large_path).convert_alpha(),
            }

            # Get the dimensions of each paddle size from the images
            self.paddle_dimensions = {
                self.SIZE_SMALL: self.paddle_images[self.SIZE_SMALL].get_size(),
                self.SIZE_MEDIUM: self.paddle_images[self.SIZE_MEDIUM].get_size(),
                self.SIZE_LARGE: self.paddle_images[self.SIZE_LARGE].get_size(),
            }

            logger.info(
                f"Paddle dimensions - Small: {self.paddle_dimensions[self.SIZE_SMALL]}, "
                f"Medium: {self.paddle_dimensions[self.SIZE_MEDIUM]}, "
                f"Large: {self.paddle_dimensions[self.SIZE_LARGE]}"
            )

        except Exception as e:
            logger.error(f"Error loading paddle sprites: {e}")
            # Fall back to simple rectangles with exact dimensions from original XPM files
            logger.warning(
                "Falling back to simple rectangle paddles with original dimensions"
            )
            self.paddle_images = None
            # Use exact dimensions from original XPM files
            self.paddle_dimensions = {
                self.SIZE_SMALL: (40, 15),  # padsml.xpm: 40x15
                self.SIZE_MEDIUM: (50, 15),  # padmed.xpm: 50x15
                self.SIZE_LARGE: (70, 15),  # padhuge.xpm: 70x15
            }

    def update_rect(self) -> None:
        """Update the rectangle size and position based on current paddle size and position."""
        width, height = self.paddle_dimensions[self.size]
        self.rect.x = int(self.x - width // 2)
        self.rect.y = int(self.y)
        self.rect.width = width
        self.rect.height = height

    def update(self, delta_ms: float, play_width: int, offset_x: int = 0) -> None:
        """Update paddle position.

        Args:
        ----
            delta_ms (float): Time since last frame in milliseconds
            play_width (int): Play area width for boundary checking
            offset_x (int): X offset of the play area

        """
        if self.direction != 0:
            self.moving = True

            # Calculate movement with framerate independence
            move_amount = self.speed * (delta_ms / 16.67)  # Normalized for 60 FPS

            # Update position
            self.x += int(self.direction * move_amount)
        else:
            self.moving = False

        # Get half the width of the current paddle size
        paddle_half_width = self.paddle_dimensions[self.size][0] // 2

        # Boundary checking within play area
        # Keep the paddle within the play area bounds (matching original logic)
        self.x = max(self.x, paddle_half_width + offset_x)
        self.x = min(self.x, offset_x + play_width - paddle_half_width)

        # Update rectangle
        self.update_rect()

    def set_direction(self, direction: int) -> None:
        """Set paddle movement direction.

        Args:
        ----
            direction (int): -1 for left, 0 for none, 1 for right

        """
        self.direction = direction

    def move_to(self, x: int, play_width: int, offset_x: int = 0) -> None:
        """Move paddle to a specific x position.

        Args:
        ----
            x (int): Target X position relative to play area
            play_width (int): Play area width for boundary checking
            offset_x (int): X offset of the play area

        """
        # Replicate original XBoing logic for paddle positioning
        self.x = offset_x + x

        # Get half the width of the current paddle size
        paddle_half_width = self.paddle_dimensions[self.size][0] // 2

        # Boundary checking
        self.x = max(self.x, paddle_half_width + offset_x)
        self.x = min(self.x, offset_x + play_width - paddle_half_width)

        # Update rectangle
        self.update_rect()

    def set_size(self, size: int) -> None:
        """Set paddle size.

        Args:
        ----
            size (int): SIZE_SMALL, SIZE_MEDIUM, or SIZE_LARGE

        """
        if size in self.paddle_dimensions:
            # Store center position
            center_x = self.x

            # Change size
            self.size = size

            # Update rectangle with new size, maintaining center position
            self.x = center_x
            self.update_rect()

    def toggle_sticky(self) -> None:
        """Toggle sticky paddle state."""
        self.sticky = not self.sticky

    def is_sticky(self) -> bool:
        """Check if the paddle is sticky."""
        return self.sticky

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the paddle.

        Args:
        ----
            surface (pygame.Surface): Surface to draw on

        """
        # Check if we have paddle images loaded
        if self.paddle_images:
            try:
                # Draw the appropriate paddle sprite at the correct position
                paddle_img = self.paddle_images[self.size]
                surface.blit(paddle_img, self.rect.topleft)
            except Exception as e:
                logger.error(f"Error drawing paddle sprite: {e}")
                # Fall back to rectangle if sprite can't be drawn
                pygame.draw.rect(surface, (200, 200, 200), self.rect)
                # Add a highlight effect on top
                highlight = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 2)
                pygame.draw.rect(surface, (255, 255, 255), highlight)
        else:
            # Draw a simple paddle with a highlight effect if no images are available
            pygame.draw.rect(surface, (200, 200, 200), self.rect)
            # Add a highlight effect on top
            highlight = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 2)
            pygame.draw.rect(surface, (255, 255, 255), highlight)
            # Draw a border around the paddle for better visibility
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 1)

    def get_rect(self) -> pygame.Rect:
        """Get the paddle's rectangle for collision detection."""
        return self.rect

    def get_center(self) -> Any:
        """Get the center position of the paddle."""
        return self.rect.center
