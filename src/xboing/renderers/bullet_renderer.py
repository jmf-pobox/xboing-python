"""Stateless renderer for displaying bullets using bullet sprites or fallback circles."""

import logging
import os
from typing import Optional

import pygame

from xboing.game.bullet_manager import BulletManager
from xboing.utils.asset_paths import get_asset_path


def get_bullet_sprite_path() -> str:
    """Get the path to the bullet sprite image."""
    return get_asset_path("images/guns/bullet.png")


class BulletRenderer:
    """Stateless renderer for displaying all bullets on screen."""

    logger = logging.getLogger("xboing.BulletRenderer")

    def __init__(self) -> None:
        """Initialize the BulletRenderer and load the bullet sprite asset."""
        bullet_sprite_path = get_bullet_sprite_path()
        self.bullet_sprite: Optional[pygame.Surface] = None
        if os.path.exists(bullet_sprite_path):
            self.bullet_sprite = pygame.image.load(bullet_sprite_path).convert_alpha()
        else:
            self.logger.warning(f"Could not load bullet sprite: {bullet_sprite_path}")

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
