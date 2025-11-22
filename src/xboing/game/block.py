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
from xboing.game.collision import CollisionType
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
        self.health = 1
        self.is_hit: bool = False
        self.hit_timer: float = 0.0
        self.animation_frame: int = 0
        self.animation_timer: float = 0.0
        self.animation_speed: int = 200  # ms per frame
        self.hit_this_frame: bool = False  # Track if block was hit in current frame

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
        # If the image is not available, log an error and use a placeholder
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

    def is_broken(self) -> bool:
        """Check if the block is broken."""
        return self.health <= 0

    def update(self, delta_ms: float) -> List[pygame.event.Event]:
        """Update the block's state.

        Args:
            delta_ms (float): Time since the last frame in milliseconds

        Returns:
            List[pygame.event.Event]: List of events generated during the update

        """
        events: List[pygame.event.Event] = []
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

        return events

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
        # If the block was already hit this frame, don't process it again
        if self.hit_this_frame:
            return False, 0, None

        # Mark the block as hit this frame
        self.hit_this_frame = True

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
            self._draw_breaking_state(surface)
        else:
            self._draw_normal_state(surface)

    def _draw_breaking_state(self, surface: pygame.Surface) -> None:
        """Draw the block in the breaking/explosion state."""
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

    def _draw_normal_state(self, surface: pygame.Surface) -> None:
        """Draw the block in its normal state."""
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

    def collides_with(self, other: Any) -> bool:
        """Check if this block collides with another collidable object.

        Args:
            other: Another collidable object to check collision with.

        Returns:
            True if the objects collide, False otherwise.

        """
        return self.rect.colliderect(other.get_rect())

    def is_active(self) -> bool:
        """Check if the block is currently active.

        Returns:
            True if the block is active (not destroyed), False otherwise.

        """
        # Only consider blocks in normal state as active for collision purposes
        return self.state == "normal"

    def set_active(self, active: bool) -> None:
        """Set the block's active state.

        Args:
            active: The new active state. If False, the block will be marked as destroyed.

        """
        if not active:
            self.state = "destroyed"
        elif self.state == "destroyed":
            self.state = "normal"

    def get_collision_type(self) -> str:
        """Return the collision type for Block."""
        return CollisionType.BLOCK.value

    def handle_collision(self, other: object) -> None:
        """Handle collision with another object (no-op for Block stub)."""
        del other  # Remove unused argument warning


class CounterBlock(Block):
    """A block that requires multiple hits to break and displays a counter."""

    def __init__(self, x: int, y: int, config: BlockTypeData) -> None:
        # Call parent initialization but with health=0 (we'll use hits_remaining instead)
        # This prevents the parent's health from being used
        super().__init__(x, y, config)
        self.logger = logging.getLogger("xboing.CounterBlock")

        # We still need hits_remaining for CounterBlock specific behavior
        self.hits_remaining = _safe_int(config.get("hits", 5), 5)
        self.logger.debug(
            f"CounterBlock initialized at ({x}, {y}) with {self.hits_remaining} hits"
        )

    def hit(self) -> Tuple[bool, int, Optional[Any]]:
        """Handle CounterBlock being hit."""
        broken = False
        points = 0
        effect = None

        if self.hits_remaining > 0:
            self.hits_remaining -= 1
            self.is_hit = True
            self.hit_timer = 200
            self.logger.debug(
                f"CounterBlock hit, remaining hits: {self.hits_remaining}, animation_frames: {self.animation_frames}"
            )

            # Only update animation frame if animation frames are enabled
            if self.animation_frames and 0 <= self.hits_remaining < len(
                self.animation_frames
            ):
                self.animation_frame = self.hits_remaining
                self.logger.debug(f"Updated animation frame to {self.animation_frame}")

        if self.hits_remaining == 0:
            broken = True
            points = self.points
            self.state = "breaking"
            self.explosion_frame_index = 0
            self.explosion_timer = 0.0
            self.logger.debug("CounterBlock broken")

        return broken, points, effect

    def _draw_normal_state(self, surface: pygame.Surface) -> None:
        """Override normal state drawing to include the counter."""
        # Decide which image to use
        if self.hits_remaining > 1 and self.animation_frames:
            image_file = self.animation_frames[self.hits_remaining - 2]
        else:
            image_file = "cntblk.png"
        counter_value = self.hits_remaining if self.hits_remaining > 1 else None
        self.logger.debug(
            f"Drawing CounterBlock with hits_remaining={self.hits_remaining}, image_file={image_file}, animation_frames={self.animation_frames}, animation_frame={self.animation_frame}"
        )

        BlockRenderer.render(
            surface=surface,
            x=self.rect.x,
            y=self.rect.y,
            width=self.rect.width,
            height=self.rect.height,
            block_type=self.type,
            image_file=image_file,
            is_hit=self.is_hit,
            animation_frames=None,  # Don't animate
            counter_value=counter_value,
        )

    # Override is_broken to use hits_remaining instead of health
    def is_broken(self) -> bool:
        """Check if the CounterBlock is broken."""
        return self.hits_remaining <= 0


def _safe_int(val: Any, default: int = 0) -> int:
    try:
        if val is None:
            return default
        return int(val)
    except (TypeError, ValueError):
        return default
