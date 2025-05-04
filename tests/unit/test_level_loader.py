#!/usr/bin/env python3
"""
Test for the XBoing LevelManager.

This tests loading level files from the original XBoing game
and verifies that the LevelManager correctly parses them.
"""

import os
import sys
import pytest
import pygame

from game.level_manager import LevelManager
from game.sprite_block import SpriteBlockManager

@pytest.fixture(scope="module", autouse=True)
def setup_pygame():
    # Use dummy video driver for headless testing
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    pygame.init()
    yield
    pygame.quit()

def test_level_loading():
    """
    Test that LevelManager can load levels 1-10 and populates block manager.
    Asserts that each level loads successfully and block count is > 0.
    """
    level_manager = LevelManager()
    block_manager = SpriteBlockManager(0, 0)
    level_manager.set_block_manager(block_manager)

    for level_num in range(1, 11):
        block_manager.blocks.clear()  # Clear blocks before each load
        success = level_manager.load_level(level_num)
        assert success, f"Level {level_num} failed to load"
        info = level_manager.get_level_info()
        # Basic checks: title is non-empty, time_bonus is int, blocks exist
        assert isinstance(info["title"], str) and info["title"], f"Level {level_num} has no title"
        assert isinstance(info["time_bonus"], int), f"Level {level_num} has invalid time_bonus"
        assert len(block_manager.blocks) > 0, f"Level {level_num} has no blocks"
        # Optionally, print for debug (pytest -s)
        print(f"Level {level_num}: Title='{info['title']}', Time Bonus={info['time_bonus']}, Block Count={len(block_manager.blocks)}")
