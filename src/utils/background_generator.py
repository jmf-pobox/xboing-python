"""
Background pattern generator for XBoing.

This module provides functions for generating background patterns
similar to the original XBoing game.
"""

import pygame


def create_pattern_background(width, height, pattern_size=32, colors=None, darkness=0):
    """
    Create a background surface with a repeating pattern similar to the original XBoing.

    Args:
        width (int): Width of the background surface
        height (int): Height of the background surface
        pattern_size (int): Size of the pattern tile (default: 32px)
        colors (tuple): Optional colors to use for the pattern. Default is XBoing's original colors.
        darkness (int): 0-100 value to darken the pattern (0=original, 100=black)

    Returns:
        pygame.Surface: The background surface
    """
    # Use the original XBoing colors if none provided
    if colors is None:
        colors = {
            "light_gray": (171, 171, 171),  # #ABABAB
            "medium_gray": (134, 134, 134),  # #868686
            "dark_gray": (101, 101, 101),  # #656565
        }

    # Apply darkness adjustment if specified
    if darkness > 0:
        # Ensure darkness is within range
        darkness = max(0, min(100, darkness))
        darkening_factor = 1.0 - (darkness / 100.0)

        # Create darker versions of the colors
        colors = {
            "light_gray": (
                int(colors["light_gray"][0] * darkening_factor),
                int(colors["light_gray"][1] * darkening_factor),
                int(colors["light_gray"][2] * darkening_factor),
            ),
            "medium_gray": (
                int(colors["medium_gray"][0] * darkening_factor),
                int(colors["medium_gray"][1] * darkening_factor),
                int(colors["medium_gray"][2] * darkening_factor),
            ),
            "dark_gray": (
                int(colors["dark_gray"][0] * darkening_factor),
                int(colors["dark_gray"][1] * darkening_factor),
                int(colors["dark_gray"][2] * darkening_factor),
            ),
        }

    # Create the pattern tile based on the original XBoing background
    # This recreates the woven/checkered appearance
    pattern = pygame.Surface((pattern_size, pattern_size))

    # Fill with medium gray as the base
    pattern.fill(colors["medium_gray"])

    # Draw the pattern similar to the original XBoing background
    # Based on the actual pixel data from bgrnd.xpm
    for y in range(pattern_size):
        for x in range(pattern_size):
            # Create a checkered pattern with alternating light/dark areas
            if (x // 8) % 2 == (y // 8) % 2:
                # Create curved pattern elements
                if (x % 8 < 2) or (y % 8 < 2):
                    pattern.set_at((x, y), colors["light_gray"])
                elif (x % 8 > 5) or (y % 8 > 5):
                    pattern.set_at((x, y), colors["dark_gray"])
            else:
                # Create curved pattern elements for the other regions
                if (x % 8 > 5) or (y % 8 > 5):
                    pattern.set_at((x, y), colors["light_gray"])
                elif (x % 8 < 2) or (y % 8 < 2):
                    pattern.set_at((x, y), colors["dark_gray"])

    # Create the background surface
    background = pygame.Surface((width, height))

    # Tile the pattern
    for y in range(0, height, pattern_size):
        for x in range(0, width, pattern_size):
            background.blit(pattern, (x, y))

    return background


def create_grid_background(width, height, grid_size=40, colors=None):
    """
    Create a grid-based background similar to XBoing's playfield.

    Args:
        width (int): Width of the background surface
        height (int): Height of the background surface
        grid_size (int): Size of each grid cell (default: 40px)
        colors (tuple): Optional colors to use for the grid

    Returns:
        pygame.Surface: The background surface
    """
    # Default XBoing-like colors
    if colors is None:
        colors = {
            "bg": (40, 44, 52),  # Dark blue-gray
            "grid": (50, 54, 62),  # Slightly lighter grid lines
        }

    # Create the background surface
    background = pygame.Surface((width, height))
    background.fill(colors["bg"])

    # Draw horizontal grid lines
    for y in range(0, height, grid_size):
        pygame.draw.line(background, colors["grid"], (0, y), (width, y))

    # Draw vertical grid lines
    for x in range(0, width, grid_size):
        pygame.draw.line(background, colors["grid"], (x, 0), (x, height))

    return background
