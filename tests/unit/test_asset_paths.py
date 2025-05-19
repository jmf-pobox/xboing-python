#!/usr/bin/env python3
"""Test the asset path utilities to ensure they correctly locate game assets."""

import os

from xboing.utils.asset_paths import (
    ASSETS_DIR,  # Use the constant instead of a function
    get_backgrounds_dir,
    get_blocks_dir,
    get_images_dir,
    get_levels_dir,
    get_paddles_dir,
    get_sounds_dir,
)


def test_asset_directories_exist():
    """Test that all asset directories exist."""
    # Check main assets directory
    assert os.path.isdir(ASSETS_DIR), f"Assets directory does not exist: {ASSETS_DIR}"

    # Check images directories
    images_dir = get_images_dir()
    assert os.path.isdir(images_dir), f"Images directory does not exist: {images_dir}"

    blocks_dir = get_blocks_dir()
    assert os.path.isdir(blocks_dir), f"Blocks directory does not exist: {blocks_dir}"

    # Check for balls directory without get_balls_dir function
    balls_dir = os.path.join(get_images_dir(), "balls")
    assert os.path.isdir(balls_dir), f"Balls directory does not exist: {balls_dir}"

    backgrounds_dir = get_backgrounds_dir()
    assert os.path.isdir(
        backgrounds_dir
    ), f"Backgrounds directory does not exist: {backgrounds_dir}"

    paddles_dir = get_paddles_dir()
    assert os.path.isdir(
        paddles_dir
    ), f"Paddles directory does not exist: {paddles_dir}"

    # Check other asset directories
    sounds_dir = get_sounds_dir()
    assert os.path.isdir(sounds_dir), f"Sounds directory does not exist: {sounds_dir}"

    levels_dir = get_levels_dir()
    assert os.path.isdir(levels_dir), f"Levels directory does not exist: {levels_dir}"


def test_asset_files_exist():
    """Test that essential asset files exist."""
    # Check for a few essential files from each category
    balls_dir = os.path.join(get_images_dir(), "balls")
    essential_files = [
        os.path.join(get_blocks_dir(), "redblk.png"),
        os.path.join(get_blocks_dir(), "blueblk.png"),
        os.path.join(balls_dir, "ball1.png"),
        os.path.join(get_backgrounds_dir(), "bgrnd.png"),
        os.path.join(get_paddles_dir(), "padmed.png"),
        os.path.join(get_sounds_dir(), "boing.wav"),
        os.path.join(get_levels_dir(), "level01.data"),
    ]

    for file_path in essential_files:
        assert os.path.isfile(file_path), f"Essential asset file missing: {file_path}"
