"""Block and CounterBlock classes for XBoing: represent and manage block objects in the game."""

import logging
import random
from typing import Any, Optional, Tuple

import pygame

from xboing.game.block_types import (
    ROAMER_BLK,
    SPECIAL_BLOCK_TYPES,
    UNBREAKABLE_BLOCK_TYPES,
)
from xboing.renderers.block_renderer import BlockRenderer
from xboing.utils.block_type_loader import BlockTypeData


class Block:
    """A sprite-based breakable block in the game (formerly SpriteBlock)."""

    logger = logging.getLogger("xboing.Block")

    def __init__(self, x: int, y: int, config: BlockTypeData) -> None:
        """Initialize a sprite-based block using config data from block_types.json.

        Args:
        ----
            x (int): X position
            y (int): Y position
            config (BlockTypeData): Block type configuration dict

        """
        self.x: int = x
        self.y: int = y
        self.config: BlockTypeData = config
        self.type: str = config.get("blockType", "UNKNOWN")
        self.width: int = config.get("width", 40)
        self.height: int = config.get("height", 20)
        self.rect: pygame.Rect = pygame.Rect(x, y, self.width, self.height)
        self.image_file: str = config.get("main_sprite", "").replace(".xpm", ".png")
        # Ensure points is always an int
        points_val = config.get("points", 0)
        try:
            self.points: int = int(points_val)
        except (TypeError, ValueError):
            self.points = 0
        self.explosion_frames: list[str] = [
            f.replace(".xpm", ".png") for f in config.get("explosion_frames", [])
        ]
        anim = config.get("animation_frames")
        self.animation_frames: Optional[list[str]] = (
            [f.replace(".xpm", ".png") for f in anim] if anim else None
        )
        # Block state - set initial health based on config (add a 'health' or 'hits' field to JSON if needed)
        self.health = config.get("hits", 1)
        self.is_hit: bool = False
        self.hit_timer: float = 0.0
        self.animation_frame: int = 0
        self.animation_timer: float = 0.0
        self.animation_speed: int = 200  # ms per frame
        # For special blocks, set up animation frames (if needed)
        image_override: Optional[pygame.Surface] = None
        # For roamer blocks which move
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
            img = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(
                img, (255, 0, 255), pygame.Rect(0, 0, self.width, self.height)
            )
            self.image = img
        self.state: str = "normal"  # 'normal', 'breaking', 'destroyed'
        self.explosion_frame_index: int = 0
        self.explosion_timer: float = 0.0
        self.explosion_frame_duration: float = 80.0  # ms per frame

    def __repr__(self) -> str:
        """Return a string representation of the block."""
        return f"Block(x={self.x}, y={self.y}, type={self.type}, state={self.state})"

    def update(self, delta_ms: float) -> None:
        """Update the block's state.

        Args:
        ----
            delta_ms (float): Time since last frame in milliseconds

        """
        # Update hit animation
        if self.is_hit:
            self.hit_timer -= delta_ms
            if self.hit_timer <= 0:
                self.is_hit = False
        # Update animations for special blocks
        if self.animation_frames:
            self.animation_timer += delta_ms
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                frame_index = (self.animation_frame + 1) % len(self.animation_frames)
                self.animation_frame = int(frame_index)
        # Update roamer movement
        if self.type == ROAMER_BLK and self.direction:
            self.move_timer += delta_ms
            if self.move_timer >= self.move_interval:
                self.move_timer = 0
                self.set_random_direction()
        # Handle breaking/explosion animation
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
                x=self.x,
                y=self.y,
                width=self.width,
                height=self.height,
                block_type=self.type,
                image_file=frame_file,
                is_hit=False,
            )
        else:
            BlockRenderer.render(
                surface=surface,
                x=self.x,
                y=self.y,
                width=self.width,
                height=self.height,
                block_type=self.type,
                image_file=self.image_file,
                is_hit=self.is_hit,
                animation_frame=self.animation_frame if self.animation_frames else None,
                animation_frames=self.animation_frames,
                direction=self.direction if self.type == ROAMER_BLK else None,
            )

    def get_rect(self) -> pygame.Rect:
        """Get the block's collision rectangle."""
        return self.rect

    def is_broken(self) -> bool:
        """Check if the block is broken."""
        return self.health <= 0


class CounterBlock(Block):
    """A block that requires multiple hits to break (counter block)."""

    def __init__(self, x: int, y: int, config: BlockTypeData) -> None:
        super().__init__(x, y, config)
        self.hits_remaining: int = config.get("hits", 5)

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
                x=self.x,
                y=self.y,
                width=self.width,
                height=self.height,
                block_type=self.type,
                image_file=frame_file,
                is_hit=False,
            )
        else:
            counter_value = self.hits_remaining - 2 if self.hits_remaining > 1 else None
            BlockRenderer.render(
                surface=surface,
                x=self.x,
                y=self.y,
                width=self.width,
                height=self.height,
                block_type=self.type,
                image_file=self.image_file,
                is_hit=self.is_hit,
                animation_frames=self.animation_frames,
                counter_value=counter_value,
            )
