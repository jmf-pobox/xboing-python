"""
Paddle implementation for XBoing.

This module contains the paddle class that manages the player-controlled paddle
and its interactions with the game, matching the original XBoing implementation.
"""

import logging
import os

import pygame
from utils.asset_paths import get_paddles_dir

# Setup logging
logger = logging.getLogger("xboing.paddle")


class Paddle:
    """The player-controlled paddle."""

    # Paddle sizes - match original XBoing constants
    SIZE_SMALL = 0  # Corresponds to PADDLE_SMALL in original
    SIZE_MEDIUM = 1  # Corresponds to PADDLE_MEDIUM in original
    SIZE_LARGE = 2  # Corresponds to PADDLE_HUGE in original

    # Distance from bottom of play area to paddle (original XBoing value)
    DIST_BASE = 30  # Matches the original C code's DIST_BASE constant

    def __init__(self, x, y, width, height, speed=10):
        """
        Initialize the paddle.

        Args:
            x (int): Starting X position
            y (int): Y position (usually fixed)
            width (int): Paddle width
            height (int): Paddle height
            speed (int): Movement speed in pixels per frame
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.size = (
            self.SIZE_LARGE
        )  # Start with the large paddle to match original game
        self.moving = False
        self.direction = 0  # -1 for left, 0 for none, 1 for right
        self.sticky = False  # For the sticky powerup
        self.old_x = x  # For replicating the original paddle movement logic

        # Load paddle sprites
        self._load_sprites()

        # Get the current paddle sprite and dimensions
        self._update_rect_size()

    def _load_sprites(self):
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
            self.paddle_images = {
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

    def _update_rect_size(self):
        """Update the rectangle size based on current paddle size."""
        width, height = self.paddle_dimensions[self.size]
        self.rect = pygame.Rect(
            int(self.x - width // 2),  # Center the paddle horizontally
            int(self.y),
            width,
            height,
        )
        self.width = width

    def update(self, delta_ms, play_width, offset_x=0):
        """
        Update paddle position.

        Args:
            delta_ms (float): Time since last frame in milliseconds
            play_width (int): Play area width for boundary checking
            offset_x (int): X offset of the play area
        """
        if self.direction != 0:
            self.moving = True

            # Calculate movement with framerate independence
            move_amount = self.speed * (delta_ms / 16.67)  # Normalized for 60 FPS

            # Update position
            self.x += self.direction * move_amount
        else:
            self.moving = False

        # Get half the width of the current paddle size
        paddle_half_width = self.paddle_dimensions[self.size][0] // 2

        # Boundary checking within play area
        # Keep the paddle within the play area bounds (matching original logic)
        if self.x < paddle_half_width + offset_x:
            self.x = paddle_half_width + offset_x
        if self.x > offset_x + play_width - paddle_half_width:
            self.x = offset_x + play_width - paddle_half_width

        # Update rectangle
        self.rect.x = int(self.x - paddle_half_width)
        self.rect.y = int(self.y)

    def set_direction(self, direction):
        """
        Set paddle movement direction.

        Args:
            direction (int): -1 for left, 0 for none, 1 for right
        """
        self.direction = direction

    def move_to(self, x, play_width, offset_x=0):
        """
        Move paddle to a specific x position.

        Args:
            x (int): Target X position relative to play area
            play_width (int): Play area width for boundary checking
            offset_x (int): X offset of the play area
        """
        # Replicate original XBoing logic for paddle positioning
        self.x = offset_x + x

        # Get half the width of the current paddle size
        paddle_half_width = self.paddle_dimensions[self.size][0] // 2

        # Boundary checking
        if self.x < paddle_half_width + offset_x:
            self.x = paddle_half_width + offset_x
        if self.x > offset_x + play_width - paddle_half_width:
            self.x = offset_x + play_width - paddle_half_width

        # Update rectangle
        self.rect.x = int(self.x - paddle_half_width)

    def set_size(self, size):
        """
        Set paddle size.

        Args:
            size (int): SIZE_SMALL, SIZE_MEDIUM, or SIZE_LARGE
        """
        if size in self.paddle_dimensions:
            # Store center position
            center_x = self.x

            # Change size
            self.size = size

            # Update rectangle with new size, maintaining center position
            self._update_rect_size()
            self.rect.x = int(center_x - self.rect.width // 2)

    def toggle_sticky(self):
        """Toggle sticky paddle state."""
        self.sticky = not self.sticky

    def is_sticky(self):
        """Check if the paddle is sticky."""
        return self.sticky

    def draw(self, surface):
        """
        Draw the paddle.

        Args:
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

        # If sticky, add a visual indicator
        if self.sticky:
            # Draw a small indicator that the paddle is sticky
            indicator_rect = pygame.Rect(self.rect.centerx - 5, self.rect.y - 5, 10, 5)
            pygame.draw.rect(surface, (255, 255, 0), indicator_rect)

    def get_rect(self):
        """Get the paddle's rectangle for collision detection."""
        return self.rect

    def get_center(self):
        """Get the center position of the paddle."""
        return self.rect.center
