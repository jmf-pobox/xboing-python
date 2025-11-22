"""
Unit tests for the collision system.

This module contains tests for the collision system defined in the collision module.
"""

import pygame

from xboing.game.collision import CollisionSystem, CollisionType


class MockCollidable:
    """Mock implementation of the Collidable protocol."""

    def __init__(self, x, y, width, height):
        """Initialize with a rectangle at the given position and size."""
        self.rect = pygame.Rect(x, y, width, height)

    def get_rect(self):
        """Get the object's collision rectangle."""
        return self.rect

    def collides_with(self, other):
        """Check if this object collides with another collidable object."""
        return self.get_rect().colliderect(other.get_rect())

    def get_collision_type(self):
        """Get the collision type of this object."""
        return CollisionType.BLOCK.value

    def handle_collision(self, other):
        """Handle collision with another object."""
        pass


def test_collision_system_init():
    """Test that the CollisionSystem initializes correctly."""
    # Test with default values
    system = CollisionSystem()
    assert system.screen_width == 0
    assert system.screen_height == 0
    assert system.collidables == []

    # Test with custom values
    system = CollisionSystem(800, 600)
    assert system.screen_width == 800
    assert system.screen_height == 600
    assert system.collidables == []


def test_collision_system_add_remove_collidable():
    """Test adding and removing collidables from the system."""
    system = CollisionSystem()
    obj1 = MockCollidable(0, 0, 10, 10)
    obj2 = MockCollidable(20, 20, 10, 10)

    # Test adding collidables
    system.add_collidable(obj1)
    assert len(system.collidables) == 1
    assert system.collidables[0] is obj1

    # Test adding the same collidable twice (should not duplicate)
    system.add_collidable(obj1)
    assert len(system.collidables) == 1

    # Test adding another collidable
    system.add_collidable(obj2)
    assert len(system.collidables) == 2
    assert system.collidables[1] is obj2

    # Test removing a collidable
    system.remove_collidable(obj1)
    assert len(system.collidables) == 1
    assert system.collidables[0] is obj2

    # Test removing a collidable that's not in the system
    system.remove_collidable(obj1)
    assert len(system.collidables) == 1

    # Test clearing all collidables
    system.clear()
    assert len(system.collidables) == 0


def test_collision_system_check_collisions():
    """Test checking for collisions between collidables."""
    system = CollisionSystem()

    # Create collidables that don't collide
    obj1 = MockCollidable(0, 0, 10, 10)
    obj2 = MockCollidable(20, 20, 10, 10)
    system.add_collidable(obj1)
    system.add_collidable(obj2)

    # Check for collisions (should be none)
    collisions = system.check_collisions()
    assert len(collisions) == 0

    # Create a collidable that collides with obj1
    obj3 = MockCollidable(5, 5, 10, 10)
    system.add_collidable(obj3)

    # Check for collisions (should be one pair)
    collisions = system.check_collisions()
    assert len(collisions) == 1
    assert (obj1, obj3) in collisions

    # Create a collidable that collides with obj2
    obj4 = MockCollidable(25, 25, 10, 10)
    system.add_collidable(obj4)

    # Check for collisions (should be two pairs)
    collisions = system.check_collisions()
    assert len(collisions) == 2
    assert (obj1, obj3) in collisions
    assert (obj2, obj4) in collisions


def test_collision_system_get_collisions_for():
    """Test getting collisions for a specific collidable."""
    system = CollisionSystem()

    # Create collidables
    obj1 = MockCollidable(0, 0, 10, 10)
    obj2 = MockCollidable(5, 5, 10, 10)  # Collides with obj1
    obj3 = MockCollidable(20, 20, 10, 10)  # Doesn't collide with obj1 or obj2

    system.add_collidable(obj1)
    system.add_collidable(obj2)
    system.add_collidable(obj3)

    # Get collisions for obj1
    collisions = system.get_collisions_for(obj1)
    assert len(collisions) == 1
    assert obj2 in collisions

    # Get collisions for obj3
    collisions = system.get_collisions_for(obj3)
    assert len(collisions) == 0

    # Get collisions for an object not in the system
    obj4 = MockCollidable(30, 30, 10, 10)
    collisions = system.get_collisions_for(obj4)
    assert len(collisions) == 0


def test_collision_system_get_collidables():
    """Test getting all collidables from the system."""
    system = CollisionSystem()

    # Create collidables
    obj1 = MockCollidable(0, 0, 10, 10)
    obj2 = MockCollidable(20, 20, 10, 10)

    system.add_collidable(obj1)
    system.add_collidable(obj2)

    # Get all collidables
    collidables = system.get_collidables()
    assert len(collidables) == 2
    assert obj1 in collidables
    assert obj2 in collidables

    # Verify that the returned list is a copy
    collidables.clear()
    assert len(system.collidables) == 2
