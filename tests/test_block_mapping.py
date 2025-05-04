#!/usr/bin/env python3
"""
Test script to verify mapping between level file characters and block types.
This script loads the first level and prints out which blocks are being created for each character.
"""

import os
import sys

import pygame

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.level_manager import LevelManager
from game.sprite_block import SpriteBlock, SpriteBlockManager
from utils.asset_paths import get_levels_dir


def main():
    # Initialize pygame (needed for SpriteBlock)
    pygame.init()

    # Read the first level file directly to analyze characters used
    levels_dir = get_levels_dir()
    level_file = os.path.join(levels_dir, "level01.data")

    print(f"Analyzing level file: {level_file}")
    print("\nLevel file format:")

    with open(level_file) as f:
        lines = f.readlines()
        print(f"Title: {lines[0].strip()}")
        print(f"Time bonus: {lines[1].strip()}")

        # Analyze the block layout (skip title and time bonus lines)
        found_chars = set()
        for line in lines[2:]:
            for char in line.strip():
                if char != "\n":
                    found_chars.add(char)

    print(
        f"\nFound {len(found_chars)} unique block characters: {''.join(sorted(found_chars))}"
    )

    # Create a SpriteBlockManager to check block types
    block_manager = SpriteBlockManager(0, 0)

    # Create a LevelManager and load the first level
    level_manager = LevelManager()
    level_manager.set_block_manager(block_manager)
    success = level_manager.load_level(1)

    if success:
        # Count which block types were created
        block_types = {}
        for block in block_manager.blocks:
            block_type = block.type
            if block_type in block_types:
                block_types[block_type] += 1
            else:
                block_types[block_type] = 1

        # Print block type counts
        print("\nBlock types created:")
        for block_type, count in block_types.items():
            # Get the name of the block type constant
            for attr in dir(SpriteBlock):
                if (
                    attr.startswith("TYPE_")
                    and getattr(SpriteBlock, attr) == block_type
                ):
                    block_name = attr
                    break
            else:
                block_name = f"Unknown ({block_type})"

            print(f"{block_name}: {count} blocks")

        # Check the mapping completeness
        print("\nVerifying character-to-block mapping:")
        for char in found_chars:
            block_type = level_manager.CHAR_TO_BLOCK_TYPE.get(char)
            if block_type is not None:
                # Find the name of this block type
                for attr in dir(SpriteBlock):
                    if (
                        attr.startswith("TYPE_")
                        and getattr(SpriteBlock, attr) == block_type
                    ):
                        block_name = attr
                        break
                else:
                    block_name = f"Unknown ({block_type})"

                print(f"Character '{char}' maps to {block_name}")
            else:
                print(f"WARNING: Character '{char}' has no mapping!")
    else:
        print("Failed to load level 1")


if __name__ == "__main__":
    main()
