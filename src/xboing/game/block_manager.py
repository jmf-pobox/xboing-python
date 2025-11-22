"""BlockManager: manages all block objects in the game, including creation, updates, and removal."""

import functools
import logging
from typing import Any, Callable, List, Optional, Tuple, Union

import pygame

from xboing.engine.events import BlockHitEvent
from xboing.game.ball import Ball
from xboing.game.block import Block, CounterBlock
from xboing.game.block_types import BLACK_BLK, COUNTER_BLK, SPECIAL_BLOCK_TYPES
from xboing.game.bullet import Bullet
from xboing.renderers.block_renderer import BlockRenderer
from xboing.utils.asset_paths import get_blocks_dir
from xboing.utils.block_type_loader import get_block_types


class BlockManager:
    """Manages sprite-based blocks in the game (formerly SpriteBlockManager)."""

    def __init__(self, offset_x: int = 0, offset_y: int = 0) -> None:
        """Initialize the block manager.

        Args:
        ----
            offset_x (int): X offset for all blocks (for positioning within play area)
            offset_y (int): Y offset for all blocks (for positioning within play area)

        """
        self.logger = logging.getLogger("xboing.BlockManager")
        # Original XBoing block dimensions and spacing
        self.brick_width = 40  # BLOCK_WIDTH in original XBoing
        self.brick_height = 20  # BLOCK_HEIGHT in original XBoing

        # Based on precise calculations:
        # (495 px play width - 360px for 9 blocks - 20px for wall spacing) /
        # 8 spaces = 14.375 px
        self.spacing = 14  # Calculated optimal horizontal spacing

        # Set vertical spacing to exactly a fixed value of 12 pixels
        # as requested to match the original game spacing
        self.vertical_spacing = 12

        self.offset_x = offset_x
        self.offset_y = offset_y
        self.blocks: List[Block] = []

        # Get blocks directory using the asset path utility
        blocks_dir = get_blocks_dir()
        self.logger.info(f"Using block images from {blocks_dir}")

        self.block_type_data = get_block_types()  # key: str -> BlockTypeData
        BlockRenderer.preload_images(self.block_type_data, blocks_dir)

    def update(self, delta_ms: float) -> None:
        """Update all blocks and remove those whose explosion animation is finished."""
        for block in self.blocks:
            block.update(delta_ms)
            # Reset hit_this_frame flag at the end of each frame
            block.hit_this_frame = False
        # Remove blocks whose explosion animation is finished
        self.blocks = [b for b in self.blocks if b.state != "destroyed"]

    @functools.singledispatchmethod
    def check_collisions(self, obj: object) -> Tuple[int, int, List[Any]]:
        """Dispatch collision checking based on the object type."""
        raise NotImplementedError(f"Unsupported collision object type: {type(obj)}")

    @check_collisions.register(Ball)
    def _(self, ball: Ball) -> Tuple[int, int, List[Any]]:
        """Check for collisions between a ball and all blocks."""
        return self._check_block_collision(
            obj=ball,
            get_position=ball.get_position,
            radius=ball.radius,
            is_bullet=False,
            remove_callback=None,
        )

    @check_collisions.register(Bullet)
    def _(self, bullet: Bullet) -> Tuple[int, int, List[Any]]:
        """Check for collisions between a bullet and all blocks."""

        def remove_bullet() -> None:
            bullet.active = False  # Mark the bullet as inactive

        return self._check_block_collision(
            obj=bullet,
            get_position=lambda: (bullet.x, bullet.y),
            radius=bullet.radius,
            is_bullet=True,
            remove_callback=remove_bullet,
        )

    @staticmethod
    def _collides_with_block(
        obj_x: float, obj_y: float, obj_radius: float, block_rect: pygame.Rect
    ) -> bool:
        """Return True if the object at (obj_x, obj_y) with radius collides with the block rect."""
        # First do a quick AABB check to avoid expensive distance calculations
        # Use a slightly larger radius for more reliable collision detection
        effective_radius = obj_radius * 1.05  # 5% larger radius for better detection

        if not (
            block_rect.left - effective_radius
            <= obj_x
            <= block_rect.right + effective_radius
            and block_rect.top - effective_radius
            <= obj_y
            <= block_rect.bottom + effective_radius
        ):
            return False

        # Find the closest point on the block to the object
        closest_x = max(block_rect.left, min(obj_x, block_rect.right))
        closest_y = max(block_rect.top, min(obj_y, block_rect.bottom))

        # Calculate distance to closest point
        dx = obj_x - closest_x
        dy = obj_y - closest_y
        distance_squared = dx * dx + dy * dy

        # Check if distance is less than radius (using effective radius)
        return distance_squared <= effective_radius * effective_radius

    @staticmethod
    def _reflect_ball(
        obj: Union[Ball, Bullet], obj_x: float, obj_y: float, block: Block
    ) -> None:
        """Reflect the ball's velocity and move it out of collision with the block."""
        # Find the closest point on the block to the object
        closest_x = max(block.rect.left, min(obj_x, block.rect.right))
        closest_y = max(block.rect.top, min(obj_y, block.rect.bottom))

        # Calculate normal vector
        dx = obj_x - closest_x
        dy = obj_y - closest_y
        distance = (dx * dx + dy * dy) ** 0.5

        # Check if ball is inside or very close to the block
        is_inside = (
            block.rect.left <= obj_x <= block.rect.right
            and block.rect.top <= obj_y <= block.rect.bottom
        )

        # Handle edge case where ball is exactly at closest point or inside block
        if distance < 0.0001 or is_inside:
            # If ball is inside block, use a more aggressive approach to push it out
            # First, find the nearest edge
            left_dist = abs(obj_x - block.rect.left)
            right_dist = abs(obj_x - block.rect.right)
            top_dist = abs(obj_y - block.rect.top)
            bottom_dist = abs(obj_y - block.rect.bottom)

            # Find the minimum distance to an edge
            min_dist = min(left_dist, right_dist, top_dist, bottom_dist)

            # Push out in the direction of the nearest edge
            if min_dist == left_dist:
                nx, ny = -1, 0  # Push left
            elif min_dist == right_dist:
                nx, ny = 1, 0  # Push right
            elif min_dist == top_dist:
                nx, ny = 0, -1  # Push up
            else:  # bottom_dist
                nx, ny = 0, 1  # Push down

            # Set a minimum distance to ensure the ball is pushed out
            distance = min(distance, 0.0001)
        else:
            nx = dx / distance
            ny = dy / distance

        # Determine if this is a corner collision
        is_corner = closest_x != obj_x and closest_y != obj_y

        # For corner collisions, use a more precise reflection
        if is_corner:
            # Calculate reflection based on corner normal
            dot = obj.vx * nx + obj.vy * ny
            obj.vx -= 2 * dot * nx
            obj.vy -= 2 * dot * ny
        # For edge collisions, use a simpler reflection
        # Determine which side was hit
        elif closest_x in (block.rect.left, block.rect.right):
            # Horizontal collision (left or right side)
            obj.vx = -obj.vx
        else:
            # Vertical collision (top or bottom)
            obj.vy = -obj.vy

        # Move ball out of collision with a larger buffer for more reliable separation
        overlap = obj.radius - distance
        if overlap > 0 or is_inside:
            # Add a larger buffer to prevent getting between blocks
            # Use an even larger buffer if the ball is inside the block
            buffer = 3.0 if is_inside else 1.5
            overlap += buffer
            obj.x += nx * overlap
            obj.y += ny * overlap
            obj.update_rect()

        # Ensure minimum velocity to prevent getting stuck
        min_speed = 3.0  # Minimum speed
        current_speed = (obj.vx * obj.vx + obj.vy * obj.vy) ** 0.5
        if current_speed < min_speed:
            scale = min_speed / current_speed if current_speed > 0 else 1.0
            obj.vx *= scale
            obj.vy *= scale

        # Normalize velocity to maintain consistent speed
        target_speed = 5.0  # Target speed after collision
        current_speed = (obj.vx * obj.vx + obj.vy * obj.vy) ** 0.5
        if current_speed > 0:
            scale = target_speed / current_speed
            obj.vx *= scale
            obj.vy *= scale

    def _handle_block_hit(self, block: Block) -> Tuple[bool, int, Any]:
        """Handle the result of hitting a block."""
        self.logger.debug(f"Block hit: [{block}]")
        broken, points, effect = block.hit()

        # Post BlockHitEvent for normal blocks
        if broken and effect not in SPECIAL_BLOCK_TYPES:
            pygame.event.post(
                pygame.event.Event(pygame.USEREVENT, {"event": BlockHitEvent()})
            )

        return broken, points, effect

    def _check_block_collision(
        self,
        obj: Union[Ball, Bullet],
        get_position: Callable[[], Tuple[float, float]],
        radius: float,
        is_bullet: bool,
        remove_callback: Optional[Callable[[], None]] = None,
    ) -> Tuple[int, int, List[Any]]:
        """Shared collision logic for balls and bullets."""
        points = 0
        broken_blocks = 0
        effects: List[Any] = []
        obj_x, obj_y = get_position()
        obj_radius = radius

        # Find the closest block for reflection
        closest_block = None
        min_distance = float("inf")

        # First pass: find the closest block for reflection
        if not is_bullet:
            for block in self.blocks[:]:
                # Skip destroyed blocks and blocks in breaking state for collision
                if block.state != "normal":
                    continue
                # Skip blocks that have already been hit this frame
                if block.hit_this_frame:
                    continue
                if self._collides_with_block(obj_x, obj_y, obj_radius, block.rect):
                    # Calculate distance to block center
                    block_center_x = block.rect.centerx
                    block_center_y = block.rect.centery
                    dx = obj_x - block_center_x
                    dy = obj_y - block_center_y
                    distance = (dx * dx + dy * dy) ** 0.5

                    if distance < min_distance:
                        min_distance = distance
                        closest_block = block

        # Reflect off the closest block if found
        if not is_bullet and closest_block is not None:
            self._reflect_ball(obj, obj_x, obj_y, closest_block)
            # Process hit for the closest block
            broken, block_points, effect = self._handle_block_hit(closest_block)
            if broken:
                points += block_points
                broken_blocks += 1
                if effect is not None:
                    effects.append(effect)
                    # Check for death effect immediately after adding it
                    if effect == "death" and not is_bullet:
                        obj.active = False
        # For bullets, process all collisions
        elif is_bullet:
            for block in self.blocks[:]:
                # Skip destroyed blocks and blocks in breaking state for collision
                if block.state != "normal":
                    continue
                # Skip blocks that have already been hit this frame
                if block.hit_this_frame:
                    continue
                if self._collides_with_block(obj_x, obj_y, obj_radius, block.rect):
                    # Process hit for the block
                    broken, block_points, effect = self._handle_block_hit(block)
                    if broken:
                        points += block_points
                        broken_blocks += 1
                        if effect is not None:
                            effects.append(effect)
                    if remove_callback:
                        remove_callback()
                        # For bullets, we still break after the first collision
                        break
        return points, broken_blocks, effects

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all blocks.

        Args:
        ----
            surface (pygame.Surface): Surface to draw on

        """
        for block in self.blocks:
            block.draw(surface)

    def get_block_count(self) -> int:
        """Get the number of remaining blocks."""
        return len(self.blocks)

    def get_breakable_count(self) -> int:
        """Get the number of breakable blocks (excluding unbreakable ones)."""
        return sum(1 for block in self.blocks if block.type != BLACK_BLK)

    def remaining_blocks(self) -> int:
        """Return the number of blocks that are not broken."""
        count: int = len([b for b in self.blocks if not b.is_broken()])
        return count

    def reflect_ball(
        self, obj: Union[Ball, Bullet], obj_x: float, obj_y: float, block: Block
    ) -> None:
        """Reflect the ball's velocity and move it out of collision with the block.

        Args:
            obj: The ball or bullet to reflect
            obj_x: The x-coordinate of the object
            obj_y: The y-coordinate of the object
            block: The block the object collided with

        """
        self._reflect_ball(obj, obj_x, obj_y, block)

    def create_block(
        self, x: int, y: int, width: int, height: int, block_type: str = "normal"
    ) -> Union[Block, CounterBlock]:
        """Create a block at the specified position."""
        config = self.block_type_data.get(block_type, {})
        config["width"] = width
        config["height"] = height

        # Create the appropriate block type
        if block_type == COUNTER_BLK:
            block: Union[Block, CounterBlock] = CounterBlock(x, y, config)
        else:
            block = Block(x, y, config)
        return block
