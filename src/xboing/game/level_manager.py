"""Level Manager for XBoing.

This module handles loading, parsing, and managing XBoing level files.
It interfaces with the BlockManager to create the appropriate block layout.
"""

import logging
import os
from typing import Any, Dict, List, Optional

from xboing.game.block import CounterBlock
from xboing.game.block_types import (
    BLACK_BLK,
    BLUE_BLK,
    BOMB_BLK,
    BULLET_BLK,
    COUNTER_BLK,
    DEATH_BLK,
    DROP_BLK,
    EXTRABALL_BLK,
    GREEN_BLK,
    HYPERSPACE_BLK,
    MAXAMMO_BLK,
    MGUN_BLK,
    MULTIBALL_BLK,
    PAD_EXPAND_BLK,
    PAD_SHRINK_BLK,
    PURPLE_BLK,
    RANDOM_BLK,
    RED_BLK,
    REVERSE_BLK,
    ROAMER_BLK,
    STICKY_BLK,
    TAN_BLK,
    TIMER_BLK,
    WALLOFF_BLK,
    YELLOW_BLK,
)
from xboing.utils.asset_paths import get_levels_dir


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

    # Map level file characters to canonical block type keys
    CHAR_TO_BLOCK_TYPE = {
        ".": None,  # Empty space (don't create a block)
        " ": None,  # Also empty space
        "\n": None,  # Newline character (don't create a block)
        "r": RED_BLK,  # Red block
        "g": GREEN_BLK,  # Green block
        "b": BLUE_BLK,  # Blue block
        "t": TAN_BLK,  # Tan block
        "y": YELLOW_BLK,  # Yellow block
        "p": PURPLE_BLK,  # Purple block
        "w": BLACK_BLK,  # Black/wall block
        "X": BOMB_BLK,  # Bomb block
        "0": COUNTER_BLK,  # Counter block (0 hits)
        "1": COUNTER_BLK,  # Counter block (1 hit)
        "2": COUNTER_BLK,  # Counter block (2 hits)
        "3": COUNTER_BLK,  # Counter block (3 hits)
        "4": COUNTER_BLK,  # Counter block (4 hits)
        "5": COUNTER_BLK,  # Counter block (5 hits)
        "B": BULLET_BLK,  # Bullet block
        "c": MAXAMMO_BLK,  # Max ammo block
        "H": HYPERSPACE_BLK,  # Hyperspace block
        "D": DEATH_BLK,  # Death block
        "L": EXTRABALL_BLK,  # Extra ball block
        "M": MGUN_BLK,  # Machine gun block
        "W": WALLOFF_BLK,  # Wall off block
        "?": RANDOM_BLK,  # Random block
        "d": DROP_BLK,  # Drop block
        "T": TIMER_BLK,  # Timer block
        "m": MULTIBALL_BLK,  # Multiball block
        "s": STICKY_BLK,  # Sticky block
        "R": REVERSE_BLK,  # Reverse paddle control block
        "<": PAD_SHRINK_BLK,  # Shrink paddle block
        ">": PAD_EXPAND_BLK,  # Expand paddle block
        "+": ROAMER_BLK,  # Roamer block
    }

    def __init__(
        self, levels_dir: Optional[str] = None, layout: Optional[Any] = None
    ) -> None:
        """Initialize the level manager.

        Args:
        ----
            levels_dir (str): Directory containing level data files.
                If None, tries to find the default levels directory.
            layout (GameLayout): The game layout to set backgrounds on.

        """
        self.logger = logging.getLogger("xboing.LevelManager")
        self.current_level = 1
        self.level_title = ""
        self.time_bonus = 0
        self.block_manager = None
        self.time_remaining: float = 0.0
        self.timer_active = False
        self.layout = layout

        # Original XBoing starts with background 2 (bgrnd2.xpm)
        # BACKGROUND_2 corresponds to background index 0 in our system
        # which will map to bgrnd2.png
        self.current_background = self.BACKGROUND_2

        # Set the levels directory
        self.levels_dir = levels_dir if levels_dir is not None else get_levels_dir()

        self.logger.info(f"Using levels directory: {self.levels_dir}")

    def set_block_manager(self, block_manager: Any) -> None:
        """Set the block manager to use for creating blocks.

        Args:
        ----
            block_manager (BlockManager): The block manager to use

        """
        self.block_manager = block_manager

    def set_layout(self, layout: Any) -> None:
        """Set the game layout to use for backgrounds.

        Args:
        ----
            layout (GameLayout): The game layout to use

        """
        self.layout = layout

    def load_level(self, level_num: Optional[int] = None) -> bool:
        """Load a specific level.

        Args:
        ----
            level_num (int): Level number to load. If None, uses current_level.

        Returns:
        -------
            bool: True if level was loaded successfully, False otherwise

        """
        if level_num is not None:
            self.current_level = level_num

        self._clamp_level_number()
        level_file = self._get_level_file_path(self.current_level)

        result = False

        if not self._level_file_exists(level_file):
            self.logger.warning(f"Level file not found: {level_file}")
        else:
            level_data = self._safe_parse_level_file(level_file)
            if level_data is None:
                self.logger.warning(f"Failed to parse level file: {level_file}")
            elif not self.block_manager:
                self.logger.error("Error: Block manager not set")
            else:
                self.level_title = level_data["title"]
                self.time_bonus = level_data["time_bonus"]
                self.time_remaining = float(level_data["time_bonus"])
                self._create_blocks_from_layout(level_data["layout"])
                self._set_level_background()
                result = True

        return result

    def _clamp_level_number(self) -> None:
        if self.current_level < 1:
            self.current_level = 1
        elif self.current_level > self.MAX_LEVELS:
            self.current_level = self.MAX_LEVELS

    def _level_file_exists(self, level_file: str) -> bool:
        return os.path.exists(level_file)

    def _safe_parse_level_file(self, level_file: str) -> Optional[Dict[str, Any]]:
        try:
            return self._parse_level_file(level_file)
        except Exception as e:
            self.logger.error(f"Error loading level {self.current_level}: {e}")
            return None

    def get_next_level(self) -> bool:
        """Advance to the next level, or reset if at the last level."""
        if self.current_level < self.MAX_LEVELS:
            self.current_level += 1
        else:
            self.current_level = 1

        # Update the background cycle (same logic as original XBoing)
        # In original XBoing: bgrnd++; if (bgrnd == 6) bgrnd = 2;
        self.current_background += 1
        if self.current_background > self.BACKGROUND_5:  # If past background 5
            self.current_background = self.BACKGROUND_2  # Reset to background 2

        return self.load_level()

    def update(self, delta_ms: float) -> None:
        """Update level timer and state.

        Args:
        ----
            delta_ms (float): Time since last frame in milliseconds

        """
        # Update time bonus if timer is active
        if self.timer_active and self.time_remaining > 0:
            # Original game decrements time once per second
            self.time_remaining -= delta_ms / 1000

            # Ensure time doesn't go below zero
            self.time_remaining = max(self.time_remaining, 0)
            # Could trigger "times up" event here

    def add_time(self, seconds: int) -> None:
        """Add time to the level timer (for power-ups).

        Args:
        ----
            seconds (int): Seconds to add

        """
        self.time_remaining += float(seconds)

    def start_timer(self) -> None:
        """Start the level timer."""
        self.timer_active = True

    def stop_timer(self) -> None:
        """Stop the level timer."""
        self.timer_active = False

    def is_level_complete(self) -> bool:
        """Check if the level is complete (all breakable blocks destroyed).

        Returns
        -------
            bool: True if level is complete, False otherwise

        """
        if self.block_manager:
            return self.block_manager.get_breakable_count() == 0
        return False

    def get_level_info(self) -> Dict[str, Any]:
        """Get current level information.

        Returns
        -------
            Dict[str, Any]: Dictionary with level info (level_num, title, time_bonus, time_remaining)

        """
        return {
            "level_num": self.current_level,
            "title": self.level_title,
            "time_bonus": self.time_bonus,
            "time_remaining": int(self.time_remaining),
        }

    def get_time_remaining(self) -> int:
        """Get remaining time in seconds.

        Returns
        -------
            int: Remaining time in seconds

        """
        return int(self.time_remaining)

    def get_score_multiplier(self) -> int:
        """Get score multiplier based on remaining time.

        Returns
        -------
            int: Score multiplier (1, 2, 3, 4, or 5)

        """
        multiplier = 1
        if self.time_remaining > 0 and self.time_bonus != 0:
            percent = self.time_remaining / self.time_bonus
            if percent > 0.8:
                multiplier = 5
            elif percent > 0.6:
                multiplier = 4
            elif percent > 0.4:
                multiplier = 3
            elif percent > 0.2:
                multiplier = 2
        return multiplier

    def _create_blocks_from_layout(self, layout: List[str]) -> None:
        """Create blocks based on the level layout.

        Args:
        ----
            layout (list): List of rows, each a string of characters representing blocks

        """
        if not self.block_manager:
            self.logger.error("Block manager not set")
            return

        # Calculate block dimensions and spacing (these should match BlockManager)
        brick_width = self.block_manager.brick_width
        brick_height = self.block_manager.brick_height

        # Clear existing blocks
        self.block_manager.blocks = []

        # Get play area width from the block manager's offset
        # The original XBoing uses 495 pixels for the play width
        # The original XBoing uses 495 pixels for the play width
        # Calculate grid dimensions
        wall_spacing = 10  # Wall spacing on each side
        horizontal_spacing = 14  # Exact spacing between blocks

        # Don't recalculate the block width - use the original game's exact values
        block_width = brick_width  # Use original 40px block width

        # Calculate total width of blocks + spacing
        # Calculate total width of blocks + spacing
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

                # Create the block using the block manager's factory method
                block = self.block_manager.create_block(x, y, block_type)

                # Handle special properties based on block type
                if char in "12345":  # Counter blocks 1-5
                    hits = int(char)
                    if isinstance(block, CounterBlock):
                        block.hits_remaining = hits + 1
                        if block.animation_frames and 0 <= (hits - 1) < len(
                            block.animation_frames
                        ):
                            block.animation_frame = hits - 1
                elif char == "0":  # Special case for '0' counter blocks
                    if isinstance(block, CounterBlock):
                        block.hits_remaining = 1
                        block.animation_frame = 0
                    block.image_file = (
                        "cntblk.png"  # The base counter block image without a number
                    )
                    block.animation_frames = None

                # Add block to manager
                self.block_manager.blocks.append(block)

    def _set_level_background(self) -> None:
        """Set the appropriate background for the current level.

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
        self.logger.info(
            f"Setting level {self.current_level} background to: {bg_file} (background {self.current_background})"
        )

        # Set the play area background
        self.layout.set_play_background(bg_index)

    def _get_level_file_path(self, level_num: int) -> str:
        """Get the file path for a specific level number.

        Args:
        ----
            level_num (int): Level number (1-80)

        Returns:
        -------
            str: Path to the level file

        """
        # Format level number with leading zeros (level01.data)
        level_file = f"level{level_num:02d}.data"
        return os.path.join(self.levels_dir, level_file)

    def _parse_level_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Parse an XBoing level file.

        Args:
        ----
            file_path (str): Path to the level file

        Returns:
        -------
            Optional[Dict[str, Any]]: Dictionary with level data (title, time_bonus, layout)
                  or None if parsing failed

        """
        try:
            with open(file_path, encoding="utf-8") as f:
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
            self.logger.error(f"Error parsing level file {file_path}: {e}")
            return None
