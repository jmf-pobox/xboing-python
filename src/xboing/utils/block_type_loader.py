"""Loader utility for block_types.json, providing type-safe access to block type data."""

import json
import logging
import os
from typing import Dict, List, Optional, TypedDict

from .asset_paths import get_asset_path

BLOCK_TYPES_PATH = get_asset_path("config/block_types.json")

logger = logging.getLogger("xboing.BlockTypeLoader")


class BlockTypeData(TypedDict, total=False):
    """TypedDict for block type configuration loaded from block_types.json."""

    blockType: str
    width: int
    height: int
    slide: int
    main_sprite: str
    explosion_frames: List[str]
    points: int
    has_explosion: bool
    special_behavior: Optional[str]
    animation_frames: Optional[List[str]]
    draw_size: List[int]
    notes: Optional[str]


def get_block_types() -> Dict[str, BlockTypeData]:
    """Load and validate block types from block_types.json.

    Returns
    -------
        Dict[str, BlockTypeData]: Mapping from blockType name to its data.

    Raises
    ------
        FileNotFoundError: If the JSON file is missing.
        ValueError: If the JSON is invalid or required fields are missing.

    """
    if not os.path.exists(BLOCK_TYPES_PATH):
        raise FileNotFoundError(f"Block types file not found: {BLOCK_TYPES_PATH}")
    with open(BLOCK_TYPES_PATH, encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("block_types.json must be a list of block type objects")
    block_types: Dict[str, BlockTypeData] = {}
    for entry in data:
        # Validate required fields
        missing = [
            field
            for field in ["blockType", "main_sprite", "points"]
            if field not in entry
        ]
        if missing:
            logger.warning(
                f"Block type entry missing fields: {missing} (entry: {entry})"
            )
            continue
        block_type = entry["blockType"]
        block_types[block_type] = entry
    return block_types
