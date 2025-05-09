"""
Collision detection system for XBoing.

This module provides a centralized collision detection system
that handles interactions between game objects.
"""



class CollisionSystem:
    """
    Manages collision detection between game objects.

    This system handles collisions between:
    - Ball and walls
    - Ball and paddle
    - Ball and blocks
    - Powerups and paddle
    """

    def __init__(self, screen_width, screen_height):
        """
        Initialize the collision system.

        Args:
            screen_width (int): Screen width for boundary checks
            screen_height (int): Screen height for boundary checks
        """
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update_boundaries(self, width, height):
        """Update the screen boundaries."""
        self.screen_width = width
        self.screen_height = height

    def check_ball_wall_collisions(self, ball):
        """
        Check and handle collisions between a ball and the walls.

        Args:
            ball (Ball): The ball to check

        Returns:
            dict: Collision information
        """
        result = {"collision": False, "side": None}  # 'left', 'right', 'top', 'bottom'

        # Get ball position and size
        x, y = ball.get_position()
        radius = ball.radius

        # Check left wall
        if x - radius < 0:
            result["collision"] = True
            result["side"] = "left"
            return result

        # Check right wall
        if x + radius > self.screen_width:
            result["collision"] = True
            result["side"] = "right"
            return result

        # Check top wall
        if y - radius < 0:
            result["collision"] = True
            result["side"] = "top"
            return result

        # Check bottom (ball lost)
        if y + radius > self.screen_height:
            result["collision"] = True
            result["side"] = "bottom"
            return result

        return result

    def check_ball_paddle_collision(self, ball, paddle):
        """
        Check and handle collisions between a ball and the paddle.

        Args:
            ball (Ball): The ball to check
            paddle (Paddle): The paddle to check against

        Returns:
            dict: Collision information
        """
        result = {"collision": False, "position": 0.0}  # -1.0 (left) to 1.0 (right)

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

        return result

    def check_circle_rect_collision(self, circle_x, circle_y, circle_radius, rect):
        """
        Check collision between a circle and a rectangle.

        Args:
            circle_x (float): Circle center X coordinate
            circle_y (float): Circle center Y coordinate
            circle_radius (float): Circle radius
            rect (pygame.Rect): Rectangle to check against

        Returns:
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
        return distance_squared < (circle_radius * circle_radius)

    def get_circle_rect_collision_normal(
        self, circle_x, circle_y, prev_x, prev_y, rect
    ):
        """
        Calculate the collision normal vector for a circle-rectangle collision.

        Args:
            circle_x (float): Current circle center X coordinate
            circle_y (float): Current circle center Y coordinate
            prev_x (float): Previous circle center X coordinate
            prev_y (float): Previous circle center Y coordinate
            rect (pygame.Rect): Rectangle involved in the collision

        Returns:
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
            else:
                # Vertical collision
                if circle_y < rect_cy:
                    nx, ny = 0, -1  # Hit from the top
                else:
                    nx, ny = 0, 1  # Hit from the bottom
        else:
            # Moving mostly vertically
            if dy > 0 and circle_y < rect.top:
                nx, ny = 0, -1  # Hit from the top
            elif dy < 0 and circle_y > rect.bottom:
                nx, ny = 0, 1  # Hit from the bottom
            else:
                # Horizontal collision
                if circle_x < rect_cx:
                    nx, ny = -1, 0  # Hit from the left
                else:
                    nx, ny = 1, 0  # Hit from the right

        return nx, ny
