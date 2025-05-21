"""Stateless renderer for displaying blocks using block sprites and animation frames."""

import logging
import os
from typing import Any, Dict, List, Optional

import pygame

from xboing.game.block_types import COUNTER_BLK
from xboing.utils.asset_paths import get_blocks_dir


class BlockRenderer:
    """Stateless renderer for displaying blocks using block sprites and animation frames."""

    logger = logging.getLogger("xboing.BlockRenderer")

    # Internal image cache
    _image_cache: Dict[str, pygame.Surface] = {}

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the internal image cache."""
        cls.logger.info("Clearing image cache.")
        cls._image_cache.clear()

    @classmethod
    def preload_images(
        cls,
        block_type_data: Dict[str, Any],
        blocks_dir: Optional[str] = None,
        clear_cache: bool = False,
    ) -> None:
        """Preload all block images and animation frames to the cache from block_type_data.

        Args:
            block_type_data: Dictionary containing block type data.
            blocks_dir: Directory containing block images.
            clear_cache: Whether to clear the image cache before preloading.

        """
        if clear_cache:
            cls.clear_cache()
        if blocks_dir is None:
            blocks_dir = get_blocks_dir()
        loaded_count = 0
        failed_count = 0
        cls.logger.info(f"Loading block images from {blocks_dir}")
        for block_info in block_type_data.values():
            # Preload main sprite
            main_sprite = block_info.get("main_sprite")
            if main_sprite:
                path = os.path.join(blocks_dir, main_sprite)
                if main_sprite not in cls._image_cache:
                    try:
                        cls._image_cache[main_sprite] = pygame.image.load(
                            path
                        ).convert_alpha()
                        loaded_count += 1
                    except Exception as e:
                        cls.logger.warning(f"Failed to load {main_sprite}: {e}")
                        failed_count += 1
            # Preload explosion frames
            explosion_frames = block_info.get("explosion_frames") or []
            for frame in explosion_frames:
                path = os.path.join(blocks_dir, frame)
                if frame not in cls._image_cache:
                    try:
                        cls._image_cache[frame] = pygame.image.load(
                            path
                        ).convert_alpha()
                        loaded_count += 1
                    except Exception as e:
                        cls.logger.warning(f"Failed to load {frame}: {e}")
                        failed_count += 1
            # Preload animation frames
            animation_frames = block_info.get("animation_frames") or []
            for frame in animation_frames:
                path = os.path.join(blocks_dir, frame)
                if frame not in cls._image_cache:
                    try:
                        cls._image_cache[frame] = pygame.image.load(
                            path
                        ).convert_alpha()
                        loaded_count += 1
                    except Exception as e:
                        cls.logger.warning(f"Failed to load {frame}: {e}")
                        failed_count += 1
        cls.logger.info(f"Loaded {loaded_count} block images, {failed_count} failed.")

    @classmethod
    def render(
        cls,
        surface: pygame.Surface,
        x: int,
        y: int,
        width: int,
        height: int,
        block_type: str,
        image_file: str,
        is_hit: bool = False,
        animation_frame: Optional[int] = None,
        animation_frames: Optional[List[str]] = None,
        counter_value: Optional[int] = None,
    ) -> None:
        """Render a block at the given position on the surface.

        Args:
        ----
            surface: Surface to draw on.
            x: X position.
            y: Y position.
            width: Block width.
            height: Block height.
            block_type: Block type string (canonical key).
            image_file: Main image file for the block.
            is_hit: Whether the block is being hit (flash effect).
            animation_frame: Current animation frame index (if animated).
            animation_frames: List of animation frame filenames.
            direction: For dynamic blocks, the current direction (if any).
            counter_value: For counter blocks, the current hit count (0-5).

        """
        img: Optional[pygame.Surface] = None
        # Special handling for counter blocks (block_type == COUNTER_BLK)
        if block_type == COUNTER_BLK and counter_value is not None and animation_frames:
            idx = max(0, min(counter_value, len(animation_frames) - 1))
            frame_file = animation_frames[idx]
            img = cls._image_cache.get(frame_file)
            if img is None:
                img = cls._image_cache.get(image_file)
        else:
            # Animation frame selection for other blocks
            if (
                animation_frames is not None
                and animation_frame is not None
                and 0 <= animation_frame < len(animation_frames)
            ):
                frame_file = animation_frames[animation_frame]
                img = cls._image_cache.get(frame_file)
            if img is None:
                img = cls._image_cache.get(image_file)
        if img is None:
            # Placeholder if image missing
            cls.logger.warning(
                f"Missing block image '{image_file}' for block type {block_type}"
            )
            img = pygame.Surface((width, height), pygame.SRCALPHA)
            pygame.draw.rect(img, (255, 0, 255), pygame.Rect(0, 0, width, height))
        # Hit/flash effect
        if is_hit:
            bright_image = img.copy()
            bright_mask = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            bright_mask.fill((100, 100, 100, 0))
            bright_image.blit(bright_mask, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(bright_image, (x, y))
        else:
            surface.blit(img, (x, y))
