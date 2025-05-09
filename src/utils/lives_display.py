"""
Lives Display for XBoing.

This module provides a class for displaying the number of remaining lives
using the ball images, reproducing the original XBoing UI.
"""

import logging
import os

import pygame

from utils.asset_paths import get_balls_dir

logger = logging.getLogger("xboing.lives_display")


class LivesDisplay:
    """
    A class for displaying the number of lives using ball images.
    
    This maintains the classic XBoing aesthetic by showing a row of
    ball images to represent the player's remaining lives.
    """

    def __init__(self):
        """Initialize the LivesDisplay with a loaded ball image."""
        self.ball_image = self._load_ball_image()
        
        # Default values
        if self.ball_image:
            self.ball_width = self.ball_image.get_width()
            self.ball_height = self.ball_image.get_height()
        else:
            # Default values in case loading fails
            self.ball_width = 16
            self.ball_height = 16
            
        # Cache for previously rendered lives displays
        self._surface_cache = {}

    def _load_ball_image(self):
        """Load the life ball image."""
        balls_dir = get_balls_dir()
        life_path = os.path.join(balls_dir, "life.png")
        
        if os.path.exists(life_path):
            return pygame.image.load(life_path).convert_alpha()
        
        # Fallback to regular ball if life.png doesn't exist
        ball_path = os.path.join(balls_dir, "ball1.png")
        if os.path.exists(ball_path):
            return pygame.image.load(ball_path).convert_alpha()
        
        logger.warning("Could not load ball image for lives display")
        return None

    def render(self, num_lives, spacing=4, scale=1.0, max_lives=3):
        """
        Render the lives display with ball images.
        
        Args:
            num_lives (int): Number of lives to display (visible balls)
            spacing (int): Pixels between ball images
            scale (float): Scale factor for the rendered balls
            max_lives (int): Total number of balls to render (default: 3)
        
        Returns:
            pygame.Surface: A surface containing the rendered lives display
        """
        # Check cache first
        cache_key = (num_lives, spacing, scale, max_lives)
        if cache_key in self._surface_cache:
            return self._surface_cache[cache_key]
            
        if not self.ball_image:
            # Return an empty surface if we don't have a ball image
            empty_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
            return empty_surface
            
        # Calculate the dimensions for the lives display
        scaled_width = int(self.ball_width * scale)
        scaled_height = int(self.ball_height * scale)
        total_width = (scaled_width * max_lives) + (spacing * (max_lives - 1)) if max_lives > 0 else 0
        
        # Create a surface for the rendered lives
        surface = pygame.Surface((max(1, total_width), scaled_height), pygame.SRCALPHA)
        
        # Scale the ball image if needed
        if scale != 1.0:
            ball_surface = pygame.transform.smoothscale(
                self.ball_image,
                (scaled_width, scaled_height)
            )
        else:
            ball_surface = self.ball_image
        
        # Render each life (invisible balls on the left, visible on the right)
        for i in range(max_lives):
            x = i * (scaled_width + spacing)
            # Balls to the left are invisible, balls to the right are visible
            if i >= (max_lives - num_lives):
                # Visible ball
                surface.blit(ball_surface, (x, 0))
            else:
                # Invisible (do not blit anything)
                pass
        
        # Cache the rendered surface
        self._surface_cache[cache_key] = surface
        
        return surface