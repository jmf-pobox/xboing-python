"""Block and CounterBlock classes for XBoing: represent and manage block objects in the game."""

import logging
import random
from typing import Any, List, Optional, Tuple

import pygame

from xboing.game.block_types import (
    ROAMER_BLK,
    SPECIAL_BLOCK_TYPES,
    UNBREAKABLE_BLOCK_TYPES,
)
from xboing.game.game_shape import GameShape
from xboing.renderers.block_renderer import BlockRenderer
from xboing.utils.block_type_loader import BlockTypeData


class Block(GameShape):
    """A sprite-based breakable block in the game (formerly SpriteBlock)."""

    logger = logging.getLogger("xboing.Block")

    def __init__(self, x: int, y: int, config: BlockTypeData) -> None:
        """Initialize a sprite-based block using config data from block_types.json.

        Args:
            x (int): X position
            y (int): Y position
            config (BlockTypeData): Block type configuration dict

        """
        # --- Geometry and Base Class Init ---
        width: int = _safe_int(config.get("width", 40), 40)
        height: int = _safe_int(config.get("height", 20), 20)
        super().__init__(x, y, width, height)

        # --- Block Type and Image Setup ---
        self.config: BlockTypeData = config
        self.type: str = config.get("blockType", "UNKNOWN")
        self.image_file: str = config.get("main_sprite", "").replace(".xpm", ".png")

        # --- Points/Scoring ---
        self.points: int = _safe_int(config.get("points", 0), 0)

        # --- Animation and Explosion Frames ---
        explosion_frames_val = config.get("explosion_frames", [])
        self.explosion_frames: List[str] = [
            str(f).replace(".xpm", ".png") for f in explosion_frames_val
        ]
        anim = config.get("animation_frames")
        self.animation_frames: Optional[List[str]] = (
            [str(f).replace(".xpm", ".png") for f in anim] if anim else None
        )

        # --- Block State and Health ---
        self.health = _safe_int(config.get("hits", 1), 1)
        self.is_hit: bool = False
        self.hit_timer: float = 0.0
        self.animation_frame: int = 0
        self.animation_timer: float = 0.0
        self.animation_speed: int = 200  # ms per frame

        # --- Special Block Animation/Image Setup ---
        image_override: Optional[pygame.Surface] = None
        self.direction: Optional[str] = None
        self.move_timer: float = 0.0
        self.move_interval: int = 1000  # ms between movements
        if self.type == ROAMER_BLK:
            self.direction = "idle"
        self.image: Optional[pygame.Surface] = None
        if image_override is not None:
            self.image = image_override
        # If image is not available, log error and use a placeholder
        elif self.image_file:
            pass  # Image loading handled by renderer
        else:
            self.logger.warning(
                f"Error: Missing block image '{self.image_file}' for block type {self.type}"
            )
            img = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            pygame.draw.rect(
                img, (255, 0, 255), pygame.Rect(0, 0, self.rect.width, self.rect.height)
            )
            self.image = img

        # --- Breaking/Explosion State ---
        self.state: str = "normal"  # 'normal', 'breaking', 'destroyed'
        self.explosion_frame_index: int = 0
        self.explosion_timer: float = 0.0
        self.explosion_frame_duration: float = 80.0  # ms per frame

    def __repr__(self) -> str:
        """Return a string representation of the block."""
        return f"Block(x={self.rect.x}, y={self.rect.y}, type={self.type}, state={self.state})"

    def update(self, delta_ms: float) -> None:
        """Update the block's state.

        Args:
            delta_ms (float): Time since last frame in milliseconds

        """
        # --- Hit Animation Section ---
        if self.is_hit:
            self.hit_timer -= delta_ms
            if self.hit_timer <= 0:
                self.is_hit = False

        # --- Special Block Animation Section ---
        if self.animation_frames:
            self.animation_timer += delta_ms
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                frame_index = (self.animation_frame + 1) % len(self.animation_frames)
                self.animation_frame = int(frame_index)

        # --- Roamer Movement Section ---
        if self.type == ROAMER_BLK and self.direction:
            self.move_timer += delta_ms
            if self.move_timer >= self.move_interval:
                self.move_timer = 0
                self.set_random_direction()

        # --- Breaking/Explosion Animation Section ---
        if self.state == "breaking":
            self.explosion_timer += delta_ms
            if self.explosion_timer >= self.explosion_frame_duration:
                self.explosion_timer = 0.0
                self.explosion_frame_index += 1
                if self.explosion_frame_index >= len(self.explosion_frames):
                    self.state = "destroyed"

    def set_random_direction(self) -> None:
        """Set a random direction for roamer blocks."""
        directions = ["idle", "up", "down", "left", "right"]
        self.direction = random.choice(directions)

    def hit(self) -> Tuple[bool, int, Optional[Any]]:
        """Handle the block being hit by a ball.

        Returns
        -------
            tuple: (broken, points, effect) - Whether the block was broken, points earned, and any special effect

        """
        broken = False
        points = 0
        effect = None
        if self.type in UNBREAKABLE_BLOCK_TYPES:
            pass
        elif self.type in SPECIAL_BLOCK_TYPES:
            self.health -= 1
            if self.health <= 0:
                broken = True
                points = self.points
                effect = self.type
        else:
            self.health -= 1
            if self.health <= 0:
                broken = True
                points = self.points
        if broken:
            self.state = "breaking"
            self.explosion_frame_index = 0
            self.explosion_timer = 0.0
        return broken, points, effect

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the block using BlockRenderer."""
        # --- Breaking/Explosion Drawing Section ---
        if self.state == "breaking":
            if not self.explosion_frames:
                # No explosion animation: immediately mark as destroyed and skip drawing
                self.state = "destroyed"
                return
            frame_file = self.explosion_frames[
                min(self.explosion_frame_index, len(self.explosion_frames) - 1)
            ]
            BlockRenderer.render(
                surface=surface,
                x=self.rect.x,
                y=self.rect.y,
                width=self.rect.width,
                height=self.rect.height,
                block_type=self.type,
                image_file=frame_file,
                is_hit=False,
            )
        else:
            BlockRenderer.render(
                surface=surface,
                x=self.rect.x,
                y=self.rect.y,
                width=self.rect.width,
                height=self.rect.height,
                block_type=self.type,
                image_file=self.image_file,
                is_hit=self.is_hit,
                animation_frame=self.animation_frame if self.animation_frames else None,
                animation_frames=self.animation_frames,
            )

    def get_rect(self) -> pygame.Rect:
        """Get the block's collision rectangle."""
        return self.rect

    def is_broken(self) -> bool:
        """Check if the block is broken."""
        return bool(self.health <= 0)


class CounterBlock(Block):
    """A block that requires multiple hits to break (counter block)."""

    def __init__(self, x: int, y: int, config: BlockTypeData) -> None:
        super().__init__(x, y, config)
        self.hits_remaining: int = _safe_int(config.get("hits", 5), 5)

    def hit(self) -> Tuple[bool, int, Optional[Any]]:
        broken = False
        points = 0
        effect = None
        if self.hits_remaining > 0:
            self.hits_remaining -= 1
            self.is_hit = True
            self.hit_timer = 200
            # Update animation frame based on hits_remaining
            if self.animation_frames and 0 <= self.hits_remaining < len(
                self.animation_frames
            ):
                self.animation_frame = self.hits_remaining
        if self.hits_remaining == 0:
            broken = True
            points = self.points
            self.state = "breaking"
            self.explosion_frame_index = 0
            self.explosion_timer = 0.0
        return broken, points, effect

    def draw(self, surface: pygame.Surface) -> None:
        if self.state == "breaking":
            if not self.explosion_frames:
                self.state = "destroyed"
                return
            frame_file = self.explosion_frames[
                min(self.explosion_frame_index, len(self.explosion_frames) - 1)
            ]
            BlockRenderer.render(
                surface=surface,
                x=self.rect.x,
                y=self.rect.y,
                width=self.rect.width,
                height=self.rect.height,
                block_type=self.type,
                image_file=frame_file,
                is_hit=False,
            )
        else:
            counter_value = self.hits_remaining - 2 if self.hits_remaining > 1 else None
            BlockRenderer.render(
                surface=surface,
                x=self.rect.x,
                y=self.rect.y,
                width=self.rect.width,
                height=self.rect.height,
                block_type=self.type,
                image_file=self.image_file,
                is_hit=self.is_hit,
                animation_frames=self.animation_frames,
                counter_value=counter_value,
            )


def _safe_int(val: Any, default: int = 0) -> int:
    try:
        if val is None:
            return default
        return int(val)
    except (TypeError, ValueError):
        return default
