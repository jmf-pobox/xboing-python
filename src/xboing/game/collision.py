"""Collision system for game objects in XBoing Python.

This module defines a reusable collision system that can detect and resolve
collisions between game objects. The system is designed to be used across
different games and provides a centralized way to handle collisions.
"""

from enum import Enum
import logging
from typing import Any, Callable, Dict, List, Tuple

from xboing.game.protocols import Collidable


class CollisionType(Enum):
    """Types of collidable objects in the game."""

    BALL = "ball"
    BULLET = "bullet"
    BLOCK = "block"
    PADDLE = "paddle"
    WALL = "wall"


class CollisionSystem:
    """System for detecting and resolving collisions between game objects."""

    def __init__(self, screen_width: int = 0, screen_height: int = 0) -> None:
        """
        Initialize the collision system.

        Args:
            screen_width: Screen width for boundary checks. Defaults to 0.
            screen_height: Screen height for boundary checks. Defaults to 0.

        """
        self.logger = logging.getLogger("xboing.CollisionSystem")
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.collidables: List[Collidable] = []
        self.collision_handlers: Dict[Tuple[str, str], Callable[[Any, Any], None]] = {}
        self.logger.info(f"CollisionSystem initialized: {screen_width}x{screen_height}")

    def update_boundaries(self, width: int, height: int) -> None:
        """
        Update the screen boundaries.

        Args:
            width: New screen width.
            height: New screen height.

        """
        self.screen_width = width
        self.screen_height = height

    def add_collidable(self, collidable: Collidable) -> None:
        """
        Add a collidable object to the system.

        Args:
            collidable: The collidable object to add.

        """
        if collidable not in self.collidables:
            self.collidables.append(collidable)

    def remove_collidable(self, collidable: Collidable) -> None:
        """
        Remove a collidable object from the system.

        Args:
            collidable: The collidable object to remove.

        """
        if collidable in self.collidables:
            self.collidables.remove(collidable)

    def register_collision_handler(
        self, type1: str, type2: str, handler: Callable[[Any, Any], None]
    ) -> None:
        """
        Register a handler for specific collision types.

        Args:
            type1: First collision type.
            type2: Second collision type.
            handler: Function to handle the collision.

        """
        key = (type1, type2)
        self.collision_handlers[key] = handler
        self.logger.debug(f"Registered collision handler for {type1}-{type2}")

    def handle_collision(self, obj1: Collidable, obj2: Collidable) -> None:
        """
        Handle collision between two objects using registered handlers.

        Args:
            obj1: First colliding object.
            obj2: Second colliding object.

        """
        type1 = obj1.get_collision_type()
        type2 = obj2.get_collision_type()

        # Try both orderings of the collision types, but only call one handler per pair
        handler = self.collision_handlers.get((type1, type2))
        if handler:
            handler(obj1, obj2)
        else:
            handler = self.collision_handlers.get((type2, type1))
            if handler:
                handler(obj2, obj1)

    def check_collisions(self) -> List[Tuple[Collidable, Collidable]]:
        """
        Check for collisions between all collidable objects.

        This method checks each pair of collidable objects exactly once
        to avoid duplicate collision detection.

        Returns:
            A list of pairs of colliding objects.

        """
        collisions: List[Tuple[Collidable, Collidable]] = []
        for i, obj1 in enumerate(self.collidables):
            for obj2 in self.collidables[i + 1 :]:
                if obj1.collides_with(obj2):
                    collisions.append((obj1, obj2))
                    self.handle_collision(obj1, obj2)
        return collisions

    def clear(self) -> None:
        """Remove all collidable objects from the system."""
        self.collidables.clear()

    def get_collidables(self) -> List[Collidable]:
        """
        Get all collidable objects in the system.

        Returns:
            A list of all collidable objects.

        """
        return self.collidables.copy()

    def get_collisions_for(self, collidable: Collidable) -> List[Collidable]:
        """
        Get all objects that collide with the given collidable.

        Args:
            collidable: The collidable object to check collisions for.

        Returns:
            A list of collidable objects that collide with the given object.

        """
        if collidable not in self.collidables:
            return []

        collisions: List[Collidable] = []
        for other in self.collidables:
            if other is not collidable and collidable.collides_with(other):
                collisions.append(other)
                self.handle_collision(collidable, other)

        return collisions

    def check_ball_wall_collisions(self, ball: Any) -> Dict[str, Any]:
        """Check and handle collisions between a ball and the walls.

        Args:
        ----
            ball (Ball): The ball to check

        Returns:
        -------
            Dict[str, Any]: Collision information

        """
        result: Dict[str, Any] = {
            "collision": False,
            "side": None,
        }  # 'left', 'right', 'top', 'bottom'

        # Get ball position and size
        x, y = ball.get_position()
        radius = ball.radius

        # Check the left wall
        if x - radius < 0:
            result["collision"] = True
            result["side"] = "left"
            self.logger.info("Ball collided with left wall.")
            return result

        # Check the right wall
        if x + radius > self.screen_width:
            result["collision"] = True
            result["side"] = "right"
            self.logger.info("Ball collided with right wall.")
            return result

        # Check the top wall
        if y - radius < 0:
            result["collision"] = True
            result["side"] = "top"
            self.logger.info("Ball collided with top wall.")
            return result

        # Check the bottom (ball lost)
        if y + radius > self.screen_height:
            result["collision"] = True
            result["side"] = "bottom"
            self.logger.info("Ball collided with bottom wall (lost).")
            return result

        return result

    def check_ball_paddle_collision(self, ball: Any, paddle: Any) -> Dict[str, Any]:
        """Check and handle collisions between a ball and the paddle.

        Args:
        ----
            ball (Ball): The ball to check
            paddle (Paddle): The paddle to check against

        Returns:
        -------
            Dict[str, Any]: Collision information

        """
        result: Dict[str, Any] = {
            "collision": False,
            "position": 0.0,
        }  # -1.0 (left) to 1.0 (right)

        # Simple rectangle collision check
        if not ball.get_rect().colliderect(paddle.get_rect()):
            return result

        # If we're moving upward, ignore the collision (already bounced)
        if ball.vy < 0:
            return result

        # Calculate where the ball hit the paddle
        paddle_center = paddle.get_rect().centerx
        hit_pos = ball.x

        # Normalize position (-1.0 to 1.0)
        offset = (hit_pos - paddle_center) / (paddle.get_rect().width / 2)

        result["collision"] = True
        result["position"] = offset
        self.logger.info(f"Ball collided with paddle at offset {offset:.2f}")

        return result


def get_circle_rect_collision_normal(
    circle_x: float,
    circle_y: float,
    prev_x: float,
    prev_y: float,
    rect: Any,
) -> Tuple[int, int]:
    """Calculate the collision normal vector for a circle-rectangle collision.

    Args:
    ----
        circle_x (float): Current circle center X coordinate
        circle_y (float): Current circle center Y coordinate
        prev_x (float): Previous circle center X coordinate
        prev_y (float): Previous circle center Y coordinate
        rect (pygame.Rect): Rectangle involved in the collision

    Returns:
    -------
        tuple: (nx, ny) normalized collision normal vector

    """
    # Default to a vertical collision if we can't determine
    nx, ny = 0, -1

    # Movement vector
    dx = circle_x - prev_x
    dy = circle_y - prev_y

    # Rectangle center
    rect_cx = rect.centerx
    rect_cy = rect.centery

    # Determine which side was hit by projecting the movement vector
    # and checking distances from rectangle sides

    # If moving mostly horizontally
    if abs(dx) > abs(dy):
        if dx > 0 and circle_x < rect.left:
            nx, ny = -1, 0  # Hit from the left
        elif dx < 0 and circle_x > rect.right:
            nx, ny = 1, 0  # Hit from the right
        # Vertical collision
        elif circle_y < rect_cy:
            nx, ny = 0, -1  # Hit from the top
        else:
            nx, ny = 0, 1  # Hit from the bottom
    # Moving mostly vertically
    elif dy > 0 and circle_y < rect.top:
        nx, ny = 0, -1  # Hit from the top
    elif dy < 0 and circle_y > rect.bottom:
        nx, ny = 0, 1  # Hit from the bottom
    # Horizontal collision
    elif circle_x < rect_cx:
        nx, ny = -1, 0  # Hit from the left
    else:
        nx, ny = 1, 0  # Hit from the right

    return nx, ny


def check_circle_rect_collision(
    circle_x: float, circle_y: float, circle_radius: float, rect: Any
) -> bool:
    """Check collision between a circle and a rectangle.

    Args:
    ----
        circle_x (float): Circle center X coordinate
        circle_y (float): Circle center Y coordinate
        circle_radius (float): Circle radius
        rect (pygame.Rect): Rectangle to check against

    Returns:
    -------
        bool: True if collision occurred, False otherwise

    """
    # Find the closest point in the rectangle to the center of the circle
    closest_x = max(rect.left, min(circle_x, rect.right))
    closest_y = max(rect.top, min(circle_y, rect.bottom))

    # Calculate the distance between the circle's center and the closest point
    distance_x = circle_x - closest_x
    distance_y = circle_y - closest_y

    # If the distance is less than the circle's radius, an intersection occurs
    distance_squared = (distance_x * distance_x) + (distance_y * distance_y)
    return bool(distance_squared < (circle_radius * circle_radius))
