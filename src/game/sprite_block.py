"""
Sprite-based Block implementation for XBoing.

This module implements blocks using the original XBoing styling,
with proper rounded edges and spacing matching the original game.
"""

import os
import random

import pygame
from utils.asset_paths import get_blocks_dir


class SpriteBlock:
    """A sprite-based breakable block in the game."""

    # Block types (matching original XBoing)
    TYPE_RED = 0
    TYPE_BLUE = 1
    TYPE_GREEN = 2
    TYPE_TAN = 3
    TYPE_YELLOW = 4
    TYPE_PURPLE = 5
    TYPE_BULLET = 6
    TYPE_BLACK = 7
    TYPE_COUNTER = 8
    TYPE_BOMB = 9
    TYPE_DEATH = 10
    TYPE_REVERSE = 11
    TYPE_HYPERSPACE = 12
    TYPE_EXTRABALL = 13
    TYPE_MGUN = 14
    TYPE_WALLOFF = 15
    TYPE_MULTIBALL = 16
    TYPE_STICKY = 17
    TYPE_PAD_SHRINK = 18
    TYPE_PAD_EXPAND = 19
    TYPE_DROP = 20
    TYPE_MAXAMMO = 21
    TYPE_ROAMER = 22
    TYPE_TIMER = 23
    TYPE_RANDOM = 24
    TYPE_DYNAMITE = 25
    TYPE_BONUSX2 = 26
    TYPE_BONUSX4 = 27
    TYPE_BONUS = 28
    TYPE_BLACKHIT = 29

    # Block behaviors - subclasses could implement these
    BEHAVIOR_NORMAL = 0  # Regular breakable block
    BEHAVIOR_UNBREAKABLE = 1  # Black wall blocks
    BEHAVIOR_COUNTER = 2  # Blocks that require multiple hits
    BEHAVIOR_SPECIAL = 3  # Special effect when broken (power-ups)
    BEHAVIOR_DAMAGE = 4  # Harmful to the player (death blocks)
    BEHAVIOR_DYNAMIC = 5  # Blocks that move or change (roamer)

    # Maps block types to image filenames, point values, and behaviors
    BLOCK_IMAGES = {
        TYPE_RED: ("redblk.png", 100, BEHAVIOR_NORMAL),
        TYPE_BLUE: ("blueblk.png", 100, BEHAVIOR_NORMAL),
        TYPE_GREEN: ("grnblk.png", 100, BEHAVIOR_NORMAL),
        TYPE_TAN: ("tanblk.png", 100, BEHAVIOR_NORMAL),
        TYPE_YELLOW: ("yellblk.png", 100, BEHAVIOR_NORMAL),
        TYPE_PURPLE: ("purpblk.png", 100, BEHAVIOR_NORMAL),
        TYPE_BULLET: ("bonus1.png", 200, BEHAVIOR_SPECIAL),  # Gives bullet ammo
        TYPE_BLACK: ("blakblk.png", 200, BEHAVIOR_UNBREAKABLE),
        TYPE_COUNTER: ("cntblk.png", 300, BEHAVIOR_COUNTER),
        TYPE_BOMB: ("bombblk.png", 500, BEHAVIOR_SPECIAL),
        TYPE_DEATH: ("death1.png", 0, BEHAVIOR_DAMAGE),
        TYPE_REVERSE: ("reverse.png", 300, BEHAVIOR_SPECIAL),
        TYPE_HYPERSPACE: ("hypspc.png", 200, BEHAVIOR_SPECIAL),
        TYPE_EXTRABALL: ("xtrabal.png", 1000, BEHAVIOR_SPECIAL),
        TYPE_MGUN: ("machgun.png", 500, BEHAVIOR_SPECIAL),
        TYPE_WALLOFF: ("walloff.png", 500, BEHAVIOR_SPECIAL),
        TYPE_MULTIBALL: ("multibal.png", 1000, BEHAVIOR_SPECIAL),
        TYPE_STICKY: ("stkyblk.png", 300, BEHAVIOR_SPECIAL),
        TYPE_PAD_SHRINK: ("padshrk.png", 0, BEHAVIOR_SPECIAL),
        TYPE_PAD_EXPAND: ("padexpn.png", 300, BEHAVIOR_SPECIAL),
        TYPE_DROP: ("bonus2.png", 200, BEHAVIOR_SPECIAL),
        TYPE_MAXAMMO: ("lotsammo.png", 500, BEHAVIOR_SPECIAL),
        TYPE_ROAMER: ("roamer.png", 800, BEHAVIOR_DYNAMIC),
        TYPE_TIMER: ("clock.png", 300, BEHAVIOR_SPECIAL),
        TYPE_RANDOM: ("bonus3.png", 200, BEHAVIOR_SPECIAL),
        TYPE_DYNAMITE: ("dynamite.png", 1000, BEHAVIOR_SPECIAL),
        TYPE_BONUSX2: ("x2bonus1.png", 500, BEHAVIOR_SPECIAL),
        TYPE_BONUSX4: ("x4bonus1.png", 1000, BEHAVIOR_SPECIAL),
        TYPE_BONUS: ("bonus1.png", 200, BEHAVIOR_SPECIAL),
        TYPE_BLACKHIT: ("blakblkH.png", 250, BEHAVIOR_NORMAL),
    }

    # Animation frames for special blocks
    ANIMATION_FRAMES = {
        TYPE_COUNTER: [
            "cntblk.png",
            "cntblk1.png",
            "cntblk2.png",
            "cntblk3.png",
            "cntblk4.png",
            "cntblk5.png",
        ],
        TYPE_DEATH: [
            "death1.png",
            "death2.png",
            "death3.png",
            "death4.png",
            "death5.png",
        ],
        TYPE_BONUSX2: ["x2bonus1.png", "x2bonus2.png", "x2bonus3.png", "x2bonus4.png"],
        TYPE_BONUSX4: ["x4bonus1.png", "x4bonus2.png", "x4bonus3.png", "x4bonus4.png"],
        TYPE_BONUS: ["bonus1.png", "bonus2.png", "bonus3.png", "bonus4.png"],
        TYPE_ROAMER: {
            "idle": "roamer.png",
            "up": "roamerU.png",
            "down": "roamerD.png",
            "left": "roamerL.png",
            "right": "roamerR.png",
        },
    }

    # Cache for loaded block images
    _image_cache = {}

    # Define vibrant XBoing-style colors for blocks with 3D effect
    XBOING_COLORS = {
        TYPE_RED: [(255, 40, 40), (220, 20, 20), (180, 0, 0)],  # Main, dark, shadow
        TYPE_BLUE: [(40, 120, 255), (20, 80, 220), (0, 40, 180)],
        TYPE_GREEN: [
            (60, 240, 60),
            (30, 200, 30),
            (30, 150, 30),
        ],  # Brighter green with visible shadow
        TYPE_YELLOW: [(255, 255, 40), (220, 220, 20), (180, 180, 0)],
        TYPE_PURPLE: [(200, 40, 240), (160, 20, 200), (120, 0, 160)],
        TYPE_TAN: [(220, 180, 140), (180, 140, 100), (140, 100, 60)],
    }

    @classmethod
    def preload_images(cls, blocks_dir):
        """
        Preload all block images to avoid loading during gameplay.

        Args:
            blocks_dir (str): Directory containing block images
        """
        loaded_count = 0
        failed_count = 0

        print(f"\nLoading block images from {blocks_dir}")

        # Load regular block images
        for _, block_info in cls.BLOCK_IMAGES.items():
            # Unpack the image file from block info (now a 3-tuple)
            image_file = block_info[0]

            image_path = os.path.join(blocks_dir, image_file)
            if os.path.exists(image_path):
                try:
                    # Load the image
                    img = pygame.image.load(image_path).convert_alpha()

                    # Store in cache
                    cls._image_cache[image_file] = img
                    loaded_count += 1

                except Exception as e:
                    print(f"Failed to load block image {image_file}: {e}")
                    failed_count += 1
            else:
                print(f"Block image not found: {image_path}")
                failed_count += 1

        # Load animation frames
        for _, frames in cls.ANIMATION_FRAMES.items():
            if isinstance(frames, list):
                for frame in frames:
                    image_path = os.path.join(blocks_dir, frame)
                    if os.path.exists(image_path) and frame not in cls._image_cache:
                        try:
                            cls._image_cache[frame] = pygame.image.load(
                                image_path
                            ).convert_alpha()
                            loaded_count += 1
                        except Exception as e:
                            print(f"Failed to load animation frame {frame}: {e}")
                            failed_count += 1
            elif isinstance(frames, dict):
                for _, frame in frames.items():
                    image_path = os.path.join(blocks_dir, frame)
                    if os.path.exists(image_path) and frame not in cls._image_cache:
                        try:
                            cls._image_cache[frame] = pygame.image.load(
                                image_path
                            ).convert_alpha()
                            loaded_count += 1
                        except Exception as e:
                            print(f"Failed to load animation frame {frame}: {e}")
                            failed_count += 1

        print(
            f"Block image loading complete: {loaded_count} loaded, {failed_count} failed"
        )

    def __init__(self, x, y, block_type=TYPE_BLUE):
        """
        Initialize a sprite-based block.

        Args:
            x (int): X position
            y (int): Y position
            block_type (int): Type of block (from TYPE_* constants)
        """
        self.x = x
        self.y = y
        self.type = block_type

        # Original XBoing block dimensions
        self.width = 40
        self.height = 20

        # Create the collision rectangle
        self.rect = pygame.Rect(x, y, self.width, self.height)

        # Get image file, points, and behavior from mapping
        if block_type in self.BLOCK_IMAGES:
            self.image_file, self.points, self.behavior = self.BLOCK_IMAGES[block_type]
        else:
            # Default to blue block
            self.image_file, self.points, self.behavior = self.BLOCK_IMAGES[
                self.TYPE_BLUE
            ]

        # Block state - set initial health based on behavior
        if self.behavior == self.BEHAVIOR_COUNTER:
            self.health = 6  # Counter blocks take multiple hits
            self.counter_value = 5  # Default to 5 count for regular counter blocks
        elif self.behavior == self.BEHAVIOR_UNBREAKABLE:
            self.health = float("inf")  # Unbreakable blocks can't be destroyed
        else:
            self.health = 1  # Normal blocks take 1 hit

        self.is_hit = False
        self.hit_timer = 0

        # Animation state for special blocks
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 200  # ms per frame
        self.animation_frames = None

        # For special blocks, set up animation frames
        if block_type in self.ANIMATION_FRAMES:
            self.animation_frames = self.ANIMATION_FRAMES[block_type]

            # For counter blocks, initialize with appropriate frame based on counter_value
            if block_type == self.TYPE_COUNTER and hasattr(self, "counter_value"):
                if self.counter_value == 0 and len(self.animation_frames) > 0:
                    # Use the base counter block image (without a number)
                    if self.animation_frames[0] in self._image_cache:
                        self.image = self._image_cache[self.animation_frames[0]]
                    # Disable animation for these blocks
                    self.animation_frames = None

        # For roamer blocks which move
        self.direction = None
        self.move_timer = 0
        self.move_interval = 1000  # ms between movements
        if self.behavior == self.BEHAVIOR_DYNAMIC:
            self.direction = "idle"

        # Use the loaded PNG image for this block type
        if self.image_file in self._image_cache:
            self.image = self._image_cache[self.image_file]
        else:
            # If image is not available, log error and use a placeholder
            print(
                f"Error: Missing block image '{self.image_file}' for block type {block_type}"
            )
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(
                self.image, (255, 0, 255), pygame.Rect(0, 0, self.width, self.height)
            )

    def _create_block_image(self, block_type):
        """
        Create a proper XBoing-style block image with 3D effects and rounded corners.

        Args:
            block_type (int): Type of block to create

        Returns:
            pygame.Surface: The block image surface
        """
        # Create a surface for the block
        img = pygame.Surface((40, 20), pygame.SRCALPHA)

        # Get appropriate colors based on block type
        if block_type in self.XBOING_COLORS:
            main_color, edge_color, shadow_color = self.XBOING_COLORS[block_type]
        else:
            # Default colors for block types not explicitly mapped
            if block_type == self.TYPE_BLACK:
                main_color = (40, 40, 40)
                edge_color = (20, 20, 20)
                shadow_color = (0, 0, 0)
            elif block_type == self.TYPE_BULLET:
                main_color = (220, 100, 100)
                edge_color = (180, 60, 60)
                shadow_color = (140, 20, 20)
            elif block_type >= self.TYPE_BONUSX2:
                main_color = (255, 215, 0)  # Gold for bonus blocks
                edge_color = (220, 180, 0)
                shadow_color = (180, 140, 0)
            else:
                # Default to blue
                main_color = (40, 120, 255)  # Vibrant blue
                edge_color = (20, 80, 220)  # Medium blue
                shadow_color = (0, 40, 180)  # Dark blue

        # Calculate highlight color
        highlight_color = (
            min(255, main_color[0] + 50),
            min(255, main_color[1] + 50),
            min(255, main_color[2] + 50),
        )

        # Draw main block with full color
        pygame.draw.rect(img, main_color, pygame.Rect(0, 0, 40, 20))

        # Draw rounded corners (transparent)
        for corner in [(0, 0), (39, 0), (0, 19), (39, 19)]:
            pygame.draw.circle(img, (0, 0, 0, 0), corner, 3)

        # Draw 3D effect - light edge on top and left
        pygame.draw.line(img, highlight_color, (3, 0), (36, 0), 2)  # Top
        pygame.draw.line(img, highlight_color, (0, 3), (0, 16), 2)  # Left

        # Draw 3D effect - dark edge on bottom and right
        pygame.draw.line(img, edge_color, (4, 19), (35, 19), 2)  # Bottom
        pygame.draw.line(img, edge_color, (39, 4), (39, 15), 2)  # Right

        # Draw shadow effect in corners
        pygame.draw.circle(img, shadow_color, (37, 17), 2)  # Bottom-right
        pygame.draw.circle(img, highlight_color, (3, 3), 2)  # Top-left

        # Special styling for specific block types
        if block_type == self.TYPE_BOMB:
            # Draw bomb icon
            pygame.draw.circle(img, (0, 0, 0), (20, 10), 6)
            pygame.draw.line(img, (255, 255, 0), (23, 5), (26, 2), 2)  # Fuse
        elif block_type == self.TYPE_MULTIBALL:
            # Draw multiball symbol (circles)
            for pos in [(14, 10), (20, 10), (26, 10)]:
                pygame.draw.circle(img, (255, 255, 255), pos, 3)
                pygame.draw.circle(img, (0, 0, 0), pos, 3, 1)
        elif block_type in [self.TYPE_BONUSX2, self.TYPE_BONUSX4]:
            # Draw bonus multiplier text
            text = "x2" if block_type == self.TYPE_BONUSX2 else "x4"
            font = pygame.font.SysFont("Arial", 12, bold=True)
            text_surf = font.render(text, True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=(20, 10))
            img.blit(text_surf, text_rect)

        return img

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

        # Update animations for special blocks
        if self.animation_frames and isinstance(self.animation_frames, list) and not (
            self.type == self.TYPE_COUNTER
            and hasattr(self, "counter_value")
            and self.counter_value == 0
        ):
            # Skip animation updates for counter blocks with counter_value=0
            self.animation_timer += delta_ms
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % len(
                    self.animation_frames
                )
                # Update the image to the current animation frame
                frame_file = self.animation_frames[self.animation_frame]
                if frame_file in self._image_cache:
                    self.image = self._image_cache[frame_file]

        # Update roamer movement
        if self.type == self.TYPE_ROAMER and self.direction:
            self.move_timer += delta_ms
            if self.move_timer >= self.move_interval:
                self.move_timer = 0
                # Change direction randomly
                self.set_random_direction()

    def set_random_direction(self):
        """Set a random direction for roamer blocks."""
        directions = ["idle", "up", "down", "left", "right"]
        self.direction = random.choice(directions)
        # Update the image based on direction
        if self.type == self.TYPE_ROAMER:
            frames = self.ANIMATION_FRAMES[self.TYPE_ROAMER]
            frame_file = frames[self.direction]
            if frame_file in self._image_cache:
                self.image = self._image_cache[frame_file]

    def hit(self):
        """
        Handle the block being hit by a ball.

        Returns:
            tuple: (broken, points, effect) - Whether the block was broken, points earned, and any special effect
        """
        # Start hit animation (except for unbreakable blocks)
        if self.behavior != self.BEHAVIOR_UNBREAKABLE:
            self.is_hit = True
            self.hit_timer = 200  # ms

        # Different behavior based on block type
        if self.behavior == self.BEHAVIOR_UNBREAKABLE:
            # Unbreakable blocks (black wall) - ball just bounces off
            return (False, 0, None)

        elif self.behavior == self.BEHAVIOR_COUNTER:
            # Counter blocks - takes multiple hits
            self.health -= 1

            # Handle the special case for counter blocks with counter_value of 0
            # In the original C code, these don't show a counter and break in one hit
            if hasattr(self, "counter_value") and self.counter_value == 0:
                # '0' counter blocks break in one hit and don't show a counter
                if self.health <= 0:
                    return (True, self.points, None)
                return (False, 0, None)

            # Normal counter blocks - update the counter image to show how many hits left
            if self.health > 0 and self.animation_frames:
                # Use the correct frame for the current health
                frame_index = max(
                    0, min(5 - self.health, len(self.animation_frames) - 1)
                )
                if self.image_file in self._image_cache:
                    self.image = self._image_cache[self.animation_frames[frame_index]]

            # Check if broken
            if self.health <= 0:
                return (True, self.points, None)

            return (False, 0, None)

        elif self.behavior == self.BEHAVIOR_SPECIAL:
            # Special blocks have effects when broken
            self.health -= 1

            # Special effects only happen when the block is broken
            if self.health <= 0:
                # Return the block type as the effect
                return (True, self.points, self.type)

            return (False, 0, None)

        elif self.behavior == self.BEHAVIOR_DAMAGE:
            # Damage blocks hurt the player (e.g., death blocks)
            self.health -= 1

            if self.health <= 0:
                # Death blocks cause the ball to be lost
                return (True, 0, "death")

            return (False, 0, None)

        elif self.behavior == self.BEHAVIOR_DYNAMIC:
            # Dynamic blocks like roamers - special handling
            self.health -= 1

            if self.health <= 0:
                return (True, self.points, self.type)

            return (False, 0, None)

        else:
            # Normal blocks (regular colored blocks)
            self.health -= 1

            if self.health <= 0:
                return (True, self.points, None)

            return (False, 0, None)

    def draw(self, surface):
        """
        Draw the block.

        Args:
            surface (pygame.Surface): Surface to draw on
        """
        # Apply hit effect (flash)
        if self.is_hit:
            # Create a temporary copy of the image and brighten it
            bright_image = self.image.copy()
            bright_mask = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            bright_mask.fill((100, 100, 100, 0))  # Semi-transparent white
            bright_image.blit(bright_mask, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
            surface.blit(bright_image, (self.x, self.y))
        else:
            # Draw normal image
            surface.blit(self.image, (self.x, self.y))

    def get_rect(self):
        """Get the block's collision rectangle."""
        return self.rect

    def is_broken(self):
        """Check if the block is broken."""
        return self.health <= 0


class SpriteBlockManager:
    """Manages sprite-based blocks in the game."""

    def __init__(self, offset_x=0, offset_y=0):
        """
        Initialize the sprite block manager.

        Args:
            offset_x (int): X offset for all blocks (for positioning within play area)
            offset_y (int): Y offset for all blocks (for positioning within play area)
        """
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
        self.blocks = []

        # Get blocks directory using asset path utility
        blocks_dir = get_blocks_dir()
        print(f"Using block images from {blocks_dir}")

        # Preload all block images for better performance
        SpriteBlock.preload_images(blocks_dir)

    def create_level(self, level_num=1, width=495, top_margin=60):
        """
        Create a level with blocks arranged in a pattern based on the original XBoing.

        Args:
            level_num (int): Level number to determine difficulty
            width (int): Width of the play area
            top_margin (int): Top margin for blocks

        Returns:
            list: The created blocks
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
                SpriteBlock.TYPE_RED,
                SpriteBlock.TYPE_BLUE,
                SpriteBlock.TYPE_GREEN,
                SpriteBlock.TYPE_YELLOW,
                SpriteBlock.TYPE_PURPLE,
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
                    block = SpriteBlock(x, y, block_type)
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
                            block_type = SpriteBlock.TYPE_PURPLE
                        elif row % 3 == 1:
                            block_type = SpriteBlock.TYPE_GREEN
                        else:
                            block_type = SpriteBlock.TYPE_TAN

                        block = SpriteBlock(x, y, block_type)
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
                        block_type = SpriteBlock.TYPE_BLACK  # Unbreakable top row
                    elif row == 1 and col % 3 == 0:
                        block_type = SpriteBlock.TYPE_BOMB  # Bombs in second row
                    elif row == 2 and col % 4 == 0:
                        block_type = SpriteBlock.TYPE_EXTRABALL  # Extra balls
                    elif row == 3 and col % 2 == 0:
                        block_type = SpriteBlock.TYPE_BONUS  # Bonus blocks
                    elif row > 5 and col % 5 == 0:
                        block_type = SpriteBlock.TYPE_MULTIBALL  # Multiball blocks
                    else:
                        # Regular color blocks
                        colors = [
                            SpriteBlock.TYPE_RED,
                            SpriteBlock.TYPE_BLUE,
                            SpriteBlock.TYPE_GREEN,
                            SpriteBlock.TYPE_TAN,
                            SpriteBlock.TYPE_YELLOW,
                        ]
                        block_type = colors[(row + col) % len(colors)]

                    block = SpriteBlock(x, y, block_type)
                    self.blocks.append(block)

        else:
            # Higher levels - mix of all block types with some gaps
            block_types = [
                SpriteBlock.TYPE_RED,
                SpriteBlock.TYPE_BLUE,
                SpriteBlock.TYPE_GREEN,
                SpriteBlock.TYPE_TAN,
                SpriteBlock.TYPE_YELLOW,
                SpriteBlock.TYPE_PURPLE,
                SpriteBlock.TYPE_BOMB,
                SpriteBlock.TYPE_EXTRABALL,
                SpriteBlock.TYPE_MULTIBALL,
                SpriteBlock.TYPE_STICKY,
                SpriteBlock.TYPE_REVERSE,
                SpriteBlock.TYPE_BONUS,
                SpriteBlock.TYPE_BONUSX2,
                SpriteBlock.TYPE_TIMER,
                SpriteBlock.TYPE_MGUN,
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
                        block_type = (
                            SpriteBlock.TYPE_BLACK
                        )  # Some unbreakable blocks in top row
                    elif r < 0.05:
                        # Rare blocks
                        rare_blocks = [
                            SpriteBlock.TYPE_ROAMER,
                            SpriteBlock.TYPE_BONUSX4,
                            SpriteBlock.TYPE_WALLOFF,
                        ]
                        block_type = random.choice(rare_blocks)
                    elif r < 0.15:
                        # Uncommon blocks
                        uncommon_blocks = [
                            SpriteBlock.TYPE_BOMB,
                            SpriteBlock.TYPE_EXTRABALL,
                            SpriteBlock.TYPE_MULTIBALL,
                            SpriteBlock.TYPE_BONUSX2,
                        ]
                        block_type = random.choice(uncommon_blocks)
                    else:
                        # Common blocks
                        block_type = random.choice(
                            block_types[:6]
                        )  # Regular colored blocks

                    block = SpriteBlock(x, y, block_type)
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
            tuple: (points, broken_blocks, effects) - Points earned, number of blocks broken, and any special effects
        """
        points = 0
        broken_blocks = 0
        effects = []

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
                    broken, block_points, effect = block.hit()

                    # Handle the hit result
                    if broken:
                        points += block_points
                        broken_blocks += 1
                        self.blocks.remove(block)

                        # If there was a special effect, add it to the effects list
                        if effect is not None:
                            effects.append(effect)

                    # Handle special death blocks
                    if effect == "death":
                        # Death blocks cause ball loss
                        ball.active = False

                    # Only handle one collision per update to prevent double hits
                    break

        return points, broken_blocks, effects

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
        return sum(1 for block in self.blocks if block.type != SpriteBlock.TYPE_BLACK)
