"""
Stateless renderer for displaying the number of lives as ball images.
Used by UI components for visual output.
"""

import logging
import os

import pygame

from utils.asset_paths import get_balls_dir


class LivesRenderer:
    """
    Stateless renderer for displaying the number of lives as ball images.
    Used by UI components for visual output.
    """

    logger = logging.getLogger("xboing.LivesRenderer")

    def __init__(self):
        """Initialize the LivesRenderer with a loaded ball image."""
        self.ball_image = self._load_ball_image()
        if self.ball_image:
            self.ball_width = self.ball_image.get_width()
            self.ball_height = self.ball_image.get_height()
        else:
            self.ball_width = 16
            self.ball_height = 16
        self._surface_cache = {}

    def _load_ball_image(self):
        balls_dir = get_balls_dir()
        life_path = os.path.join(balls_dir, "life.png")
        if os.path.exists(life_path):
            return pygame.image.load(life_path).convert_alpha()
        ball_path = os.path.join(balls_dir, "ball1.png")
        if os.path.exists(ball_path):
            return pygame.image.load(ball_path).convert_alpha()
        self.logger.warning("Could not load ball image for lives display")
        return None

    def render(self, num_lives, spacing=4, scale=1.0, max_lives=3):
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
