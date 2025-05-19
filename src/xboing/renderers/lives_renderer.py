"""Stateless renderer for displaying the number of lives as ball images."""

import logging
import os
from typing import Any, Dict, Optional

import pygame

from xboing.utils.asset_paths import get_images_dir


class LivesRenderer:
    """Stateless renderer for displaying the number of lives as ball images."""

    logger = logging.getLogger("xboing.LivesRenderer")

    ball_image: Optional[pygame.Surface]
    ball_width: int
    ball_height: int
    _surface_cache: Dict[Any, pygame.Surface]

    def __init__(self) -> None:
        """Initialize the LivesRenderer with a loaded ball image."""
        self.ball_image: Optional[pygame.Surface] = self._load_ball_image()
        if self.ball_image:
            self.ball_width = self.ball_image.get_width()
            self.ball_height = self.ball_image.get_height()
        else:
            self.ball_width = 16
            self.ball_height = 16
        self._surface_cache: Dict[Any, pygame.Surface] = {}

    def _load_ball_image(self) -> Optional[pygame.Surface]:
        """Load the ball image for displaying lives."""
        images_dir = get_images_dir()
        life_path = os.path.join(images_dir, "balls", "life.png")
        if os.path.exists(life_path):
            return pygame.image.load(life_path).convert_alpha()
        ball_path = os.path.join(images_dir, "balls", "ball1.png")
        if os.path.exists(ball_path):
            return pygame.image.load(ball_path).convert_alpha()
        self.logger.warning("Could not load ball image for lives display")
        return None

    def render(
        self,
        num_lives: int,
        spacing: int = 4,
        scale: float = 1.0,
        max_lives: int = 3,
    ) -> pygame.Surface:
        """Render the number of lives as ball images.

        Args:
        ----
            num_lives: Number of lives to display.
            spacing: Spacing between balls. Defaults to 4.
            scale: Scale factor for ball size. Defaults to 1.0.
            max_lives: Maximum number of lives to display. Defaults to 3.

        Returns:
        -------
            The rendered lives as a pygame.Surface.

        """
        cache_key = (num_lives, spacing, scale, max_lives)
        if cache_key in self._surface_cache:
            return self._surface_cache[cache_key]
        if not self.ball_image:
            empty_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
            return empty_surface
        scaled_width = int(self.ball_width * scale)
        scaled_height = int(self.ball_height * scale)
        total_width = (
            (scaled_width * max_lives) + (spacing * (max_lives - 1))
            if max_lives > 0
            else 0
        )
        surface = pygame.Surface((max(1, total_width), scaled_height), pygame.SRCALPHA)
        if scale != 1.0:
            ball_surface = pygame.transform.smoothscale(
                self.ball_image, (scaled_width, scaled_height)
            )
        else:
            ball_surface = self.ball_image
        for i in range(max_lives):
            x = i * (scaled_width + spacing)
            if i >= (max_lives - num_lives):
                surface.blit(ball_surface, (x, 0))
        self._surface_cache[cache_key] = surface
        return surface
