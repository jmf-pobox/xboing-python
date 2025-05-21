"""BlockManager: manages all block objects in the game, including creation, updates, and removal."""

import functools
import logging
from typing import Any, Callable, List, Optional, Tuple, Union

import pygame

from xboing.game.ball import Ball
from xboing.game.block import Block, CounterBlock
from xboing.game.block_types import BLACK_BLK, COUNTER_BLK
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
        # (495px play width - 360px for 9 blocks - 20px for wall spacing) / 8 spaces = 14.375px
        self.spacing = 14  # Calculated optimal horizontal spacing

        # Set vertical spacing to exactly a fixed value of 12 pixels
        # as requested to match the original game spacing
        self.vertical_spacing = 12

        self.offset_x = offset_x
        self.offset_y = offset_y
        self.blocks: List[Block] = []

        # Get blocks directory using asset path utility
        blocks_dir = get_blocks_dir()
        self.logger.info(f"Using block images from {blocks_dir}")

        self.block_type_data = get_block_types()  # key: str -> BlockTypeData
        BlockRenderer.preload_images(self.block_type_data, blocks_dir)

    def update(self, delta_ms: float) -> None:
        """Update all blocks and remove those whose explosion animation is finished."""
        for block in self.blocks:
            block.update(delta_ms)
        # Remove blocks whose explosion animation is finished
        self.blocks = [b for b in self.blocks if b.state != "destroyed"]

    @functools.singledispatchmethod
    def check_collisions(self, obj: object) -> Tuple[int, int, List[Any]]:
        """Dispatch collision checking based on object type (Ball, Bullet, etc)."""
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
            bullet.active = False  # Mark bullet as inactive (caller should remove)

        return self._check_block_collision(
            obj=bullet,
            get_position=lambda: (bullet.x, bullet.y),
            radius=bullet.radius,
            is_bullet=True,
            remove_callback=remove_bullet,
        )

    def _collides_with_block(
        self, obj_x: float, obj_y: float, obj_radius: float, block_rect: pygame.Rect
    ) -> bool:
        """Return True if the object at (obj_x, obj_y) with radius collides with the block rect."""
        closest_x = max(block_rect.left, min(obj_x, block_rect.right))
        closest_y = max(block_rect.top, min(obj_y, block_rect.bottom))
        dx = obj_x - closest_x
        dy = obj_y - closest_y
        distance = (dx * dx + dy * dy) ** 0.5
        return bool(distance <= obj_radius)

    def _reflect_ball(
        self, obj: Union[Ball, Bullet], obj_x: float, obj_y: float, block: Block
    ) -> None:
        """Reflect the ball's velocity and move it out of collision with the block."""
        closest_x = max(block.rect.left, min(obj_x, block.rect.right))
        closest_y = max(block.rect.top, min(obj_y, block.rect.bottom))
        dx = obj_x - closest_x
        dy = obj_y - closest_y
        distance = (dx * dx + dy * dy) ** 0.5
        if distance > 0:
            nx = dx / distance
            ny = dy / distance
        else:
            nx, ny = 0, -1
        dot = obj.vx * nx + obj.vy * ny
        obj.vx -= 2 * dot * nx
        obj.vy -= 2 * dot * ny
        overlap = obj.radius - distance
        obj.x += nx * overlap
        obj.y += ny * overlap
        obj.update_rect()

    def _handle_block_hit(self, block: Block) -> Tuple[bool, int, Any]:
        """Handle the result of hitting a block."""
        self.logger.debug(f"Block hit: [{block}]")
        return block.hit()

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
        for block in self.blocks[:]:
            # Skip blocks that are breaking or destroyed
            if block.state != "normal":
                continue
            if self._collides_with_block(obj_x, obj_y, obj_radius, block.rect):
                if not is_bullet:
                    self._reflect_ball(obj, obj_x, obj_y, block)
                broken, block_points, effect = self._handle_block_hit(block)
                if broken:
                    points += block_points
                    broken_blocks += 1
                    # Do not remove block here; it will be removed after explosion animation
                    if effect is not None:
                        effects.append(effect)
                if is_bullet and remove_callback:
                    remove_callback()
                if effect == "death" and not is_bullet:
                    obj.active = False
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

    def create_block(self, x: int, y: int, block_type_key: str) -> Block:
        """Create a Block using the canonical key and config from block_types.json."""
        config = self.block_type_data.get(block_type_key)
        if config is None:
            raise ValueError(f"Unknown block type key {block_type_key}")
        if block_type_key == COUNTER_BLK:
            return CounterBlock(x, y, config)
        return Block(x, y, config)
