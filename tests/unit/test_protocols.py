"""
Unit tests for the game protocols.

This module contains tests for the protocol definitions in the protocols module.
"""

import pygame

from xboing.game.collision import CollisionType
from xboing.game.protocols import (
    Activatable,
    Collidable,
    Drawable,
    GameObject,
    Positionable,
    Updateable,
)


class MockUpdateable:
    """Mock implementation of the Updateable protocol."""

    def update(self, delta_ms):
        """Update the object state."""
        return []


class MockDrawable:
    """Mock implementation of the Drawable protocol."""

    def draw(self, surface):
        """Draw the object on the given surface."""
        pass


class MockCollidable:
    """Mock implementation of the Collidable protocol."""

    def get_rect(self):
        """Get the object's collision rectangle."""
        return pygame.Rect(0, 0, 10, 10)

    def collides_with(self, other):
        """Check if this object collides with another collidable object."""
        return self.get_rect().colliderect(other.get_rect())

    def get_collision_type(self):
        """Get the collision type of this object."""
        return CollisionType.BLOCK.value

    def handle_collision(self, other):
        """Handle collision with another object."""
        pass


class MockPositionable:
    """Mock implementation of the Positionable protocol."""

    def __init__(self):
        """Initialize with a default position."""
        self.x = 0
        self.y = 0

    def get_position(self):
        """Get the object's current position as (x, y)."""
        return self.x, self.y

    def set_position(self, x, y):
        """Set the object's position to (x, y)."""
        self.x = x
        self.y = y


class MockActivatable:
    """Mock implementation of the Activatable protocol."""

    def __init__(self):
        """Initialize with a default active state."""
        self.active = True

    def is_active(self):
        """Check if the object is currently active."""
        return self.active

    def set_active(self, active):
        """Set the object's active state."""
        self.active = active


class MockGameObject(
    MockUpdateable, MockDrawable, MockCollidable, MockPositionable, MockActivatable
):
    """Mock implementation of the GameObject protocol."""

    pass


def test_updateable_protocol():
    """Test that the Updateable protocol works correctly."""
    obj = MockUpdateable()
    assert isinstance(obj, Updateable)
    assert obj.update(16.67) == []


def test_drawable_protocol():
    """Test that the Drawable protocol works correctly."""
    obj = MockDrawable()
    assert isinstance(obj, Drawable)
    # Create a mock surface for testing
    surface = pygame.Surface((100, 100))
    # This should not raise an exception
    obj.draw(surface)


def test_collidable_protocol():
    """Test that the Collidable protocol works correctly."""
    obj1 = MockCollidable()
    obj2 = MockCollidable()
    assert isinstance(obj1, Collidable)
    assert obj1.get_rect() == pygame.Rect(0, 0, 10, 10)
    assert obj1.collides_with(obj2) is True


def test_positionable_protocol():
    """Test that the Positionable protocol works correctly."""
    obj = MockPositionable()
    assert isinstance(obj, Positionable)
    assert obj.get_position() == (0, 0)
    obj.set_position(10, 20)
    assert obj.get_position() == (10, 20)


def test_activatable_protocol():
    """Test that the Activatable protocol works correctly."""
    obj = MockActivatable()
    assert isinstance(obj, Activatable)
    assert obj.is_active() is True
    obj.set_active(False)
    assert obj.is_active() is False


def test_game_object_protocol():
    """Test that the GameObject protocol works correctly."""
    obj = MockGameObject()
    assert isinstance(obj, GameObject)
    assert isinstance(obj, Updateable)
    assert isinstance(obj, Drawable)
    assert isinstance(obj, Collidable)
    assert isinstance(obj, Positionable)
    assert isinstance(obj, Activatable)
