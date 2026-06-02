"""Color constants for XBoing.

This module defines color constants used throughout the application.
"""

# Basic colors
BLACK: tuple[int, int, int] = (0, 0, 0)
WHITE: tuple[int, int, int] = (255, 255, 255)
GREEN: tuple[int, int, int] = (0, 255, 0)
YELLOW: tuple[int, int, int] = (255, 255, 0)

# Background colors
DARK_BLUE: tuple[int, int, int] = (
    20,
    20,
    30,
)  # Dark blue fallback color for main background
MEDIUM_BLUE: tuple[int, int, int] = (
    40,
    40,
    50,
)  # Medium blue fallback color for play area

# Message colors
MESSAGE_GREEN: tuple[int, int, int] = (
    GREEN  # Green color for messages and level title messages
)
