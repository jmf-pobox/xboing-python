"""Asset path utilities for XBoing.

This module provides helper functions for locating assets in the
project directory structure with a single canonical path for each asset type.
"""

import os

# Definitive assets directory (now inside xboing package)
ASSETS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
)


def get_asset_path(relative_path: str, create_dirs: bool = False) -> str:
    """Get the absolute path to an asset.

    Args:
    ----
        relative_path (str): Relative path within the assets directory
            (e.g., 'images/blocks/redblk.png')
        create_dirs (bool): If True, create directories if they don't exist

    Returns:
    -------
        str: Absolute path to the asset

    """
    asset_path = os.path.join(ASSETS_DIR, relative_path)

    # If create_dirs is True, create directories if they don't exist
    if create_dirs and not os.path.exists(os.path.dirname(asset_path)):
        os.makedirs(os.path.dirname(asset_path), exist_ok=True)

    return asset_path


def get_images_dir() -> str:
    """Get the path to the images directory."""
    return os.path.join(ASSETS_DIR, "images")


def get_sounds_dir() -> str:
    """Get the path to the sounds directory."""
    return get_asset_path("sounds", create_dirs=True)


def get_levels_dir() -> str:
    """Get the path to the levels directory."""
    return get_asset_path("levels", create_dirs=True)


def get_blocks_dir() -> str:
    """Get the path to the blocks directory."""
    return get_asset_path("images/blocks", create_dirs=True)


def get_backgrounds_dir() -> str:
    """Get the path to the backgrounds directory."""
    return get_asset_path("images/bgrnds", create_dirs=True)


def get_paddles_dir() -> str:
    """Get the path to the paddle graphics directory."""
    return get_asset_path("images/paddle", create_dirs=True)


def get_digits_dir() -> str:
    """Get the path to the digit images directory."""
    return get_asset_path("images/digits", create_dirs=True)


def get_balls_dir() -> str:
    """Get the path to the ball images directory."""
    return get_asset_path("images/balls", create_dirs=True)
