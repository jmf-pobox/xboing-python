"""
Base class for all circular game objects (e.g., Ball) in XBoing Python.
Defines CircularGameShape as a subclass of GameShape.
"""

from abc import abstractmethod
from typing import Tuple

import pygame

from xboing.game.game_shape import GameShape


class CircularGameShape(GameShape):
    """
    Base class for all circular game objects (e.g., Ball) in XBoing Python.
    Defines CircularGameShape as a subclass of GameShape.
    """

    def __init__(self, x: float, y: float, radius: int) -> None:
        """Initialize the circular game shape with position and radius."""
        super().__init__(x, y, radius * 2, radius * 2)
        self.radius: int = radius
        self.update_rect()

    def update_rect(self) -> None:
        """Update the rect to be centered on (x, y) with the given radius."""
        self.rect.x = int(self.x - self.radius)
        self.rect.y = int(self.y - self.radius)
        self.rect.width = self.radius * 2
        self.rect.height = self.radius * 2

    def get_position(self) -> Tuple[float, float]:
        """Get the center position of the shape as (x, y)."""
        return (self.x, self.y)

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the circular shape on the given surface."""
        ...
