#!/usr/bin/env python3
"""
Test the mapping between level file characters and block types.
"""

import pygame
import pytest
from game.level_manager import LevelManager
from game.sprite_block import SpriteBlock, SpriteBlockManager


@pytest.fixture
def setup_level_manager():
    """Set up the level manager and block manager for testing."""
    # Initialize pygame (needed for SpriteBlock)
    pygame.init()

    # Create managers
    block_manager = SpriteBlockManager(0, 0)
    level_manager = LevelManager()
    level_manager.set_block_manager(block_manager)

    return level_manager, block_manager


def test_level01_loads_successfully(setup_level_manager):
    """Test that level 1 loads successfully."""
    level_manager, _ = setup_level_manager
    success = level_manager.load_level(1)

    assert success, "Level 1 failed to load"

    # Check level title
    assert (
        level_manager.level_title == "Genesis"
    ), f"Expected level title 'Genesis', got '{level_manager.level_title}'"

    # Check time bonus
    assert (
        level_manager.time_bonus == 120
    ), f"Expected time bonus 120, got {level_manager.time_bonus}"


def test_level01_block_mapping(setup_level_manager):
    """Test that the first level contains the expected block types."""
    level_manager, block_manager = setup_level_manager
    level_manager.load_level(1)

    # Get all block types created
    block_types = {}
    for block in block_manager.blocks:
        block_type = block.type
        if block_type in block_types:
            block_types[block_type] += 1
        else:
            block_types[block_type] = 1

    # Expected block types in level 1 based on Genesis level layout
    expected_blocks = {
        SpriteBlock.TYPE_RED: 9,  # 'r' character
        SpriteBlock.TYPE_BLUE: 9,  # 'b' character
        SpriteBlock.TYPE_GREEN: 9,  # 'g' character
        SpriteBlock.TYPE_TAN: 9,  # 't' character
        SpriteBlock.TYPE_YELLOW: 9,  # 'y' character
        SpriteBlock.TYPE_PURPLE: 9,  # 'p' character
        SpriteBlock.TYPE_COUNTER: 9,  # '0' character
        SpriteBlock.TYPE_BULLET: 3,  # 'B' character
    }

    # Check that we have the expected counts
    for block_type, expected_count in expected_blocks.items():
        assert block_type in block_types, f"Expected to find block type {block_type}"
        assert (
            block_types[block_type] == expected_count
        ), f"Expected {expected_count} blocks of type {block_type}, found {block_types.get(block_type, 0)}"


def test_char_to_block_type_mapping():
    """Test that all the level characters map to valid block types."""
    level_manager = LevelManager()

    # All characters used in level files
    test_chars = ".rbgty0pB"

    for char in test_chars:
        if char == ".":
            # Empty space character should map to None
            assert (
                level_manager.CHAR_TO_BLOCK_TYPE.get(char) is None
            ), f"Character '{char}' should map to None"
        else:
            # Other characters should map to valid block types
            assert (
                char in level_manager.CHAR_TO_BLOCK_TYPE
            ), f"Character '{char}' is missing from CHAR_TO_BLOCK_TYPE"

            block_type = level_manager.CHAR_TO_BLOCK_TYPE[char]
            assert isinstance(
                block_type, int
            ), f"Block type for character '{char}' should be an integer"
