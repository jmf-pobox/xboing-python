"""Bullet: A projectile that can be fired from the paddle."""

import logging
from typing import List, Tuple

import pygame

from xboing.game.circular_game_shape import CircularGameShape
from xboing.game.collision import CollisionType
from xboing.game.physics_mixin import PhysicsMixin

logger = logging.getLogger(__name__)

DEFAULT_AMMO_QUANTITY: int = 4


class Bullet(CircularGameShape, PhysicsMixin):
    """A projectile that can be fired from the paddle."""

    # Default values
    DEFAULT_RADIUS = 4  # Default radius of bullets in pixels
    DEFAULT_VELOCITY_Y = -10.0  # Default upward velocity of bullets (negative is up)
    DEFAULT_PADDLE_GAP = 1  # Default gap in pixels between bullet and paddle

    def __init__(
        self,
        x: float,
        y: float,
        vx: float = 0.0,
        vy: float = DEFAULT_VELOCITY_Y,
        radius: int = DEFAULT_RADIUS,
        color: Tuple[int, int, int] = (255, 255, 0),
    ) -> None:
        """Initialize the bullet.

        Args:
            x: Initial x position
            y: Initial y position
            vx: Initial x velocity
            vy: Initial y velocity
            radius: Bullet radius
            color: Bullet color

        """
        # Initialize the PhysicsMixin first so self.physics exists
        PhysicsMixin.__init__(self, x, y, vx, vy)
        # Now initialize the CircularGameShape
        CircularGameShape.__init__(self, x, y, radius)
        self.color = color
        self.active = True
        self.update_rect()

    def update(self, delta_ms: float) -> List[pygame.event.Event]:
        """Update the bullet's position based on its velocity and the elapsed time.

        Args:
            delta_ms (float): Time since last frame in milliseconds.

        Returns:
            List[pygame.event.Event]: List of events generated during the update.

        """
        events: List[pygame.event.Event] = []

        old_x, old_y = self.x, self.y

        # Update position using physics component
        self.update_physics(delta_ms)
        self.x, self.y = self.physics.get_position()

        logger.debug(f"Bullet updated: ({old_x}, {old_y}) -> ({self.x}, {self.y})")
        self.update_rect()

        # Deactivate if the bullet is past the top of the game area
        if self.y + self.radius < 0:
            self.active = False

        return events

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the bullet as a filled circle.

        Args:
            surface: Surface to draw on.

        """
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def get_rect(self) -> pygame.Rect:
        """Get the bullet's collision rectangle."""
        return self.rect

    def is_active(self) -> bool:
        """Return True if the bullet is still in play (on screen)."""
        # Check if the bullet is off-screen or has been explicitly deactivated
        active = 0 <= self.x <= 495 and 0 <= self.y <= 640 and self.active
        logger.debug(f"Bullet is_active called: ({self.x}, {self.y}) -> {active}")
        return active

    def set_active(self, active: bool) -> None:
        """Set the bullet's active state.

        Args:
            active: The new active state.

        """
        self.active = active

    def update_rect(self) -> None:
        """Update the collision rectangle based on the current position."""
        # Update the CircularGameShape position from the physics component
        self.x, self.y = self.physics.get_position()
        # Use the CircularGameShape's update_rect method
        super().update_rect()

    def get_collision_type(self) -> str:
        """Return the collision type for Bullet."""
        return CollisionType.BULLET.value

    def handle_collision(self, other: object) -> None:
        """Handle collision with another object (no-op for Bullet stub)."""
        del other  # Remove unused argument warning

    def set_position(self, x: float, y: float) -> None:
        """Set the bullet's position.

        Args:
            x (float): New X position
            y (float): New Y position

        """
        self.x = float(x)
        self.y = float(y)
        self.physics.set_position((self.x, self.y))
        self.x, self.y = self.physics.get_position()
        self.update_rect()

    def set_velocity(self, vx: float, vy: float) -> None:
        """Set the bullet's velocity.

        Args:
            vx (float): X velocity
            vy (float): Y velocity

        """
        self.physics.set_velocity((float(vx), float(vy)))
        self.x, self.y = self.physics.get_position()
