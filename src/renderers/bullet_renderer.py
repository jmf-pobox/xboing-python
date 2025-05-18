"""Stateless renderer for displaying bullets using bullet sprites or fallback circles."""

import logging
from typing import Optional

import pygame

from game.bullet_manager import BulletManager


class BulletRenderer:
    """Stateless renderer for displaying all bullets on screen."""

    logger = logging.getLogger("xboing.BulletRenderer")

    def __init__(self, bullet_sprite: Optional[pygame.Surface] = None) -> None:
        """Initialize the BulletRenderer.

        Args:
            bullet_sprite: Optional sprite to use for bullets. If None, draws circles.

        """
        self.bullet_sprite = bullet_sprite

    def render(self, surface: pygame.Surface, bullet_manager: BulletManager) -> None:
        """Render all active bullets on the given surface.

        Args:
            surface: The Pygame surface to draw on.
            bullet_manager: The BulletManager instance managing all bullets.

        """
        self.logger.debug(f"BulletManager id in render: {id(bullet_manager)}")
        self.logger.debug(f"Rendering {len(bullet_manager.bullets)} bullets")
        for bullet in bullet_manager.bullets:
            if self.bullet_sprite:
                rect = self.bullet_sprite.get_rect(
                    center=(int(bullet.x), int(bullet.y))
                )
                surface.blit(self.bullet_sprite, rect)
            else:
                pygame.draw.circle(
                    surface, bullet.color, (int(bullet.x), int(bullet.y)), bullet.radius
                )
