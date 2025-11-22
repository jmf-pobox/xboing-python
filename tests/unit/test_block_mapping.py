#!/usr/bin/env python3
"""Test the mapping between level file characters and block types."""

import pygame
import pytest

from xboing.game.block import Block, CounterBlock
from xboing.game.block_manager import BlockManager
from xboing.game.block_types import (
    BLUE_BLK,
    BULLET_BLK,
    COUNTER_BLK,
    GREEN_BLK,
    PURPLE_BLK,
    RED_BLK,
    TAN_BLK,
    YELLOW_BLK,
)
from xboing.game.level_manager import LevelManager
from xboing.utils.block_type_loader import BlockTypeData, get_block_types


@pytest.fixture
def setup_level_manager():
    """Set up the level manager and block manager for testing."""
    # Initialize pygame (needed for SpriteBlock)
    pygame.init()

    # Create managers
    block_manager = BlockManager(0, 0)
    level_manager = LevelManager()
    level_manager.set_block_manager(block_manager)
    block_types = get_block_types()
    return level_manager, block_manager, block_types


def test_level01_loads_successfully(setup_level_manager):
    """Test that level 1 loads successfully."""
    level_manager, _, _ = setup_level_manager
    level_manager.load_level(1)

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
    level_manager, block_manager, block_types = setup_level_manager
    level_manager.load_level(1)

    # Get all block types created
    block_types = {}
    for block in block_manager.blocks:
        block_type = block.type  # This is now a string key
        if block_type in block_types:
            block_types[block_type] += 1
        else:
            block_types[block_type] = 1

    # Expected block types in level 1 based on Genesis level layout
    expected_blocks = {
        RED_BLK: 9,  # 'r' character
        BLUE_BLK: 9,  # 'b' character
        GREEN_BLK: 9,  # 'g' character
        TAN_BLK: 9,  # 't' character
        YELLOW_BLK: 9,  # 'y' character
        PURPLE_BLK: 9,  # 'p' character
        COUNTER_BLK: 9,  # '0' character
        BULLET_BLK: 3,  # 'B' character
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
                block_type, str
            ), f"Block type for character '{char}' should be a string (canonical key)"


def test_block_removal_after_explosion_animation():
    pygame.init()
    block_manager = BlockManager(0, 0)
    block_types = get_block_types()
    # Create a single block
    block = Block(10, 10, block_types[RED_BLK])
    block_manager.blocks = [block]
    # Hit the block (should enter breaking state)
    block.hit()
    assert block.state == "breaking"
    # Block should still be present
    block_manager.update(40)  # less than frame duration
    assert block in block_manager.blocks
    # Advance enough to finish animation
    for _ in range(5):
        block_manager.update(100)
    # Now block should be removed
    assert block not in block_manager.blocks


def test_counterblock_initialization_and_hit_logic():
    # Minimal config for a counter block with 3 hits and 4 animation frames
    config: BlockTypeData = {
        "blockType": "COUNTER_BLK",
        "main_sprite": "cntblk.png",
        "points": 200,
        "animation_frames": [
            "cntblk1.png",
            "cntblk2.png",
            "cntblk3.png",
            "cntblk4.png",
        ],
        "explosion_frames": ["excnt1.png", "excnt2.png", "excnt3.png"],
    }
    block = CounterBlock(10, 20, config)
    block.hits_remaining = 3
    block.animation_frame = 2  # Should match hits_remaining - 1

    # Hit 1: hits_remaining should decrement, animation_frame should update
    broken, points, _effect = block.hit()
    assert not broken
    assert block.hits_remaining == 2
    assert block.animation_frame == 2  # Should match hits_remaining

    # Hit 2
    broken, points, _effect = block.hit()
    assert not broken
    assert block.hits_remaining == 1
    assert block.animation_frame == 1

    # Hit 3: block should break
    broken, points, _effect = block.hit()
    assert broken
    assert points == 200
    assert block.hits_remaining == 0
    assert block.state == "breaking"

    # After breaking, further hits should not decrement below 0
    broken, points, _effect = block.hit()
    assert block.hits_remaining == 0
    assert block.state == "breaking"
