#!/usr/bin/env python3
"""
Test script for the XBoing LevelManager.

This script tests loading level files from the original XBoing game
and verifies that the LevelManager correctly parses them.
"""

import os
import sys

import pygame

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.game.level_manager import LevelManager
from src.game.sprite_block import SpriteBlockManager


def main():
    """Test level loading functionality."""
    # Initialize pygame (needed for SpriteBlock)
    pygame.init()

    # Create a small display for testing
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("XBoing Level Loader Test")

    # Create the level manager
    level_manager = LevelManager()

    # Create a block manager with offset (0, 0)
    block_manager = SpriteBlockManager(0, 0)

    # Set the block manager for the level manager
    level_manager.set_block_manager(block_manager)

    # Try to load levels 1-10
    print("\nTesting level loading:")
    for level_num in range(1, 11):
        success = level_manager.load_level(level_num)
        if success:
            info = level_manager.get_level_info()
            print(f"Level {level_num} loaded successfully:")
            print(f"  Title: {info['title']}")
            print(f"  Time Bonus: {info['time_bonus']} seconds")
            print(f"  Block Count: {len(block_manager.blocks)}")

            # Create a simple image to visualize the level
            screen.fill((0, 0, 0))
            block_manager.draw(screen)
            pygame.display.flip()

            # Wait for a key press or quit
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN:
                        waiting = False
        else:
            print(f"Failed to load level {level_num}")

    # Clean up
    pygame.quit()
    print("Test complete")


if __name__ == "__main__":
    main()
