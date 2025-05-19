"""BlockManager: manages all block objects in the game, including creation, updates, and removal."""

import functools
import logging
import random
from typing import Any, List, Optional, Tuple

import pygame

from game.ball import Ball
from game.block import Block, CounterBlock
from game.bullet import Bullet
from renderers.block_renderer import BlockRenderer
from utils.asset_paths import get_blocks_dir
from utils.block_type_loader import get_block_types


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

    def create_level(
        self, level_num: int = 1, width: int = 495, top_margin: int = 60
    ) -> List[Block]:
        """Create a level with blocks arranged in a pattern based on the original XBoing.

        Args:
        ----
            level_num (int): Level number to determine difficulty
            width (int): Width of the play area
            top_margin (int): Top margin for blocks

        Returns:
        -------
            List[Block]: The created blocks

        """
        self.blocks = []

        # Set minimal wall spacing to prevent ball passing through sides
        wall_spacing = 10

        # Calculate usable width after wall spacing
        usable_width = width - (wall_spacing * 2)

        # Original XBoing had a maximum of 9 columns
        max_cols = 9

        # Calculate total spacing between blocks
        total_spacing = (max_cols - 1) * self.spacing

        # Calculate total width available for blocks
        total_block_width = usable_width - total_spacing

        # Calculate adjusted block width to fill the playfield
        actual_brick_width = total_block_width // max_cols

        # Use the smaller of the calculated width or standard width
        block_width = min(actual_brick_width, self.brick_width)

        # Calculate left margin to center blocks in play area
        left_margin = (
            wall_spacing
            + (usable_width - (max_cols * block_width + total_spacing)) // 2
        )

        # Original XBoing had a maximum of 18 rows and 9 columns
        max_rows = min(18, 3 + level_num)

        # Create a pattern based on level number
        if level_num == 1:
            # Basic pattern with alternating colored blocks (red, blue, green, yellow, purple)
            block_types = [
                "RED_BLK",
                "BLUE_BLK",
                "GREEN_BLK",
                "YELLOW_BLK",
                "PURPLE_BLK",
            ]

            for row in range(max_rows):
                for col in range(max_cols):
                    # Calculate position with proper spacing
                    x = self.offset_x + left_margin + col * (block_width + 14)
                    y = (
                        self.offset_y
                        + top_margin
                        + row * (self.brick_height + self.vertical_spacing)
                    )

                    # Alternate block types based on row
                    block_type = block_types[row % len(block_types)]

                    # Create the block
                    block = self.create_block(x, y, block_type)
                    self.blocks.append(block)

        elif level_num == 2:
            # Checkerboard pattern
            for row in range(max_rows):
                for col in range(max_cols):
                    if (row + col) % 2 == 0:  # Checkerboard pattern
                        x = self.offset_x + left_margin + col * (block_width + 14)
                        y = (
                            self.offset_y
                            + top_margin
                            + row * (self.brick_height + self.vertical_spacing)
                        )

                        # Alternate between color blocks
                        if row % 3 == 0:
                            block_type = "PURPLE_BLK"
                        elif row % 3 == 1:
                            block_type = "GREEN_BLK"
                        else:
                            block_type = "TAN_BLK"

                        block = self.create_block(x, y, block_type)
                        self.blocks.append(block)

        elif level_num == 3:
            # Mixed block types including special blocks
            for row in range(max_rows):
                for col in range(max_cols):
                    x = self.offset_x + left_margin + col * (block_width + 14)
                    y = (
                        self.offset_y
                        + top_margin
                        + row * (self.brick_height + self.vertical_spacing)
                    )

                    # Determine block type based on position
                    if row == 0:
                        block_type = "BLACK_BLK"  # Unbreakable top row
                    elif row == 1 and col % 3 == 0:
                        block_type = "BOMB_BLK"  # Bombs in second row
                    elif row == 2 and col % 4 == 0:
                        block_type = "EXTRABALL_BLK"  # Extra balls
                    elif row == 3 and col % 2 == 0:
                        block_type = "BONUS_BLK"  # Bonus blocks
                    elif row > 5 and col % 5 == 0:
                        block_type = "MULTIBALL_BLK"  # Multiball blocks
                    else:
                        # Regular color blocks
                        colors = [
                            "RED_BLK",
                            "BLUE_BLK",
                            "GREEN_BLK",
                            "TAN_BLK",
                            "YELLOW_BLK",
                        ]
                        block_type = colors[(row + col) % len(colors)]

                    block = self.create_block(x, y, block_type)
                    self.blocks.append(block)

        else:
            # Higher levels - mix of all block types with some gaps
            block_types = [
                "RED_BLK",
                "BLUE_BLK",
                "GREEN_BLK",
                "TAN_BLK",
                "YELLOW_BLK",
                "PURPLE_BLK",
                "BOMB_BLK",
                "EXTRABALL_BLK",
                "MULTIBALL_BLK",
                "STICKY_BLK",
                "REVERSE_BLK",
                "BONUS_BLK",
                "BONUSX2_BLK",
                "TIMER_BLK",
                "MGUN_BLK",
            ]

            for row in range(max_rows):
                for col in range(max_cols):
                    # Skip some blocks randomly to create gaps
                    if random.random() < 0.2:
                        continue

                    x = self.offset_x + left_margin + col * (block_width + 14)
                    y = (
                        self.offset_y
                        + top_margin
                        + row * (self.brick_height + self.vertical_spacing)
                    )

                    # Randomize block types with occasional special blocks
                    r = random.random()
                    if row == 0 and r < 0.3:
                        block_type = "BLACK_BLK"
                    elif r < 0.05:
                        # Rare blocks
                        rare_blocks = [
                            "ROAMER_BLK",
                            "BONUSX4_BLK",
                            "WALLOFF_BLK",
                        ]
                        block_type = random.choice(rare_blocks)
                    elif r < 0.15:
                        # Uncommon blocks
                        uncommon_blocks = [
                            "BOMB_BLK",
                            "EXTRABALL_BLK",
                            "MULTIBALL_BLK",
                            "BONUSX2_BLK",
                        ]
                        block_type = random.choice(uncommon_blocks)
                    else:
                        # Common blocks
                        block_type = random.choice(
                            block_types[:6]
                        )  # Regular colored blocks

                    block = self.create_block(x, y, block_type)
                    self.blocks.append(block)

        return self.blocks

    def update(self, delta_ms: float) -> None:
        """Update all blocks and remove those whose explosion animation is finished."""
        for block in self.blocks:
            block.update(delta_ms)
        # Remove blocks whose explosion animation is finished
        self.blocks = [b for b in self.blocks if b.state != "destroyed"]

    @functools.singledispatchmethod
    def check_collisions(self, obj) -> Tuple[int, int, List[Any]]:
        """Dispatch collision checking based on object type (Ball, Bullet, etc)."""
        raise NotImplementedError(f"Unsupported collision object type: {type(obj)}")

    @check_collisions.register(Ball)
    def _(self, ball) -> Tuple[int, int, List[Any]]:
        """Check for collisions between a ball and all blocks."""
        return self._check_block_collision(
            obj=ball,
            get_rect=ball.get_rect,
            get_position=ball.get_position,
            radius=ball.radius,
            is_bullet=False,
            remove_callback=None,
        )

    @check_collisions.register(Bullet)
    def _(self, bullet) -> Tuple[int, int, List[Any]]:
        """Check for collisions between a bullet and all blocks."""

        def remove_bullet():
            bullet.active = False  # Mark bullet as inactive (caller should remove)

        return self._check_block_collision(
            obj=bullet,
            get_rect=bullet.get_rect,
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
        return distance <= obj_radius

    def _reflect_ball(self, obj, obj_x: float, obj_y: float, block: Block) -> None:
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
        obj._update_rect()

    def _handle_block_hit(self, block: Block) -> Tuple[bool, int, Any]:
        """Handle the result of hitting a block."""
        self.logger.debug(f"Block hit: [{block}]")
        return block.hit()

    def _check_block_collision(
        self,
        obj,
        get_rect,
        get_position,
        radius,
        is_bullet: bool,
        remove_callback=None,
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
        return sum(1 for block in self.blocks if block.type != "BLACK_BLK")

    def remaining_blocks(self) -> int:
        """Return the number of blocks that are not broken."""
        count: int = len([b for b in self.blocks if not b.is_broken()])
        return count

    def get_block_by_id(self, block_id: int) -> Optional[Block]:
        """Return the Block with the given ID, or None if not found."""
        for block in self.blocks:
            if hasattr(block, "id") and block.id == block_id:  # type: ignore[attr-defined]  # Block.id is dynamic
                return block
        return None

    def create_block(self, x: int, y: int, block_type_key: str) -> Block:
        """Create a Block using the canonical key and config from block_types.json."""
        config = self.block_type_data.get(block_type_key)
        if config is None:
            raise ValueError(f"Unknown block type key {block_type_key}")
        if block_type_key == "COUNTER_BLK":
            return CounterBlock(x, y, config)
        return Block(x, y, config)
