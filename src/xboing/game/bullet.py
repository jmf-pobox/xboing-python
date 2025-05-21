"""Bullet implementation for XBoing.

This module contains the Bullet class that handles projectile state and movement.
"""

import logging
from typing import Tuple

import pygame

from xboing.game.circular_game_shape import CircularGameShape

logger = logging.getLogger("xboing.Bullet")


class Bullet(CircularGameShape):
    """A projectile bullet fired by the paddle gun (inherits from CircularGameShape)."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float = 0.0,
        vy: float = -10.0,
        radius: int = 4,
        color: Tuple[int, int, int] = (255, 255, 0),
    ) -> None:
        """Initialize a new bullet.

        Args:
            x (float): Starting X position.
            y (float): Starting Y position.
            vx (float): X velocity.
            vy (float): Y velocity.
            radius (int): Bullet radius.
            color (Tuple[int, int, int]): RGB color tuple.

        """
        super().__init__(x, y, radius)
        self.vx: float = vx
        self.vy: float = vy
        self.color: Tuple[int, int, int] = color
        self.active: bool = True

    def update(self, delta_ms: float) -> None:
        """Update the bullet's position based on its velocity and the elapsed time."""
        old_x, old_y = self.x, self.y
        self.x += self.vx * (delta_ms / 16.67)
        self.y += self.vy * (delta_ms / 16.67)
        logger.debug(f"Bullet updated: ({old_x}, {old_y}) -> ({self.x}, {self.y})")
        self.update_rect()
        # Deactivate if off screen (above top)
        if self.y + self.radius < 0:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the bullet as a filled circle.

        Args:
            surface: Surface to draw on.

        """
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def get_rect(self) -> pygame.Rect:
        """Get the bullet's collision rectangle."""
        return self.rect

    def is_active(self) -> bool:
        """Return True if the bullet is still in play (on screen)."""
        active = 0 <= self.x <= 495 and 0 <= self.y <= 640
        logger.debug(f"Bullet is_active called: ({self.x}, {self.y}) -> {active}")
        return active
