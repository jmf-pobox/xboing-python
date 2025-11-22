"""Ball: The main game object that bounces around the screen."""

import logging
import math
import os
import random
from typing import Any, ClassVar, List, Optional, Tuple, Union

import pygame

from xboing.engine.events import (
    BallLostEvent,
    PaddleHitEvent,
    WallHitEvent,
)
from xboing.game.circular_game_shape import CircularGameShape
from xboing.game.collision import CollisionType
from xboing.game.physics_mixin import PhysicsMixin
from xboing.utils.asset_loader import load_image
from xboing.utils.asset_paths import get_balls_dir, get_images_dir

# Type alias for events used in this module
Event = Union[BallLostEvent, PaddleHitEvent, WallHitEvent]

logger = logging.getLogger(__name__)


BALL_RADIUS = 8  # Approximated from the original game


class Ball(CircularGameShape, PhysicsMixin):
    """The main game object that bounces around the screen."""

    # Class variables for sprites
    sprites: ClassVar[List[pygame.Surface]] = []
    animation_frames: ClassVar[List[pygame.Surface]] = []
    guide_images: ClassVar[List[pygame.Surface]] = []
    logger: ClassVar[logging.Logger] = logging.getLogger("xboing.Ball")
    GUIDE_ANIM_FRAME_MS: ClassVar[float] = 80.0  # ms per guide animation frame

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

    @classmethod
    def load_guide_images(cls) -> None:
        """Load the 11 guide images for the paddle launch direction indicator."""
        if cls.guide_images:
            return  # Already loaded
        guides_dir = os.path.join(get_images_dir(), "guides")
        cls.guide_images = []
        for i in range(1, 12):
            filename = os.path.join(guides_dir, f"guide{i}.png")
            try:
                img = load_image(filename, alpha=True)
                cls.guide_images.append(img)
            except (pygame.error, FileNotFoundError) as e:
                cls.logger.warning(f"Failed to load guide image {filename}: {e}")
                # Fallback: magenta rectangle
                fallback = pygame.Surface((29, 12), pygame.SRCALPHA)
                fallback.fill((255, 0, 255))
                cls.guide_images.append(fallback)

    def __init__(
        self,
        x: float,
        y: float,
        vx: float = 0.0,
        vy: float = 0.0,
        radius: int = 5,
        color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        """Initialize the ball.

        Args:
            x: Initial x position
            y: Initial y position
            vx: Initial x velocity
            vy: Initial y velocity
            radius: Ball radius
            color: Ball color

        """
        # Initialize the CircularGameShape
        super().__init__(x, y, radius)
        # Initialize the PhysicsMixin
        PhysicsMixin.__init__(self, x, y, vx, vy)
        self.color = color
        self.active = True

        # State
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

        # Guide animation state
        self.guide_pos: int = 0  # Index into guide_images (0-10)
        self.guide_inc: int = 1  # +1 or -1 for ping-pong
        self.guide_anim_counter: float = 0.0  # ms accumulator

        # Ensure sprites and guide images are loaded
        if not Ball.sprites:
            Ball.load_sprites()
        if not Ball.guide_images:
            Ball.load_guide_images()

    def _update_animation(self, delta_ms: float) -> None:
        """Update ball animation frame."""
        if self.birth_animation or len(Ball.sprites) <= 1:
            return
        self.anim_counter += delta_ms
        if self.anim_counter >= self.anim_frame_ms:
            self.anim_counter -= self.anim_frame_ms
            self.anim_frame = (self.anim_frame + 1) % len(Ball.sprites)

    def _update_stuck_to_paddle(self, paddle: Any, delta_ms: float) -> None:
        """Update ball position and guide animation when stuck to paddle."""
        # Update position to stick to paddle
        self.x = paddle.rect.centerx + self.paddle_offset
        self.y = paddle.rect.top - self.radius - 1
        # Update physics component position
        self.physics.set_position((self.x, self.y))
        self.update_rect()

        # Guide animation update
        self.guide_anim_counter += delta_ms
        while self.guide_anim_counter >= Ball.GUIDE_ANIM_FRAME_MS:
            self.guide_anim_counter -= Ball.GUIDE_ANIM_FRAME_MS
            self.guide_pos += self.guide_inc
            if self.guide_pos == 10:
                self.guide_inc = -1
            elif self.guide_pos == 0:
                self.guide_inc = 1

    def _handle_wall_collisions(
        self,
        offset_x: int,
        offset_y: int,
        screen_width: int,
        screen_height: int,
    ) -> tuple[bool, list[Event], tuple[float, float]]:
        """Handle collisions with walls.

        Returns:
            tuple: (changed, events, (vx, vy))

        """
        events: List[Event] = []
        changed = False
        vx, vy = self.physics.get_velocity()

        left_boundary = offset_x
        right_boundary = offset_x + screen_width
        top_boundary = offset_y
        bottom_boundary = offset_y + screen_height

        # Left and right walls
        if self.x - self.radius < left_boundary:
            self.x = left_boundary + self.radius
            vx = abs(vx)
            changed = True
            events.append(WallHitEvent())
        if self.x + self.radius > right_boundary:
            self.x = right_boundary - self.radius
            vx = -abs(vx)
            changed = True
            events.append(WallHitEvent())

        # Top wall
        if self.y - self.radius < top_boundary:
            self.y = top_boundary + self.radius
            vy = abs(vy)
            changed = True
            events.append(WallHitEvent())

        # Bottom boundary - ball is lost
        if self.y - self.radius > bottom_boundary:
            self.active = False
            events.append(BallLostEvent())

        return changed, events, (vx, vy)

    def update(
        self,
        delta_ms: float,
        screen_width: int = 0,
        screen_height: int = 0,
        paddle: Optional[Any] = None,
        offset_x: int = 0,
        offset_y: int = 0,
    ) -> List[Event]:
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
            List[Event]: List of events generated during the update

        """
        events: List[Event] = []

        self._update_animation(delta_ms)

        if not self.active:
            return events

        if self.stuck_to_paddle and paddle:
            self._update_stuck_to_paddle(paddle, delta_ms)
            return events

        # Update position using physics component
        self.physics.update(delta_ms)
        self.x, self.y = self.physics.get_position()
        self.update_rect()

        # Handle wall collisions
        changed, wall_events, (vx, vy) = self._handle_wall_collisions(
            offset_x, offset_y, screen_width, screen_height
        )
        events.extend(wall_events)

        # Return early if ball was lost at bottom boundary
        if any(isinstance(e, BallLostEvent) for e in wall_events):
            return events

        # Update physics with new position and velocity if changed
        if changed:
            self.physics.set_position((self.x, self.y))
            self.physics.set_velocity((vx, vy))

        # Handle paddle collision if paddle is provided
        if paddle and self._check_paddle_collision(paddle):
            changed = True
            events.append(PaddleHitEvent())

        # Update the collision rectangle
        self.update_rect()

        # Apply some randomness to prevent predictable patterns
        if changed:
            self._add_random_factor()

        return events

    def update_rect(self) -> None:
        """Update the collision rectangle based on the current position."""
        # Update the CircularGameShape position from the physics component
        self.x, self.y = self.get_position()
        # Use the CircularGameShape's update_rect method
        super().update_rect()

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

        # Get current velocity from physics component
        vx, vy = self.get_velocity()

        # If we're moving upward, ignore the collision (already bounced)
        if vy < 0:
            return False

        # Sound will be triggered from the return value
        # Add a comment to help identify this in main.py

        # Calculate bounce angle based on where the ball hit the paddle
        # The further from the center, the steeper the angle
        paddle_center = paddle.rect.centerx
        hit_pos = self.x

        # Normalize position (-1.0 to 1.0)
        offset = (hit_pos - paddle_center) / (paddle.rect.width / 2)

        # Calculate a new angle (between 30 and 150 degrees)
        angle = math.pi / 2 + (offset * math.pi / 3)  # Pi/3 = 60 degrees

        # Calculate ball speed (maintain current speed)
        speed = math.sqrt(vx * vx + vy * vy)

        # Update velocity components
        new_vx = speed * math.cos(angle)
        new_vy = -speed * math.sin(angle)  # Negative for an upward direction
        self.set_velocity(new_vx, new_vy)

        # Move ball to top of paddle to prevent sticking
        self.y = paddle.rect.top - self.radius - 1
        self.set_position(self.x, self.y)

        # Handle sticky paddle
        if paddle.is_sticky():
            self.stuck_to_paddle = True
            self.paddle_offset = 0.0

        return True

    def get_launch_velocity_from_guide_pos(self) -> Tuple[float, float]:
        """Get the launch velocity (vx, vy) for the current guide position."""
        # Default speed if no current velocity
        default_speed = 5.0

        mapping = [
            (-5, -1),
            (-4, -2),
            (-3, -3),
            (-2, -4),
            (-1, -5),
            (0, -5),
            (1, -5),
            (2, -4),
            (3, -3),
            (4, -2),
            (5, -1),
        ]

        # Get current velocity and speed
        vx, vy = self.get_velocity()
        current_speed = math.sqrt(vx * vx + vy * vy)

        # If no current speed, use default
        if current_speed < 0.1:
            current_speed = default_speed
            logger.debug(f"Using default speed: {default_speed}")

        # Get direction from guide position
        dx, dy = mapping[self.guide_pos]
        logger.debug(
            f"Guide position {self.guide_pos} gives direction: dx={dx}, dy={dy}"
        )

        # Normalize direction vector
        norm = math.sqrt(dx * dx + dy * dy)
        if norm < 0.1:  # Avoid division by zero
            logger.debug("Direction vector too small, using straight up")
            return 0.0, -current_speed

        # Scale direction by current speed
        final_vx = current_speed * dx / norm
        final_vy = current_speed * dy / norm

        logger.debug(f"Calculated launch velocity: vx={final_vx}, vy={final_vy}")
        return final_vx, final_vy

    def release_from_paddle(self) -> None:
        """Release the ball if it's stuck to the paddle, using guide_pos
        for the launch direction.
        """
        logger.debug(f"Ball released from paddle at x={self.x}, y={self.y}")
        if self.stuck_to_paddle:
            vx, vy = self.get_launch_velocity_from_guide_pos()
            logger.debug(f"Initial launch velocity: vx={vx}, vy={vy}")

            # If velocity is zero or too small, set a default upward velocity
            speed = math.sqrt(vx * vx + vy * vy)
            if speed < 1.0:
                logger.debug("Velocity too small, using default upward velocity")
                vx = 0.0
                vy = -5.0

            self.set_velocity(vx, vy)
            # Verify velocity was set correctly
            final_vx, final_vy = self.get_velocity()
            logger.debug(f"Final velocity after release: vx={final_vx}, vy={final_vy}")

        self.stuck_to_paddle = False

    def _add_random_factor(self) -> None:
        """Add a slight randomness to prevent predictable patterns."""
        vx, vy = self.get_velocity()
        speed = math.sqrt(vx * vx + vy * vy)
        angle = math.atan2(-vy, vx)
        angle += random.uniform(-0.087, 0.087)
        speed_factor = random.uniform(0.95, 1.05)
        new_vx = speed * speed_factor * math.cos(angle)
        new_vy = -speed * speed_factor * math.sin(angle)
        # Ensure the new velocity is not exactly the same as before
        if abs(new_vx - vx) < 1e-6 and abs(new_vy - vy) < 1e-6:
            new_vx += 0.1
        self.set_velocity(new_vx, new_vy)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the ball.

        Args:
        ----
            surface (pygame.Surface): Surface to draw on

        """
        # Draw the guide if stuck to paddle
        if self.stuck_to_paddle and Ball.guide_images:
            guide_img = Ball.guide_images[self.guide_pos]
            guide_rect = guide_img.get_rect()
            guide_rect.centerx = int(self.x)
            # 2 px gap above ball
            guide_rect.bottom = int(self.y) - self.radius - 2
            surface.blit(guide_img, guide_rect)

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
        return self.x, self.y

    def set_position(self, x: float, y: float) -> None:
        """Set the ball's position.

        Args:
        ----
            x (float): New X position
            y (float): New Y position

        """
        self.x = float(x)
        self.y = float(y)
        self.physics.set_position((self.x, self.y))
        self.update_rect()

    def set_velocity(self, vx: float, vy: float) -> None:
        """Set the ball's velocity.

        Args:
        ----
            vx (float): X velocity
            vy (float): Y velocity

        """
        logger.debug(f"Setting ball velocity: vx={vx}, vy={vy}")
        self.physics.set_velocity((float(vx), float(vy)))
        # Get current position from physics component
        self.x, self.y = self.physics.get_position()
        self.update_rect()

    def is_active(self) -> bool:
        """Check if the ball is still active."""
        return self.active

    def set_active(self, active: bool) -> None:
        """Set the ball's active state.

        Args:
            active: The new active state.

        """
        self.active = active

    def get_collision_type(self) -> str:
        """Return the collision type for Ball."""
        return CollisionType.BALL.value

    def handle_collision(self, other: object) -> None:
        """Handle collision with another object (no-op for Ball stub)."""
        del other  # Remove unused argument warning
