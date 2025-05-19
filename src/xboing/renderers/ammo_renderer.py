"""AmmoRenderer: Stateless renderer for displaying the current ammo (bullets) as bullet images."""

import logging
import os
from typing import Any, Dict, Optional

import pygame

from xboing.utils.asset_paths import get_images_dir

MAX_AMMO = 20


class AmmoRenderer:
    """Stateless renderer for displaying the current ammo (bullets) as bullet images."""

    logger = logging.getLogger("xboing.AmmoRenderer")

    bullet_image: Optional[pygame.Surface]
    bullet_width: int
    bullet_height: int
    _surface_cache: Dict[Any, pygame.Surface]

    def __init__(self) -> None:
        """Initialize the AmmoRenderer with a loaded bullet image."""
        self.bullet_image: Optional[pygame.Surface] = self._load_bullet_image()
        if self.bullet_image:
            self.bullet_width = self.bullet_image.get_width()
            self.bullet_height = self.bullet_image.get_height()
        else:
            self.bullet_width = 16
            self.bullet_height = 16
        self._surface_cache: Dict[Any, pygame.Surface] = {}

    def _load_bullet_image(self) -> Optional[pygame.Surface]:
        """Load the bullet image for displaying ammo."""
        bullet_path = os.path.join(get_images_dir(), "guns", "bullet.png")
        if os.path.exists(bullet_path):
            return pygame.image.load(bullet_path).convert_alpha()
        self.logger.warning("Could not load bullet image for ammo display")
        return None

    def render(
        self,
        ammo: int,
        spacing: int = 1,
        max_ammo: int = MAX_AMMO,
    ) -> pygame.Surface:
        """Render the current ammo as bullet images.

        Args:
        ----
            ammo: Number of bullets to display as available (visible).
            spacing: Spacing between bullets. Defaults to 1.
            max_ammo: Maximum number of bullets to display. Defaults to 20.

        Returns:
        -------
            The rendered ammo as a pygame.Surface.

        """
        cache_key = (ammo, spacing, max_ammo)
        if cache_key in self._surface_cache:
            return self._surface_cache[cache_key]
        if not self.bullet_image:
            empty_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
            return empty_surface
        total_width = (
            (self.bullet_width * max_ammo) + (spacing * (max_ammo - 1))
            if max_ammo > 0
            else 0
        )
        surface = pygame.Surface(
            (max(1, total_width), self.bullet_height), pygame.SRCALPHA
        )
        for i in range(max_ammo):
            x = i * (self.bullet_width + spacing)
            # Show only the rightmost `ammo` bullets
            if i >= (max_ammo - ammo):
                surface.blit(self.bullet_image, (x, 0))
        self._surface_cache[cache_key] = surface
        return surface
