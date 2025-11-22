"""PhysicsMixin: A mixin class that provides common physics-related functionality.

Architecture Note:
------------------
This mixin wraps PhysicsComponent (from components.py) to provide a convenient
mixin interface for game objects. It adds property-based access (vx, vy) and
convenience methods while delegating physics calculations to PhysicsComponent.

This is intentional layering, not duplication:
- PhysicsComponent: Low-level physics calculations (composition)
- PhysicsMixin: Convenience wrapper for game objects (mixin pattern)

The two-layer design allows PhysicsComponent to remain pure and reusable while
PhysicsMixin provides game-specific convenience features.
"""

from typing import Any, Tuple

import pygame

from xboing.game.components import PhysicsComponent


class PhysicsMixin:
    """Mixin class providing convenient physics functionality for game objects.

    This mixin wraps PhysicsComponent to provide property access (vx, vy) and
    convenient methods for game objects that need physics behavior.
    """

    def __init__(self, x: float, y: float, vx: float, vy: float) -> None:
        """Initialize the physics component.

        Args:
            x: Initial x position
            y: Initial y position
            vx: Initial x velocity
            vy: Initial y velocity

        """
        self.physics = PhysicsComponent(
            position=(x, y), velocity=(vx, vy), acceleration=(0, 0), mass=1.0
        )

    def update_physics(self, delta_ms: float) -> None:
        """Update the physics component.

        Args:
            delta_ms: Time since last update in milliseconds

        """
        self.physics.update(delta_ms)

    def get_position(self) -> Tuple[float, float]:
        """Get the current position.

        Returns:
            Tuple of (x, y) coordinates

        """
        return self.physics.get_position()

    def set_position(self, x: float, y: float) -> None:
        """Set the position.

        Args:
            x: New x position
            y: New y position

        """
        self.physics.set_position((x, y))

    def get_velocity(self) -> Tuple[float, float]:
        """Get the current velocity.

        Returns:
            Tuple of (vx, vy) velocities

        """
        return self.physics.get_velocity()

    def set_velocity(self, vx: float, vy: float) -> None:
        """Set the velocity.

        Args:
            vx: New x velocity
            vy: New y velocity

        """
        self.physics.set_velocity((vx, vy))

    @property
    def vx(self) -> float:
        """Get the x velocity."""
        return self.get_velocity()[0]

    @vx.setter
    def vx(self, value: float) -> None:
        """Set the x velocity."""
        _, vy = self.get_velocity()
        self.set_velocity(value, vy)

    @property
    def vy(self) -> float:
        """Get the y velocity."""
        return self.get_velocity()[1]

    @vy.setter
    def vy(self, value: float) -> None:
        """Set the y velocity."""
        vx, _ = self.get_velocity()
        self.set_velocity(vx, value)

    def collides_with(self, other: Any) -> bool:
        """Check if this object collides with another collidable object."""
        return self.get_rect().colliderect(other.get_rect())

    def get_rect(self) -> pygame.Rect:
        """Return the object's rect for collision detection. Must be implemented by subclass."""
        raise NotImplementedError
