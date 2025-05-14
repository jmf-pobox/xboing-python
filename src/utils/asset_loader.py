"""
Asset loading utilities.

This module provides functions for loading game assets such as
images and converting them for use with pygame.
"""

import logging
import os

import pygame

logger = logging.getLogger("xboing.AssetLoader")


def load_image(filename, alpha=True, scale=None):
    """
    Load an image and convert it for optimal display.

    Args:
        filename (str): Path to the image file
        alpha (bool): Whether the image has alpha transparency
        scale (tuple): Optional (width, height) to scale the image to

    Returns:
        pygame.Surface: The loaded image surface
    """
    try:
        surface = pygame.image.load(filename)
    except pygame.error as e:
        logger.error(f"Error loading image {filename}: {e}")
        # Create a small error surface
        surface = pygame.Surface((64, 64))
        surface.fill((255, 0, 255))  # Fill with magenta to make errors obvious
        return surface

    # Convert the surface for faster blitting
    if alpha:
        surface = surface.convert_alpha()
    else:
        surface = surface.convert()

    # Scale if needed
    if scale:
        surface = pygame.transform.scale(surface, scale)

    return surface


def load_image_sequence(directory, pattern, num_frames, alpha=True):
    """
    Load a sequence of images for animation.

    Args:
        directory (str): Directory containing the images
        pattern (str): Filename pattern with {} for frame number
        num_frames (int): Number of frames to load
        alpha (bool): Whether the images have alpha transparency

    Returns:
        list: List of pygame.Surface objects
    """
    frames = []
    for i in range(num_frames):
        filename = os.path.join(directory, pattern.format(i))
        surface = load_image(filename, alpha)
        frames.append(surface)
    return frames


def create_font(size):
    """
    Create a pygame font object.

    Args:
        font_name (str): Font name or path to font file, or None for default
        size (int): Font size in points

    Returns:
        pygame.font.Font: The font object
    """
    return pygame.font.Font(None, size)
