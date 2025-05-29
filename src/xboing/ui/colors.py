"""Color constants for XBoing.

This module defines color constants used throughout the application.
"""

from typing import Tuple

# Basic colors
BLACK: Tuple[int, int, int] = (0, 0, 0)
WHITE: Tuple[int, int, int] = (255, 255, 255)
GREEN: Tuple[int, int, int] = (0, 255, 0)
YELLOW: Tuple[int, int, int] = (255, 255, 0)

# Background colors
DARK_BLUE: Tuple[int, int, int] = (
    20,
    20,
    30,
)  # Dark blue fallback color for main background
MEDIUM_BLUE: Tuple[int, int, int] = (
    40,
    40,
    50,
)  # Medium blue fallback color for play area

# Message colors
MESSAGE_GREEN: Tuple[int, int, int] = (
    GREEN  # Green color for messages and level title messages
)
