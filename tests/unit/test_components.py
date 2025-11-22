"""
Unit tests for the game components.

This module contains tests for the component definitions in the components module.
"""

from xboing.game.components import PhysicsComponent


def test_physics_component_init():
    """Test that the PhysicsComponent initializes correctly."""
    # Test with default values
    physics = PhysicsComponent((10, 20))
    assert physics.position == (10, 20)
    assert physics.velocity == (0, 0)
    assert physics.acceleration == (0, 0)
    assert physics.mass == 1.0

    # Test with custom values
    physics = PhysicsComponent((10, 20), (1, 2), (0.1, 0.2), 2.0)
    assert physics.position == (10, 20)
    assert physics.velocity == (1, 2)
    assert physics.acceleration == (0.1, 0.2)
    assert physics.mass == 2.0


def test_physics_component_update():
    """Test that the PhysicsComponent updates correctly."""
    # Test with no velocity or acceleration
    physics = PhysicsComponent((10, 20))
    new_pos = physics.update(16.67)  # 1 frame at 60 FPS
    assert new_pos == (10, 20)
    assert physics.position == (10, 20)

    # Test with velocity but no acceleration
    physics = PhysicsComponent((10, 20), (5, 10))
    new_pos = physics.update(16.67)  # 1 frame at 60 FPS
    assert new_pos == (15, 30)
    assert physics.position == (15, 30)

    # Test with velocity and acceleration
    physics = PhysicsComponent((10, 20), (5, 10), (1, 2))
    new_pos = physics.update(16.67)  # 1 frame at 60 FPS
    assert new_pos == (15, 30)  # Position updated based on original velocity
    assert physics.position == (15, 30)
    assert physics.velocity == (6, 12)  # Velocity increased by acceleration

    # Test with a smaller time delta
    physics = PhysicsComponent((10, 20), (5, 10), (1, 2))
    new_pos = physics.update(8.335)  # 0.5 frame at 60 FPS
    assert new_pos == (12.5, 25)  # Position updated based on original velocity
    assert physics.position == (12.5, 25)
    assert physics.velocity == (5.5, 11)  # Velocity increased by acceleration * 0.5


def test_physics_component_apply_force():
    """Test that the PhysicsComponent applies forces correctly."""
    # Test with default mass
    physics = PhysicsComponent((10, 20))
    physics.apply_force((10, 20))
    assert physics.acceleration == (10, 20)

    # Test with custom mass
    physics = PhysicsComponent((10, 20), mass=2.0)
    physics.apply_force((10, 20))
    assert physics.acceleration == (5, 10)  # Force divided by mass

    # Test applying multiple forces
    physics = PhysicsComponent((10, 20))
    physics.apply_force((10, 20))
    physics.apply_force((5, 10))
    assert physics.acceleration == (15, 30)  # Forces accumulate


def test_physics_component_setters_getters():
    """Test the setter and getter methods of PhysicsComponent."""
    physics = PhysicsComponent((10, 20))

    # Test position setter/getter
    physics.set_position((30, 40))
    assert physics.get_position() == (30, 40)
    assert physics.position == (30, 40)

    # Test velocity setter/getter
    physics.set_velocity((5, 10))
    assert physics.get_velocity() == (5, 10)
    assert physics.velocity == (5, 10)

    # Test acceleration setter/getter
    physics.set_acceleration((1, 2))
    assert physics.get_acceleration() == (1, 2)
    assert physics.acceleration == (1, 2)
