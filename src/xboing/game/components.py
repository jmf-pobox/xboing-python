"""
Components for game objects in XBoing Python.

This module defines reusable components that can be composed with game objects
to provide common functionality. These components enhance reusability across
different games and enable a more modular approach to game object design.

Architecture Note:
------------------
PhysicsComponent is a low-level composition component used internally by
PhysicsMixin. It provides pure physics calculations without any game-specific
behavior. PhysicsMixin (in physics_mixin.py) wraps this component to provide
a convenient mixin interface with property access (vx, vy) for game objects.

This is intentional layering, not duplication:
- PhysicsComponent: Low-level physics calculations (composition)
- PhysicsMixin: Convenience wrapper for game objects (mixin pattern)
"""

from typing import Tuple


class PhysicsComponent:
    """Component for handling physics behavior of game objects."""

    def __init__(
        self,
        position: Tuple[float, float],
        velocity: Tuple[float, float] = (0, 0),
        acceleration: Tuple[float, float] = (0, 0),
        mass: float = 1.0,
    ) -> None:
        """
        Initialize the physics component with position, velocity, acceleration, and mass.

        Args:
            position: Initial position as (x, y).
            velocity: Initial velocity as (vx, vy). Defaults to (0, 0).
            acceleration: Initial acceleration as (ax, ay). Defaults to (0, 0).
            mass: Object mass, affects force calculations. Defaults to 1.0.

        """
        self.position = position
        self.velocity = velocity
        self.acceleration = acceleration
        self.mass = mass

    def update(self, delta_ms: float) -> Tuple[float, float]:
        """
        Update the physics state based on the time delta.

        Args:
            delta_ms: Time delta in milliseconds since the last update.

        Returns:
            The new position as (x, y).

        """
        # Normalize for 60 FPS (16.67 ms per frame)
        delta_factor = delta_ms / 16.67

        # Store the current velocity for position update
        current_vx, current_vy = self.velocity

        # Update position based on current velocity
        self.position = (
            self.position[0] + current_vx * delta_factor,
            self.position[1] + current_vy * delta_factor,
        )

        # Update velocity based on acceleration
        self.velocity = (
            current_vx + self.acceleration[0] * delta_factor,
            current_vy + self.acceleration[1] * delta_factor,
        )

        return self.position

    def apply_force(self, force: Tuple[float, float]) -> None:
        """
        Apply a force to the object, changing its acceleration based on mass.

        Args:
            force: Force vector as (fx, fy).

        """
        self.acceleration = (
            self.acceleration[0] + force[0] / self.mass,
            self.acceleration[1] + force[1] / self.mass,
        )

    def set_velocity(self, velocity: Tuple[float, float]) -> None:
        """
        Set the object's velocity.

        Args:
            velocity: New velocity as (vx, vy).

        """
        self.velocity = velocity

    def get_velocity(self) -> Tuple[float, float]:
        """
        Get the object's current velocity.

        Returns:
            Current velocity as (vx, vy).

        """
        return self.velocity

    def set_position(self, position: Tuple[float, float]) -> None:
        """
        Set the object's position.

        Args:
            position: New position as (x, y).

        """
        self.position = position

    def get_position(self) -> Tuple[float, float]:
        """
        Get the object's current position.

        Returns:
            Current position as (x, y).

        """
        return self.position

    def set_acceleration(self, acceleration: Tuple[float, float]) -> None:
        """
        Set the object's acceleration.

        Args:
            acceleration: New acceleration as (ax, ay).

        """
        self.acceleration = acceleration

    def get_acceleration(self) -> Tuple[float, float]:
        """
        Get the object's current acceleration.

        Returns:
            Current acceleration as (ax, ay).

        """
        return self.acceleration
