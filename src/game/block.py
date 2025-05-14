"""
Block implementation for XBoing.

This module contains the block class and related utilities for
creating, rendering, and managing breakable blocks.
"""

import logging
import random

import pygame


class Block:
    """A breakable block in the game."""

    logger = logging.getLogger("xboing.Block")

    # Block types
    TYPE_NORMAL = 0
    TYPE_HARD = 1
    TYPE_UNBREAKABLE = 2
    TYPE_BONUS = 3
    TYPE_POWERUP = 4

    # Block colors
    COLORS = {
        "blue": (41, 173, 255),
        "red": (255, 59, 59),
        "green": (29, 219, 22),
        "yellow": (255, 255, 29),
        "purple": (173, 41, 214),
        "teal": (4, 217, 217),
        "white": (200, 200, 200),
        "gray": (150, 150, 150),
    }

    def __init__(
        self, x, y, width, height, block_type=TYPE_NORMAL, color_name="blue", points=100
    ):
        """
        Initialize a block.

        Args:
            x (int): X position
            y (int): Y position
            width (int): Block width
            height (int): Block height
            block_type (int): Type of block (normal, hard, unbreakable, etc.)
            color_name (str): Name of the color from the COLORS dictionary
            points (int): Points awarded for breaking this block
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = block_type
        self.color_name = color_name
        self.points = points

        # Get color from name
        if color_name in self.COLORS:
            self.color = self.COLORS[color_name]
        else:
            self.color = self.COLORS["blue"]  # Default

        # Create the collision rectangle
        self.rect = pygame.Rect(x, y, width, height)

        # Health depends on block type
        if block_type == self.TYPE_HARD:
            self.health = 2
        elif block_type == self.TYPE_UNBREAKABLE:
            self.health = -1  # Infinite
        else:
            self.health = 1

        # Animation state
        self.animation_frame = 0
        self.is_hit = False
        self.hit_timer = 0
        self.logger.info(
            f"Block created at ({x}, {y}) type={block_type} color={color_name}"
        )

    def update(self, delta_ms):
        """
        Update the block's state.

        Args:
            delta_ms (float): Time since last frame in milliseconds
        """
        # Update hit animation
        if self.is_hit:
            self.hit_timer -= delta_ms
            if self.hit_timer <= 0:
                self.is_hit = False

    def hit(self):
        """
        Handle the block being hit by a ball.

        Returns:
            tuple: (broken, points) - Whether the block was broken and points earned
        """
        # Can't hit unbreakable blocks
        if self.health < 0:
            return (False, 0)

        # Start hit animation
        self.is_hit = True
        self.hit_timer = 200  # ms

        # Reduce health
        self.health -= 1

        # Check if broken
        if self.health <= 0:
            self.logger.info(
                f"Block at ({self.x}, {self.y}) broken, points={self.points}"
            )
            return (True, self.points)

        return (False, 0)

    def draw(self, surface):
        """
        Draw the block.

        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Determine color based on hit state
        color = self.color
        if self.is_hit:
            # Brighten the color for hit animation
            r = min(255, int(color[0] * 1.5))
            g = min(255, int(color[1] * 1.5))
            b = min(255, int(color[2] * 1.5))
            color = (r, g, b)

        # Draw the main block
        pygame.draw.rect(surface, color, self.rect)

        # Draw a border
        border_color = (
            min(255, color[0] + 30),
            min(255, color[1] + 30),
            min(255, color[2] + 30),
        )
        pygame.draw.rect(surface, border_color, self.rect, 1)

        # For hard blocks, add an indicator
        if self.type == self.TYPE_HARD:
            # Draw an "X" pattern
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (self.rect.left + 5, self.rect.top + 5),
                (self.rect.right - 5, self.rect.bottom - 5),
                2,
            )
            pygame.draw.line(
                surface,
                (255, 255, 255),
                (self.rect.right - 5, self.rect.top + 5),
                (self.rect.left + 5, self.rect.bottom - 5),
                2,
            )

        # For unbreakable blocks, add a different indicator
        elif self.type == self.TYPE_UNBREAKABLE:
            # Draw horizontal lines
            for y_offset in range(5, self.height - 5, 4):
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (self.rect.left + 5, self.rect.top + y_offset),
                    (self.rect.right - 5, self.rect.top + y_offset),
                    1,
                )

        # For bonus blocks, add a special indicator
        elif self.type == self.TYPE_BONUS:
            # Draw a star-like shape
            center_x = self.rect.centerx
            center_y = self.rect.centery

            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), 5, 1)
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), 8, 1)

        # For powerup blocks, add a different indicator
        elif self.type == self.TYPE_POWERUP:
            # Draw a question mark
            font = pygame.font.Font(None, self.height - 4)
            text = font.render("?", True, (255, 255, 255))
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)

    def get_rect(self):
        """Get the block's collision rectangle."""
        return self.rect

    def is_broken(self):
        """Check if the block is broken."""
        return self.health == 0


class BlockManager:
    """Manages all blocks in the game."""

    def __init__(
        self, brick_width=50, brick_height=20, margin=2, offset_x=0, offset_y=0
    ):
        """
        Initialize the block manager.

        Args:
            brick_width (int): Width of each brick
            brick_height (int): Height of each brick
            margin (int): Margin between bricks
            offset_x (int): X offset for all blocks (for positioning within play area)
            offset_y (int): Y offset for all blocks (for positioning within play area)
        """
        self.brick_width = brick_width
        self.brick_height = brick_height
        self.margin = margin
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.blocks = []

    def create_level(self, level_num=1, width=800, top_margin=100):
        """
        Create a level with blocks arranged in a pattern.

        Args:
            level_num (int): Level number to determine difficulty
            width (int): Width of the play area
            top_margin (int): Top margin for blocks

        Returns:
            list: The created blocks
        """
        self.blocks = []

        # Calculate how many blocks can fit horizontally
        blocks_per_row = (width - self.margin) // (self.brick_width + self.margin)

        # Adjust for level difficulty
        rows = min(12, 3 + level_num)

        # Create a pattern based on level number
        if level_num == 1:
            # Basic rows
            for row in range(rows):
                for col in range(blocks_per_row):
                    x = (
                        self.offset_x
                        + self.margin
                        + col * (self.brick_width + self.margin)
                    )
                    y = (
                        self.offset_y
                        + top_margin
                        + row * (self.brick_height + self.margin)
                    )

                    # Alternate colors
                    colors = ["blue", "red", "green", "yellow"]
                    color = colors[row % len(colors)]

                    block = Block(
                        x,
                        y,
                        self.brick_width,
                        self.brick_height,
                        Block.TYPE_NORMAL,
                        color,
                    )
                    self.blocks.append(block)

        elif level_num == 2:
            # Checkerboard pattern
            for row in range(rows):
                for col in range(blocks_per_row):
                    if (row + col) % 2 == 0:  # Checkerboard pattern
                        x = (
                            self.offset_x
                            + self.margin
                            + col * (self.brick_width + self.margin)
                        )
                        y = (
                            self.offset_y
                            + top_margin
                            + row * (self.brick_height + self.margin)
                        )

                        color = "purple" if row % 3 == 0 else "teal"

                        block = Block(
                            x,
                            y,
                            self.brick_width,
                            self.brick_height,
                            Block.TYPE_NORMAL,
                            color,
                        )
                        self.blocks.append(block)

        elif level_num == 3:
            # Mixed types
            for row in range(rows):
                for col in range(blocks_per_row):
                    x = (
                        self.offset_x
                        + self.margin
                        + col * (self.brick_width + self.margin)
                    )
                    y = (
                        self.offset_y
                        + top_margin
                        + row * (self.brick_height + self.margin)
                    )

                    # Determine block type
                    block_type = Block.TYPE_NORMAL
                    if row == 0:
                        block_type = Block.TYPE_UNBREAKABLE
                    elif row < 3 and col % 3 == 0:
                        block_type = Block.TYPE_HARD
                    elif row > 5 and col % 5 == 0:
                        block_type = Block.TYPE_BONUS

                    # Choose color based on type
                    if block_type == Block.TYPE_UNBREAKABLE:
                        color = "gray"
                    elif block_type == Block.TYPE_HARD:
                        color = "red"
                    elif block_type == Block.TYPE_BONUS:
                        color = "yellow"
                    else:
                        colors = ["blue", "green", "purple", "teal"]
                        color = colors[(row + col) % len(colors)]

                    block = Block(
                        x, y, self.brick_width, self.brick_height, block_type, color
                    )
                    self.blocks.append(block)
        else:
            # Random pattern for higher levels
            for row in range(rows):
                for col in range(blocks_per_row):
                    # Skip some blocks randomly
                    if random.random() < 0.2:
                        continue

                    x = (
                        self.offset_x
                        + self.margin
                        + col * (self.brick_width + self.margin)
                    )
                    y = (
                        self.offset_y
                        + top_margin
                        + row * (self.brick_height + self.margin)
                    )

                    # Randomize block types
                    r = random.random()
                    if r < 0.05:
                        block_type = Block.TYPE_UNBREAKABLE
                        color = "gray"
                    elif r < 0.2:
                        block_type = Block.TYPE_HARD
                        color = "red"
                    elif r < 0.3:
                        block_type = Block.TYPE_BONUS
                        color = "yellow"
                    elif r < 0.35:
                        block_type = Block.TYPE_POWERUP
                        color = "purple"
                    else:
                        block_type = Block.TYPE_NORMAL
                        colors = ["blue", "green", "teal"]
                        color = colors[random.randint(0, len(colors) - 1)]

                    # Points increase with row depth
                    points = 100 + row * 10

                    block = Block(
                        x,
                        y,
                        self.brick_width,
                        self.brick_height,
                        block_type,
                        color,
                        points,
                    )
                    self.blocks.append(block)

        return self.blocks

    def update(self, delta_ms):
        """
        Update all blocks.

        Args:
            delta_ms (float): Time since last frame in milliseconds
        """
        for block in self.blocks:
            block.update(delta_ms)

    def check_collisions(self, ball):
        """
        Check for collisions between a ball and all blocks.

        Args:
            ball (Ball): The ball to check collisions with

        Returns:
            tuple: (points, broken_blocks) - Points earned and number of blocks broken
        """
        points = 0
        broken_blocks = 0

        # Get ball position and previous position
        ball_rect = ball.get_rect()
        ball_x, ball_y = ball.get_position()
        ball_radius = ball.radius

        # Check each block
        for _, block in enumerate(self.blocks[:]):
            # Check collision with the block
            if block.rect.colliderect(ball_rect):
                # Calculate collision normal using the block's edges
                # Determine which side of the block was hit

                # Find closest point on rectangle to circle center
                closest_x = max(block.rect.left, min(ball_x, block.rect.right))
                closest_y = max(block.rect.top, min(ball_y, block.rect.bottom))

                # Calculate distance from closest point to circle center
                dx = ball_x - closest_x
                dy = ball_y - closest_y
                distance = (dx * dx + dy * dy) ** 0.5

                # If distance is less than or equal to radius, collision occurred
                if distance <= ball_radius:
                    # Determine normal vector (normalize the closest point vector)
                    if distance > 0:
                        nx = dx / distance
                        ny = dy / distance
                    else:
                        # If ball is exactly at the closest point, use a default normal
                        nx, ny = 0, -1

                    # Handle ball bounce
                    # Calculate dot product of velocity and normal
                    dot = ball.vx * nx + ball.vy * ny

                    # Reflect velocity
                    ball.vx -= 2 * dot * nx
                    ball.vy -= 2 * dot * ny

                    # Move ball out of collision
                    overlap = ball_radius - distance
                    ball.x += nx * overlap
                    ball.y += ny * overlap

                    # Update ball rectangle
                    ball._update_rect()

                    # Hit the block
                    broken, block_points = block.hit()
                    if broken:
                        points += block_points
                        broken_blocks += 1
                        self.blocks.remove(block)

                    # Only handle one collision per update to prevent double hits
                    break

        return points, broken_blocks

    def draw(self, surface):
        """
        Draw all blocks.

        Args:
            surface (pygame.Surface): Surface to draw on
        """
        for block in self.blocks:
            block.draw(surface)

    def get_block_count(self):
        """Get the number of remaining blocks."""
        return len(self.blocks)

    def get_breakable_count(self):
        """Get the number of breakable blocks (excluding unbreakable ones)."""
        return sum(1 for block in self.blocks if block.type != Block.TYPE_UNBREAKABLE)
