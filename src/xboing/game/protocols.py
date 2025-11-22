"""
Protocols for game objects in XBoing Python.

This module defines the core protocols that formalize the interfaces
of game objects in the XBoing Python port. These protocols enable
better maintainability, type safety, and testability, while also
supporting the development of other similar games.
"""

from typing import Any, List, Protocol, Tuple, runtime_checkable

import pygame


@runtime_checkable
class Updateable(Protocol):
    """Protocol for objects that update with the game clock."""

    def update(self, delta_ms: float) -> List[pygame.event.Event]:
        """
        Update the object state based on the time delta.

        Args:
            delta_ms: Time delta in milliseconds since the last update.

        Returns:
            A list of events that resulted from the update.

        """
        ...


@runtime_checkable
class Drawable(Protocol):
    """Protocol for objects that can draw themselves."""

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the object on the given surface.

        Args:
            surface: The pygame surface to draw on.

        """
        ...


@runtime_checkable
class Collidable(Protocol):
    """Protocol for objects that can participate in collision detection."""

    def collides_with(self, other: Any) -> bool:
        """Check if this object collides with another object.

        Args:
            other: Another object to check collision with.

        Returns:
            True if the objects collide, False otherwise.

        """
        ...

    def get_rect(self) -> pygame.Rect:
        """Get the rectangle representing this object.

        Returns:
            A pygame.Rect representing the object's bounds.

        """
        ...

    def get_collision_type(self) -> str:
        """Get the collision type of this object.

        Returns:
            A string identifying the type of collidable object.

        """
        ...

    def handle_collision(self, other: Any) -> None:
        """Handle collision with another object.

        Args:
            other: The object this object collided with.

        """
        ...


@runtime_checkable
class Positionable(Protocol):
    """Protocol for objects with a position in the game world."""

    def get_position(self) -> Tuple[float, float]:
        """
        Get the object's current position as (x, y).

        Returns:
            A tuple containing the x and y coordinates.

        """
        ...

    def set_position(self, x: float, y: float) -> None:
        """
        Set the object's position to (x, y).

        Args:
            x: The x coordinate.
            y: The y coordinate.

        """
        ...


@runtime_checkable
class Activatable(Protocol):
    """Protocol for objects with an active state."""

    def is_active(self) -> bool:
        """
        Check if the object is currently active.

        Returns:
            True if the object is active, False otherwise.

        """
        ...

    def set_active(self, active: bool) -> None:
        """
        Set the object's active state.

        Args:
            active: The new active state.

        """
        ...


@runtime_checkable
class GameObject(Updateable, Drawable, Collidable, Positionable, Activatable, Protocol):
    """
    Combined protocol for complete game objects.

    This protocol combines all the core protocols to define a complete
    game object interface. It can be used for type checking and to ensure
    that game objects implement all required methods.
    """

    # No additional implementation needed
