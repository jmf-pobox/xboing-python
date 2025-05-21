"""Ball implementation for XBoing.

This module contains the ball class that handles physics, movement,
and collision detection with walls and the paddle.
"""

import logging
import math
import os
import random
from typing import Any, ClassVar, List, Optional, Tuple

import pygame

from xboing.utils.asset_paths import get_balls_dir

logger = logging.getLogger(__name__)


class Ball:
    """A bouncing ball with physics and collision detection."""

    # Class variables for sprites
    sprites: ClassVar[List[pygame.Surface]] = []
    animation_frames: ClassVar[List[pygame.Surface]] = []
    logger: ClassVar[logging.Logger] = logging.getLogger("xboing.Ball")

    @classmethod
    def load_sprites(cls) -> None:
        """Load the ball sprites once for all balls."""
        if not cls.sprites:
            cls.sprites = []
            cls.animation_frames = []
            assets_dir = get_balls_dir()

            # Load the four main ball sprites
            for i in range(1, 5):
                sprite_path = os.path.join(assets_dir, f"ball{i}.png")
                try:
                    img = pygame.image.load(sprite_path).convert_alpha()
                    cls.sprites.append(img)
                except (pygame.error, FileNotFoundError) as e:
                    cls.logger.warning(f"Failed to load ball sprite {i}: {e}")
                    # Create a fallback sprite if loading fails
                    fallback = pygame.Surface((20, 20), pygame.SRCALPHA)
                    pygame.draw.circle(fallback, (255, 255, 255), (10, 10), 10)
                    cls.sprites.append(fallback)

            # Load the ball birth animation frames
            for i in range(1, 9):
                anim_path = os.path.join(assets_dir, f"bbirth{i}.png")
                try:
                    img = pygame.image.load(anim_path).convert_alpha()
                    cls.animation_frames.append(img)
                except (pygame.error, FileNotFoundError) as e:
                    cls.logger.warning(f"Failed to load ball animation frame {i}: {e}")

    def __init__(
        self,
        x: float,
        y: float,
        radius: int = 8,
        color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        """Initialize a new ball.

        Args:
        ----
            x (float): Starting X position
            y (float): Starting Y position
            radius (int): Ball radius
            color (tuple): RGB color tuple

        """
        self.x: float = float(x)
        self.y: float = float(y)
        self.radius: int = radius
        self.color: Tuple[int, int, int] = color

        # Initial velocity
        angle = random.uniform(math.pi / 4, 3 * math.pi / 4)  # Start with upward angle
        speed = 5.0
        self.vx: float = speed * math.cos(angle)
        self.vy: float = -speed * math.sin(
            angle
        )  # Negative because Y increases downward

        # State
        self.active: bool = True
        self.stuck_to_paddle: bool = False
        self.paddle_offset: float = 0.0

        # Animation state
        self.animation_frame: int = 0
        self.frame_counter: int = 0
        self.birth_animation: bool = False
        # Main ball animation state
        self.anim_frame: int = 0
        self.anim_counter: float = 0.0
        self.anim_frame_ms = 100  # Animation frame duration in ms (was ANIM_FRAME_MS)

        # Ensure sprites are loaded
        if not Ball.sprites:
            Ball.load_sprites()

        # Create the collision rect
        self.rect: pygame.Rect = pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def update(
        self,
        delta_ms: float,
        screen_width: int,
        screen_height: int,
        paddle: Optional[Any] = None,
        offset_x: int = 0,
        offset_y: int = 0,
    ) -> Tuple[bool, bool, bool]:
        """Update ball position and handle collisions.

        Args:
        ----
            delta_ms (float): Time since last frame in milliseconds
            screen_width (int): Play area width for boundary collision
            screen_height (int): Play area height for boundary collision
            paddle (Paddle): Paddle object for collision detection
            offset_x (int): X offset of the play area
            offset_y (int): Y offset of the play area

        Returns:
        -------
            tuple: (is_active, hit_paddle, hit_wall) - ball status and collision info

        """
        # Animate main ball (not during birth animation)
        if (
            not self.birth_animation
            and Ball.sprites is not None
            and len(Ball.sprites) > 1
        ):
            self.anim_counter += delta_ms
            if self.anim_counter >= self.anim_frame_ms:
                self.anim_counter -= self.anim_frame_ms
                self.anim_frame = (self.anim_frame + 1) % len(Ball.sprites)

        if not self.active:
            return (False, False, False)

        if self.stuck_to_paddle and paddle:
            self.x = paddle.rect.centerx + self.paddle_offset
            self.y = paddle.rect.top - self.radius - 1
            self.update_rect()
            return (True, False, False)

        # Calculate movement with framerate independence
        move_factor = delta_ms / 16.67  # Normalized for 60 FPS

        # Update position
        self.x += self.vx * move_factor
        self.y += self.vy * move_factor

        # Handle wall collisions
        changed = False
        hit_wall = False

        # Define the play area boundaries with offsets
        left_boundary = offset_x
        right_boundary = offset_x + screen_width
        top_boundary = offset_y
        bottom_boundary = offset_y + screen_height

        # Left and right walls
        if self.x - self.radius < left_boundary:
            self.x = left_boundary + self.radius
            self.vx = abs(self.vx)  # Ensure positive (right) direction
            changed = True
            hit_wall = True  # Hit left wall
        elif self.x + self.radius > right_boundary:
            self.x = right_boundary - self.radius
            self.vx = -abs(self.vx)  # Ensure negative (left) direction
            changed = True
            hit_wall = True  # Hit right wall

        # Top wall
        if self.y - self.radius < top_boundary:
            self.y = top_boundary + self.radius
            self.vy = abs(self.vy)  # Ensure positive (down) direction
            changed = True
            hit_wall = True  # Hit top wall

        # Bottom boundary - ball is lost
        if self.y - self.radius > bottom_boundary:
            self.active = False
            return (False, False, False)

        # Handle paddle collision if paddle is provided
        hit_paddle = False
        if paddle and self._check_paddle_collision(paddle):
            changed = True
            hit_paddle = True

        # Update the collision rectangle
        self.update_rect()

        # Apply some randomness to prevent predictable patterns
        if changed:
            self._add_random_factor()

        return (True, hit_paddle, hit_wall)

    def update_rect(self) -> None:
        """Update the collision rectangle based on current position."""
        self.rect.x = int(self.x - self.radius)
        self.rect.y = int(self.y - self.radius)

    def _check_paddle_collision(self, paddle: Any) -> bool:
        """Check for collision with the paddle and handle bouncing.

        Args:
        ----
            paddle (Paddle): The paddle object

        Returns:
        -------
            bool: True if collision occurred, False otherwise

        """
        # Simple rectangle collision check
        if not pygame.Rect(self.rect).colliderect(paddle.rect):
            return False

        # If we're moving upward, ignore the collision (already bounced)
        if self.vy < 0:
            return False

        # Sound will be triggered from the return value
        # Add a comment to help identify this in main.py

        # Calculate bounce angle based on where the ball hit the paddle
        # The further from the center, the steeper the angle
        paddle_center = paddle.rect.centerx
        hit_pos = self.x

        # Normalize position (-1.0 to 1.0)
        offset = (hit_pos - paddle_center) / (paddle.rect.width / 2)

        # Calculate new angle (between 30 and 150 degrees)
        angle = math.pi / 2 + (offset * math.pi / 3)  # Pi/3 = 60 degrees

        # Calculate ball speed (maintain current speed)
        speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)

        # Update velocity components
        self.vx = speed * math.cos(angle)
        self.vy = -speed * math.sin(angle)  # Negative for upward direction

        # Move ball to top of paddle to prevent sticking
        self.y = paddle.rect.top - self.radius - 1

        # Handle sticky paddle
        if paddle.is_sticky():
            self.stuck_to_paddle = True
            self.paddle_offset = 0.0

        return True

    def release_from_paddle(self) -> None:
        """Release the ball if it's stuck to the paddle."""
        logger.debug(f"Ball released from paddle at x={self.x}, y={self.y}")
        self.stuck_to_paddle = False
        logger.debug(f"[release_from_paddle] Ball released: vx={self.vx}, vy={self.vy}")

    def _add_random_factor(self) -> None:
        """Add a slight randomness to prevent predictable patterns."""
        # Apply up to 5% random variance to speed
        speed = math.sqrt(self.vx * self.vx + self.vy * self.vy)
        angle = math.atan2(
            -self.vy, self.vx
        )  # Note negative vy due to screen coordinates

        # Add small random angle change (up to 5 degrees)
        angle += random.uniform(-0.087, 0.087)  # ±5 degrees in radians

        # Recalculate velocity with a slight random speed boost
        speed_factor = random.uniform(0.95, 1.05)
        self.vx = speed * speed_factor * math.cos(angle)
        self.vy = -speed * speed_factor * math.sin(angle)  # Negative for upward

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the ball.

        Args:
        ----
            surface (pygame.Surface): Surface to draw on

        """
        if not Ball.sprites:
            # Fallback to circle drawing if sprites failed to load
            pygame.draw.circle(
                surface, self.color, (int(self.x), int(self.y)), self.radius
            )

            # Add a highlight effect
            highlight_pos = (
                int(self.x - self.radius * 0.5),
                int(self.y - self.radius * 0.5),
            )
            highlight_radius = int(self.radius * 0.3)
            pygame.draw.circle(
                surface, (255, 255, 255), highlight_pos, highlight_radius
            )
        elif self.birth_animation and Ball.animation_frames:
            # Draw birth animation frames
            current_frame = Ball.animation_frames[self.animation_frame]
            frame_rect = current_frame.get_rect()
            frame_rect.center = (int(self.x), int(self.y))
            surface.blit(current_frame, frame_rect)

            # Update animation frame
            self.frame_counter += 1
            if self.frame_counter >= 4:  # Speed of animation
                self.frame_counter = 0
                self.animation_frame += 1
                if self.animation_frame >= len(Ball.animation_frames):
                    self.animation_frame = 0
                    self.birth_animation = False
        else:
            # Draw animated main ball sprite
            sprite = Ball.sprites[self.anim_frame]
            sprite_rect = sprite.get_rect()
            sprite_rect.center = (int(self.x), int(self.y))
            surface.blit(sprite, sprite_rect)

    def get_rect(self) -> pygame.Rect:
        """Get the ball's collision rectangle."""
        return self.rect

    def get_position(self) -> Tuple[float, float]:
        """Get the ball's current position."""
        return (self.x, self.y)

    def set_position(self, x: float, y: float) -> None:
        """Set the ball's position.

        Args:
        ----
            x (float): New X position
            y (float): New Y position

        """
        self.x = float(x)
        self.y = float(y)
        self.update_rect()

    def set_velocity(self, vx: float, vy: float) -> None:
        """Set the ball's velocity.

        Args:
        ----
            vx (float): X velocity component
            vy (float): Y velocity component

        """
        self.vx = float(vx)
        self.vy = float(vy)

    def is_active(self) -> bool:
        """Check if the ball is still active."""
        return self.active
