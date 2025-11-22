"""Level Manager for XBoing.

This module handles loading, parsing, and managing XBoing level files.
It interfaces with the BlockManager to create the appropriate block layout.
"""

import logging
import os
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Optional

if TYPE_CHECKING:
    from xboing.game.block_manager import BlockManager

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

    # Default time bonus in seconds if not specified in level info
    DEFAULT_TIME_BONUS = 120

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
    CHAR_TO_BLOCK_TYPE: ClassVar[Dict[str, Optional[str]]] = {
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
        "0": COUNTER_BLK,  # Counter block (no number, 1 hit)
        "1": COUNTER_BLK,  # Counter block (shows 1, 2 hits)
        "2": COUNTER_BLK,  # Counter block (shows 2, 3 hits)
        "3": COUNTER_BLK,  # Counter block (shows 3, 4 hits)
        "4": COUNTER_BLK,  # Counter block (shows 4, 5 hits)
        "5": COUNTER_BLK,  # Counter block (shows 5, 6 hits)
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
        self,
        levels_dir: Optional[str] = None,
        layout: Optional[Any] = None,
        starting_level: int = 1,
    ) -> None:
        """Initialize the level manager.

        Args:
            levels_dir: Directory containing level data files. If None, uses the default.
            layout: The game layout to set backgrounds on.
            starting_level: The level to start at (default: 1).

        """
        self.logger = logging.getLogger("xboing.LevelManager")
        self.current_level: int = starting_level
        self.logger.info(
            f"LevelManager __init__: starting_level={starting_level}, current_level={self.current_level}"
        )
        self.level_title: str = ""
        self.time_bonus: int = 0
        self.block_manager: Optional["BlockManager"] = None
        self.layout = layout
        self.current_background: int = self.BACKGROUND_2
        self.levels_dir: str = (
            levels_dir if levels_dir is not None else get_levels_dir()
        )
        self.logger.info(f"Using levels directory: {self.levels_dir}")

    def set_block_manager(self, block_manager: "BlockManager") -> None:
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
            level_num (int): Level number to load. If None, uses current_level.

        Returns:
            bool: True if the level was loaded successfully, False otherwise

        """
        if level_num is not None:
            self.logger.info(f"load_level called with level_num={level_num}")
            self.current_level = level_num
        self.logger.info(f"load_level: current_level={self.current_level}")
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
                self._create_blocks_from_layout(level_data["layout"])
                self._set_level_background()
                result = True

        return result

    def _clamp_level_number(self) -> None:
        if self.current_level < 1:
            self.current_level = 1
        elif self.current_level > self.MAX_LEVELS:
            self.current_level = self.MAX_LEVELS

    @staticmethod
    def _level_file_exists(level_file: str) -> bool:
        return os.path.exists(level_file)

    def _safe_parse_level_file(self, level_file: str) -> Optional[Dict[str, Any]]:
        try:
            return self._parse_level_file(level_file)
        except (OSError, ValueError) as e:
            self.logger.error(f"Error loading level {self.current_level}: {e}")
            return None

    def get_next_level(self) -> bool:
        """Advance to the next level or reset if at the last level."""
        self.logger.info(
            f"get_next_level: current_level before increment={self.current_level}"
        )
        if self.current_level < self.MAX_LEVELS:
            self.current_level += 1
        else:
            self.current_level = 1
        self.logger.info(
            f"get_next_level: current_level after increment={self.current_level}"
        )
        # Update the background cycle (same logic as original XBoing)
        self.current_background += 1
        if self.current_background > self.BACKGROUND_5:
            self.current_background = self.BACKGROUND_2
        return self.load_level()

    def is_level_complete(self) -> bool:
        """Check if the level is complete (all breakable blocks destroyed).

        Returns
        -------
            bool: True if the level is complete, False otherwise

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
        }

    def _create_blocks_from_layout(self, layout: List[str]) -> None:
        """Create blocks from the level layout."""
        self.logger.debug("Creating blocks from layout")
        if not self.block_manager:
            self.logger.error("Block manager not set")
            return

        # Calculate block dimensions and spacing (these should match BlockManager)
        brick_width = self.block_manager.brick_width
        brick_height = self.block_manager.brick_height

        # Clear existing blocks
        self.block_manager.blocks = []

        # Calculate grid dimensions
        wall_spacing = 10  # Wall spacing on each side
        horizontal_spacing = 14  # Exact spacing between blocks
        vertical_spacing = 12  # Exact spacing between rows

        # The left margin is simply the wall spacing (10 px)
        left_margin = wall_spacing

        # Create blocks based on layout
        for row_idx, row in enumerate(layout):
            for col_idx, char in enumerate(row):
                if char == " ":
                    continue

                # Calculate block position with proper spacing
                x = (
                    self.block_manager.offset_x
                    + left_margin
                    + col_idx * (brick_width + horizontal_spacing)
                )
                y = (
                    self.block_manager.offset_y
                    + wall_spacing
                    + row_idx * (brick_height + vertical_spacing)
                )

                # Create block based on character
                block = None
                self.logger.debug(
                    f"Processing character '{char}' at position ({x}, {y})"
                )
                if char in "0123456789":  # Counter blocks 0-9
                    hits = int(char) + 1
                    self.logger.debug(
                        f"Creating counter block with value {char}, hits_required={hits}"
                    )
                    block = self.block_manager.create_block(
                        x, y, brick_width, brick_height, COUNTER_BLK
                    )
                    self.logger.debug(f"Created block: {block}, type: {type(block)}")
                    if isinstance(block, CounterBlock):
                        block.hits_remaining = hits
                        # Set animation frame for numbers > 1
                        if (
                            block.animation_frames
                            and hits > 1
                            and 0 <= (hits - 2) < len(block.animation_frames)
                        ):
                            block.animation_frame = hits - 2
                            self.logger.debug(
                                f"Set animation frame to {block.animation_frame}"
                            )
                        else:
                            block.animation_frame = 0
                        self.logger.debug(
                            f"Counter block created with {block.hits_remaining} hits remaining"
                        )
                    else:
                        self.logger.error(
                            f"Failed to create CounterBlock for character '{char}'"
                        )
                else:
                    # Handle other block types
                    block_type = self.CHAR_TO_BLOCK_TYPE.get(char)
                    if block_type:
                        block = self.block_manager.create_block(
                            x, y, brick_width, brick_height, block_type
                        )
                        self.logger.debug(f"Created block of type {block_type}")

                # Add block to the manager if it was created successfully
                if block is not None:
                    self.block_manager.blocks.append(block)
                    self.logger.debug(f"Added block to manager: {block}")
                else:
                    self.logger.debug(f"No block created for character '{char}'")

    def _set_level_background(self) -> None:
        """Set the appropriate background for the current level.

        In the original XBoing, backgrounds rotate between levels.
        """
        if self.layout is None:
            return

        # In the original XBoing:
        # 1. The main window always uses the space-themed background
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
                    time_bonus = self.DEFAULT_TIME_BONUS

                # Read block layout (remaining lines)
                layout: List[str] = []
                for line in f:
                    row = line.strip()
                    if row:  # Skip empty lines
                        layout.append(row)

                return {"title": title, "time_bonus": time_bonus, "layout": layout}
        except (OSError, ValueError) as e:
            self.logger.error(f"Error parsing level file {file_path}: {e}")
            return None

    def get_current_background_index(self) -> int:
        """Get the current background index for the play area (0-based,
        for bgrnd2.png, bgrnd3.png, etc.).
        """
        return self.current_background - self.BACKGROUND_2
