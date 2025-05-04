"""
Level Manager for XBoing.

This module handles loading, parsing, and managing XBoing level files.
It interfaces with the SpriteBlockManager to create the appropriate block layout.
"""

import os

from src.game.sprite_block import SpriteBlock
from src.utils.asset_paths import get_levels_dir


class LevelManager:
    """Manages level loading, progression, and completion in XBoing."""

    # Maximum number of levels in the original XBoing
    MAX_LEVELS = 80

    # Background types (matching original XBoing)
    BACKGROUND_SPACE = 0
    BACKGROUND_SEE_THRU = 1
    BACKGROUND_BLACK = 2
    BACKGROUND_WHITE = 3
    BACKGROUND_0 = 4
    BACKGROUND_1 = 5
    BACKGROUND_2 = 6
    BACKGROUND_3 = 7
    BACKGROUND_4 = 8
    BACKGROUND_5 = 9

    # Map level file characters to SpriteBlock types
    CHAR_TO_BLOCK_TYPE = {
        ".": None,  # Empty space (don't create a block)
        " ": None,  # Also empty space
        "\n": None,  # Newline character (don't create a block)
        "r": SpriteBlock.TYPE_RED,  # Red block
        "g": SpriteBlock.TYPE_GREEN,  # Green block
        "b": SpriteBlock.TYPE_BLUE,  # Blue block
        "t": SpriteBlock.TYPE_TAN,  # Tan block
        "y": SpriteBlock.TYPE_YELLOW,  # Yellow block
        "p": SpriteBlock.TYPE_PURPLE,  # Purple block
        "w": SpriteBlock.TYPE_BLACK,  # Black/wall block
        "X": SpriteBlock.TYPE_BOMB,  # Bomb block
        "0": SpriteBlock.TYPE_COUNTER,  # Counter block (0 hits)
        "1": SpriteBlock.TYPE_COUNTER,  # Counter block (1 hit)
        "2": SpriteBlock.TYPE_COUNTER,  # Counter block (2 hits)
        "3": SpriteBlock.TYPE_COUNTER,  # Counter block (3 hits)
        "4": SpriteBlock.TYPE_COUNTER,  # Counter block (4 hits)
        "5": SpriteBlock.TYPE_COUNTER,  # Counter block (5 hits)
        "B": SpriteBlock.TYPE_BULLET,  # Bullet block
        "c": SpriteBlock.TYPE_MAXAMMO,  # Max ammo block
        "H": SpriteBlock.TYPE_HYPERSPACE,  # Hyperspace block
        "D": SpriteBlock.TYPE_DEATH,  # Death block
        "L": SpriteBlock.TYPE_EXTRABALL,  # Extra ball block
        "M": SpriteBlock.TYPE_MGUN,  # Machine gun block
        "W": SpriteBlock.TYPE_WALLOFF,  # Wall off block
        "?": SpriteBlock.TYPE_RANDOM,  # Random block
        "d": SpriteBlock.TYPE_DROP,  # Drop block
        "T": SpriteBlock.TYPE_TIMER,  # Timer block
        "m": SpriteBlock.TYPE_MULTIBALL,  # Multiball block
        "s": SpriteBlock.TYPE_STICKY,  # Sticky block
        "R": SpriteBlock.TYPE_REVERSE,  # Reverse paddle control block
        "<": SpriteBlock.TYPE_PAD_SHRINK,  # Shrink paddle block
        ">": SpriteBlock.TYPE_PAD_EXPAND,  # Expand paddle block
        "+": SpriteBlock.TYPE_ROAMER,  # Roamer block
    }

    def __init__(self, levels_dir=None, layout=None):
        """
        Initialize the level manager.

        Args:
            levels_dir (str): Directory containing level data files.
                If None, tries to find the default levels directory.
            layout (GameLayout): The game layout to set backgrounds on.
        """
        self.current_level = 1
        self.level_title = ""
        self.time_bonus = 0
        self.block_manager = None
        self.time_remaining = 0
        self.timer_active = False
        self.layout = layout

        # Original XBoing starts with background 2 (bgrnd2.xpm)
        # BACKGROUND_2 corresponds to background index 0 in our system
        # which will map to bgrnd2.png
        self.current_background = self.BACKGROUND_2

        # Set the levels directory
        self.levels_dir = levels_dir if levels_dir is not None else get_levels_dir()

        print(f"Using levels directory: {self.levels_dir}")

    def set_block_manager(self, block_manager):
        """
        Set the block manager to use for creating blocks.

        Args:
            block_manager (SpriteBlockManager): The block manager to use
        """
        self.block_manager = block_manager

    def set_layout(self, layout):
        """
        Set the game layout to use for backgrounds.

        Args:
            layout (GameLayout): The game layout to use
        """
        self.layout = layout

    def load_level(self, level_num=None):
        """
        Load a specific level.

        Args:
            level_num (int): Level number to load. If None, uses current_level.

        Returns:
            bool: True if level was loaded successfully, False otherwise
        """
        if level_num is not None:
            self.current_level = level_num

        # Ensure level number is within bounds
        if self.current_level < 1:
            self.current_level = 1
        elif self.current_level > self.MAX_LEVELS:
            self.current_level = self.MAX_LEVELS

        # Get level file path
        level_file = self._get_level_file_path(self.current_level)

        if not os.path.exists(level_file):
            print(f"Level file not found: {level_file}")
            return False

        try:
            level_data = self._parse_level_file(level_file)
            if level_data:
                self.level_title = level_data["title"]
                self.time_bonus = level_data["time_bonus"]
                self.time_remaining = level_data["time_bonus"]

                # Create blocks based on level data using block manager
                if self.block_manager:
                    self._create_blocks_from_layout(level_data["layout"])

                    # Set appropriate background for this level
                    self._set_level_background()

                    return True
                else:
                    print("Error: Block manager not set")
                    return False
            else:
                print(f"Failed to parse level file: {level_file}")
                return False
        except Exception as e:
            print(f"Error loading level {self.current_level}: {e}")
            return False

    def get_next_level(self):
        """
        Advance to the next level.

        Returns:
            bool: True if next level was loaded successfully, False otherwise
        """
        self.current_level += 1

        # Wrap around to level 1 after reaching MAX_LEVELS
        if self.current_level > self.MAX_LEVELS:
            self.current_level = 1

        # Update the background cycle (same logic as original XBoing)
        # In original XBoing: bgrnd++; if (bgrnd == 6) bgrnd = 2;
        self.current_background += 1
        if self.current_background > self.BACKGROUND_5:  # If past background 5
            self.current_background = self.BACKGROUND_2  # Reset to background 2

        return self.load_level()

    def update(self, delta_ms):
        """
        Update level timer and state.

        Args:
            delta_ms (float): Time since last frame in milliseconds
        """
        # Update time bonus if timer is active
        if self.timer_active and self.time_remaining > 0:
            # Original game decrements time once per second
            self.time_remaining -= delta_ms / 1000

            # Ensure time doesn't go below zero
            if self.time_remaining < 0:
                self.time_remaining = 0
                # Could trigger "times up" event here

    def add_time(self, seconds):
        """
        Add time to the level timer (for power-ups).

        Args:
            seconds (int): Seconds to add
        """
        self.time_remaining += seconds

    def start_timer(self):
        """Start the level timer."""
        self.timer_active = True

    def stop_timer(self):
        """Stop the level timer."""
        self.timer_active = False

    def is_level_complete(self):
        """
        Check if the level is complete (all breakable blocks destroyed).

        Returns:
            bool: True if level is complete, False otherwise
        """
        if self.block_manager:
            return self.block_manager.get_breakable_count() == 0
        return False

    def get_level_info(self):
        """
        Get current level information.

        Returns:
            dict: Dictionary with level info (level_num, title, time_bonus, time_remaining)
        """
        return {
            "level_num": self.current_level,
            "title": self.level_title,
            "time_bonus": self.time_bonus,
            "time_remaining": int(self.time_remaining),
        }

    def get_time_remaining(self):
        """
        Get remaining time in seconds.

        Returns:
            int: Remaining time in seconds
        """
        return int(self.time_remaining)

    def get_score_multiplier(self):
        """
        Get score multiplier based on remaining time.

        Returns:
            int: Score multiplier (1, 2, 3, 4, or 5)
        """
        # In original XBoing, time remaining affects final score
        if self.time_remaining <= 0:
            return 1

        if self.time_bonus == 0:
            return 1

        # Calculate percentage of time remaining
        percent = self.time_remaining / self.time_bonus

        if percent > 0.8:
            return 5
        elif percent > 0.6:
            return 4
        elif percent > 0.4:
            return 3
        elif percent > 0.2:
            return 2
        else:
            return 1

    def _create_blocks_from_layout(self, layout):
        """
        Create blocks based on the level layout.

        Args:
            layout (list): List of rows, each a string of characters representing blocks
        """
        if not self.block_manager:
            print("Error: Block manager not set")
            return

        # Calculate block dimensions and spacing (these should match SpriteBlockManager)
        brick_width = self.block_manager.brick_width
        brick_height = self.block_manager.brick_height
        spacing = self.block_manager.spacing

        # Clear existing blocks
        self.block_manager.blocks = []

        # Get play area width from the block manager's offset
        # The original XBoing uses 495 pixels for the play width
        play_width = 495  # Default value based on the original game

        # Calculate grid dimensions
        max_cols = 9  # Original XBoing uses MAX_COL=9

        # Based on precise calculations for a 495px playfield with 9 blocks:
        # Each block is 40px wide, 9 blocks = 360px total
        # With wall spacing of 10px on each side (20px total)
        # Remaining space: 495 - 360 - 20 = 115px
        # Ideal spacing between blocks: 115px / 8 spaces = 14.375px
        wall_spacing = 10  # Wall spacing on each side
        horizontal_spacing = 14  # Exact spacing between blocks

        # Don't recalculate the block width - use the original game's exact values
        block_width = brick_width  # Use original 40px block width

        # Calculate total width of blocks + spacing
        total_width = (
            (max_cols * block_width)
            + ((max_cols - 1) * horizontal_spacing)
            + (2 * wall_spacing)
        )

        # This should be 494px, almost exactly filling the 495px play_width
        # print(f"Total calculated width: {total_width}")

        # The left margin is simply the wall spacing (10px)
        left_margin = wall_spacing

        # Set vertical spacing to exactly 12 pixels as requested
        vertical_spacing = 12

        # Create blocks based on layout
        for row_idx, row in enumerate(layout):
            for col_idx, char in enumerate(row):
                # Skip empty spaces
                if char == ".":
                    continue

                # Convert character to block type
                block_type = self.CHAR_TO_BLOCK_TYPE.get(char)
                if block_type is None:
                    continue

                # Calculate position with precise spacing from walls and between blocks
                x = (
                    self.block_manager.offset_x
                    + left_margin
                    + col_idx * (block_width + horizontal_spacing)
                )

                # Add top margin for vertical positioning with 50% block height spacing
                top_margin = wall_spacing
                y = (
                    self.block_manager.offset_y
                    + top_margin
                    + row_idx * (brick_height + vertical_spacing)
                )

                # Create the block
                block = SpriteBlock(x, y, block_type)

                # Handle special properties based on block type
                if char in "12345":  # Counter blocks 1-5
                    # Set hit points based on character (1-5)
                    hits = int(char)
                    block.health = hits + 1  # Add 1 because we decrement on hit
                elif char == "0":  # Special case for '0' counter blocks
                    # In the original C code, '0' counter blocks have counterSlide=0
                    # and don't display a number or count down
                    block.health = 1  # Just one hit to break
                    block.counter_value = 0  # Mark as a non-counting counter block

                    # Force this block to use the base counter block image without animation
                    block.image_file = (
                        "cntblk.png"  # The base counter block image without a number
                    )
                    if block.image_file in SpriteBlock._image_cache:
                        block.image = SpriteBlock._image_cache[block.image_file]
                    # Disable animations completely for this block
                    block.animation_frames = None

                # Add block to manager
                self.block_manager.blocks.append(block)

    def _set_level_background(self):
        """
        Set the appropriate background for the current level.
        In the original XBoing, backgrounds rotate between levels.
        """
        if self.layout is None:
            return

        # In the original XBoing:
        # 1. The main window always uses the space background
        # 2. The play window cycles through backgrounds 2-5 for each level

        # Map our background constants to the original XBoing background indices:
        # BACKGROUND_2 = bgrnd2.xpm, etc.
        bg_index = self.current_background - self.BACKGROUND_2

        # Backgrounds cycle between 2-5 in the original game
        # BACKGROUND_2 (bg_index 0) -> bgrnd2.png
        # BACKGROUND_3 (bg_index 1) -> bgrnd3.png
        # BACKGROUND_4 (bg_index 2) -> bgrnd4.png
        # BACKGROUND_5 (bg_index 3) -> bgrnd5.png
        bg_file = f"bgrnd{bg_index+2}.png"

        # Debug information
        print(
            f"Setting level {self.current_level} background to: {bg_file} (background {self.current_background})"
        )

        # Set the play area background
        self.layout.set_play_background(bg_index)

    def _get_level_file_path(self, level_num):
        """
        Get the file path for a specific level number.

        Args:
            level_num (int): Level number (1-80)

        Returns:
            str: Path to the level file
        """
        # Format level number with leading zeros (level01.data)
        level_file = f"level{level_num:02d}.data"
        return os.path.join(self.levels_dir, level_file)

    def _parse_level_file(self, file_path):
        """
        Parse an XBoing level file.

        Args:
            file_path (str): Path to the level file

        Returns:
            dict: Dictionary with level data (title, time_bonus, layout)
                  or None if parsing failed
        """
        try:
            with open(file_path) as f:
                # Read title (first line)
                title = f.readline().strip()

                # Read time bonus (second line)
                try:
                    time_bonus = int(f.readline().strip())
                except ValueError:
                    # Default if parsing fails
                    time_bonus = 120

                # Read block layout (remaining lines)
                layout = []
                for line in f:
                    row = line.strip()
                    if row:  # Skip empty lines
                        layout.append(row)

                return {"title": title, "time_bonus": time_bonus, "layout": layout}
        except Exception as e:
            print(f"Error parsing level file {file_path}: {e}")
            return None
