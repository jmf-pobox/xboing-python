"""Tests for collision handlers in XBoing."""

from typing import Any, Tuple

import pygame
import pytest

from xboing.game.collision import CollisionSystem, CollisionType


class MockCollidable:
    """Mock collidable object for testing."""

    def __init__(
        self,
        collision_type: CollisionType,
        position: Tuple[float, float],
        size: Tuple[int, int],
        collides: bool = True,
    ) -> None:
        """Initialize mock collidable.

        Args:
            collision_type: Type of collidable
            position: (x, y) position
            size: (width, height) size
            collides: Whether this object should report collisions

        """
        self.collision_type = collision_type
        self.x, self.y = position
        self.width, self.height = size
        self.collides = collides
        self.collision_count = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def get_collision_type(self) -> str:
        """Get the collision type of this object."""
        return self.collision_type.value

    def get_rect(self) -> pygame.Rect:
        """Get the rectangle representing this object."""
        return self.rect

    def collides_with(self, other: Any) -> bool:
        """Check if this object collides with another."""
        if not isinstance(other, MockCollidable):
            return False
        return self.collides and other.collides and self.rect.colliderect(other.rect)

    def handle_collision(self, other: Any) -> None:
        """Handle collision with another object."""
        self.collision_count += 1


@pytest.fixture
def collision_system() -> CollisionSystem:
    """Create a CollisionSystem instance for testing."""
    return CollisionSystem()


@pytest.fixture
def mock_ball() -> MockCollidable:
    """Create a mock ball for testing."""
    return MockCollidable(
        collision_type=CollisionType.BALL, position=(100, 100), size=(20, 20)
    )


@pytest.fixture
def mock_block() -> MockCollidable:
    """Create a mock block for testing."""
    return MockCollidable(
        collision_type=CollisionType.BLOCK, position=(90, 90), size=(30, 30)
    )


def test_register_collision_handler(
    collision_system: CollisionSystem,
    mock_ball: MockCollidable,
    mock_block: MockCollidable,
) -> None:
    """Test registering a collision handler."""
    collision_count = 0

    def handler(obj1: Any, obj2: Any) -> None:
        nonlocal collision_count
        collision_count += 1

    collision_system.register_collision_handler(
        CollisionType.BALL.value, CollisionType.BLOCK.value, handler
    )

    collision_system.add_collidable(mock_ball)
    collision_system.add_collidable(mock_block)
    collision_system.check_collisions()

    assert collision_count == 1


def test_collision_handler_order(
    collision_system: CollisionSystem,
    mock_ball: MockCollidable,
    mock_block: MockCollidable,
) -> None:
    """Test that collision handlers work regardless of object order."""
    collision_count = 0

    def handler(obj1: Any, obj2: Any) -> None:
        nonlocal collision_count
        collision_count += 1

    # Register handler for BLOCK-BALL (reverse order)
    collision_system.register_collision_handler(
        CollisionType.BLOCK.value, CollisionType.BALL.value, handler
    )

    collision_system.add_collidable(mock_ball)
    collision_system.add_collidable(mock_block)
    collision_system.check_collisions()

    assert collision_count == 1


def test_multiple_collision_handlers(
    collision_system: CollisionSystem, mock_ball: MockCollidable
) -> None:
    """Test handling multiple collisions with different handlers."""
    ball_collisions = 0
    block_collisions = 0

    def ball_handler(obj1: Any, obj2: Any) -> None:
        nonlocal ball_collisions
        ball_collisions += 1

    def block_handler(obj1: Any, obj2: Any) -> None:
        nonlocal block_collisions
        block_collisions += 1

    # Create multiple blocks that all overlap with each other and the ball
    blocks = [
        MockCollidable(
            collision_type=CollisionType.BLOCK,
            position=(100, 100),  # Overlaps with ball
            size=(30, 30),
        ),
        MockCollidable(
            collision_type=CollisionType.BLOCK,
            position=(110, 110),  # Overlaps with ball and block 1
            size=(30, 30),
        ),
    ]

    # Register handlers
    collision_system.register_collision_handler(
        CollisionType.BALL.value, CollisionType.BLOCK.value, ball_handler
    )
    collision_system.register_collision_handler(
        CollisionType.BLOCK.value, CollisionType.BLOCK.value, block_handler
    )

    # Add objects
    collision_system.add_collidable(mock_ball)
    for block in blocks:
        collision_system.add_collidable(block)

    # Check collisions
    collisions = collision_system.check_collisions()

    # Verify that we detected all collisions
    assert len(collisions) == 3  # Ball-Block1, Ball-Block2, Block1-Block2
    assert ball_collisions == 2  # Ball collides with both blocks
    assert block_collisions == 1  # Blocks collide with each other


def test_no_handler_registered(
    collision_system: CollisionSystem,
    mock_ball: MockCollidable,
    mock_block: MockCollidable,
) -> None:
    """Test behavior when no handler is registered for a collision."""
    collision_system.add_collidable(mock_ball)
    collision_system.add_collidable(mock_block)

    # Should not raise any exceptions
    collision_system.check_collisions()


def test_handler_removal(
    collision_system: CollisionSystem,
    mock_ball: MockCollidable,
    mock_block: MockCollidable,
) -> None:
    """Test that handlers can be replaced by registering a new one."""
    collision_count = 0

    def handler1(obj1: Any, obj2: Any) -> None:
        nonlocal collision_count
        collision_count += 1

    def handler2(obj1: Any, obj2: Any) -> None:
        nonlocal collision_count
        collision_count += 2

    # Register first handler
    collision_system.register_collision_handler(
        CollisionType.BALL.value, CollisionType.BLOCK.value, handler1
    )

    # Register second handler (should replace first)
    collision_system.register_collision_handler(
        CollisionType.BALL.value, CollisionType.BLOCK.value, handler2
    )

    collision_system.add_collidable(mock_ball)
    collision_system.add_collidable(mock_block)
    collision_system.check_collisions()

    assert collision_count == 2  # Should use handler2
