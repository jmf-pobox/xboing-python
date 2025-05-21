"""Canonical block type constants and groupings for XBoing."""

from typing import Tuple

# Block type string constants (match block_types.json)
RED_BLK: str = "RED_BLK"
BLUE_BLK: str = "BLUE_BLK"
GREEN_BLK: str = "GREEN_BLK"
TAN_BLK: str = "TAN_BLK"
YELLOW_BLK: str = "YELLOW_BLK"
PURPLE_BLK: str = "PURPLE_BLK"
BULLET_BLK: str = "BULLET_BLK"
BLACK_BLK: str = "BLACK_BLK"
COUNTER_BLK: str = "COUNTER_BLK"
BOMB_BLK: str = "BOMB_BLK"
DEATH_BLK: str = "DEATH_BLK"
REVERSE_BLK: str = "REVERSE_BLK"
HYPERSPACE_BLK: str = "HYPERSPACE_BLK"
EXTRABALL_BLK: str = "EXTRABALL_BLK"
MGUN_BLK: str = "MGUN_BLK"
WALLOFF_BLK: str = "WALLOFF_BLK"
MULTIBALL_BLK: str = "MULTIBALL_BLK"
STICKY_BLK: str = "STICKY_BLK"
PAD_SHRINK_BLK: str = "PAD_SHRINK_BLK"
PAD_EXPAND_BLK: str = "PAD_EXPAND_BLK"
DROP_BLK: str = "DROP_BLK"
MAXAMMO_BLK: str = "MAXAMMO_BLK"
ROAMER_BLK: str = "ROAMER_BLK"
TIMER_BLK: str = "TIMER_BLK"
RANDOM_BLK: str = "RANDOM_BLK"
DYNAMITE_BLK: str = "DYNAMITE_BLK"
BONUSX2_BLK: str = "BONUSX2_BLK"
BONUSX4_BLK: str = "BONUSX4_BLK"
BONUS_BLK: str = "BONUS_BLK"
BLACKHIT_BLK: str = "BLACKHIT_BLK"

SPECIAL_BLOCK_TYPES: Tuple[str, ...] = (
    BOMB_BLK,
    MULTIBALL_BLK,
    BONUSX2_BLK,
    BONUSX4_BLK,
    BONUS_BLK,
    DEATH_BLK,
    REVERSE_BLK,
    HYPERSPACE_BLK,
    EXTRABALL_BLK,
    MGUN_BLK,
    WALLOFF_BLK,
    STICKY_BLK,
    PAD_SHRINK_BLK,
    PAD_EXPAND_BLK,
    DROP_BLK,
    MAXAMMO_BLK,
    ROAMER_BLK,
    TIMER_BLK,
    RANDOM_BLK,
    DYNAMITE_BLK,
    BLACKHIT_BLK,
    BULLET_BLK,
)
"""Block types that trigger special effects when broken."""

NORMAL_BLOCK_TYPES: Tuple[str, ...] = (
    RED_BLK,
    BLUE_BLK,
    GREEN_BLK,
    TAN_BLK,
    YELLOW_BLK,
    PURPLE_BLK,
)
"""Standard destructible block types."""

UNBREAKABLE_BLOCK_TYPES: Tuple[str, ...] = (BLACK_BLK,)
"""Block types that are indestructible."""
