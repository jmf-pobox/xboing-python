"""Tests for the enhanced CollisionSystem."""

from enum import Enum
from typing import Any, Tuple

import pygame
import pytest

from xboing.game.collision import CollisionSystem


class CollisionType(Enum):
    """Types of collidable objects in the game."""

    BALL = "ball"
    BULLET = "bullet"
    BLOCK = "block"
    PADDLE = "paddle"
    WALL = "wall"


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
        # Add attributes needed for collision tests
        self.radius = max(self.width, self.height) // 2
        self.vy = 1.0  # Default to moving downward

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

    def get_position(self) -> Tuple[float, float]:
        """Get the object's current position as (x, y)."""
        return (self.x, self.y)

    def set_position(self, x: float, y: float) -> None:
        """Set the object's position to (x, y)."""
        self.x = x
        self.y = y
        self.rect.x = int(x)
        self.rect.y = int(y)


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


def test_collision_system_initialization(collision_system: CollisionSystem) -> None:
    """Test CollisionSystem initialization."""
    assert collision_system.collidables == []
    assert collision_system.screen_width == 0
    assert collision_system.screen_height == 0


def test_add_collidable(
    collision_system: CollisionSystem, mock_ball: MockCollidable
) -> None:
    """Test adding a collidable object."""
    collision_system.add_collidable(mock_ball)
    assert mock_ball in collision_system.collidables
    assert len(collision_system.collidables) == 1


def test_remove_collidable(
    collision_system: CollisionSystem, mock_ball: MockCollidable
) -> None:
    """Test removing a collidable object."""
    collision_system.add_collidable(mock_ball)
    collision_system.remove_collidable(mock_ball)
    assert mock_ball not in collision_system.collidables
    assert len(collision_system.collidables) == 0


def test_check_collisions(
    collision_system: CollisionSystem,
    mock_ball: MockCollidable,
    mock_block: MockCollidable,
) -> None:
    """Test collision detection between objects."""
    collision_system.add_collidable(mock_ball)
    collision_system.add_collidable(mock_block)

    collisions = collision_system.check_collisions()
    assert len(collisions) == 1
    assert (mock_ball, mock_block) in collisions or (
        mock_block,
        mock_ball,
    ) in collisions


def test_no_collisions(
    collision_system: CollisionSystem, mock_ball: MockCollidable
) -> None:
    """Test when no collisions occur."""
    non_colliding = MockCollidable(
        collision_type=CollisionType.BLOCK,
        position=(200, 200),  # Far from mock_ball
        size=(30, 30),
    )
    collision_system.add_collidable(mock_ball)
    collision_system.add_collidable(non_colliding)

    collisions = collision_system.check_collisions()
    assert len(collisions) == 0


def test_clear_collidables(
    collision_system: CollisionSystem,
    mock_ball: MockCollidable,
    mock_block: MockCollidable,
) -> None:
    """Test clearing all collidable objects."""
    collision_system.add_collidable(mock_ball)
    collision_system.add_collidable(mock_block)
    collision_system.clear()
    assert len(collision_system.collidables) == 0


def test_get_collidables(
    collision_system: CollisionSystem,
    mock_ball: MockCollidable,
    mock_block: MockCollidable,
) -> None:
    """Test getting all collidable objects."""
    collision_system.add_collidable(mock_ball)
    collision_system.add_collidable(mock_block)
    collidables = collision_system.get_collidables()
    assert len(collidables) == 2
    assert mock_ball in collidables
    assert mock_block in collidables


def test_get_collisions_for(
    collision_system: CollisionSystem,
    mock_ball: MockCollidable,
    mock_block: MockCollidable,
) -> None:
    """Test getting collisions for a specific object."""
    collision_system.add_collidable(mock_ball)
    collision_system.add_collidable(mock_block)

    collisions = collision_system.get_collisions_for(mock_ball)
    assert len(collisions) == 1
    assert mock_block in collisions


def test_update_boundaries(collision_system: CollisionSystem) -> None:
    """Test updating screen boundaries."""
    collision_system.update_boundaries(800, 600)
    assert collision_system.screen_width == 800
    assert collision_system.screen_height == 600


def test_ball_wall_collision(collision_system: CollisionSystem) -> None:
    """Test ball-wall collision detection."""
    collision_system.update_boundaries(800, 600)
    ball = MockCollidable(
        collision_type=CollisionType.BALL,
        position=(0, 300),  # Touching left wall
        size=(20, 20),
    )

    result = collision_system.check_ball_wall_collisions(ball)
    assert result["collision"] is True
    assert result["side"] == "left"


def test_ball_paddle_collision(collision_system: CollisionSystem) -> None:
    """Test ball-paddle collision detection."""
    ball = MockCollidable(
        collision_type=CollisionType.BALL, position=(100, 100), size=(20, 20)
    )
    paddle = MockCollidable(
        collision_type=CollisionType.PADDLE, position=(90, 90), size=(100, 20)
    )

    result = collision_system.check_ball_paddle_collision(ball, paddle)
    assert result["collision"] is True
    assert -1.0 <= result["position"] <= 1.0
