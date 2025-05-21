"""
Base class for all game objects with a rect and position in XBoing Python.
Defines the GameShape ABC for rectangular and derived shapes.
"""

from abc import ABC, abstractmethod
from typing import Tuple

import pygame


class GameShape(ABC):
    """
    Base class for all game objects with a rect and position in XBoing Python.
    Defines the GameShape ABC for rectangular and derived shapes.
    """

    def __init__(self, x: float, y: float, width: int, height: int) -> None:
        """Initialize the game shape with position and size."""
        self.x: float = x
        self.y: float = y
        self.rect: pygame.Rect = pygame.Rect(int(self.x), int(self.y), width, height)

    def update_rect(self) -> None:
        """Update the rect position based on current x and y."""
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def get_rect(self) -> pygame.Rect:
        """Get the shape's rectangle for collision detection."""
        return self.rect

    def get_position(self) -> Tuple[float, float]:
        """Get the shape's current position as (x, y)."""
        return (self.x, self.y)

    @property
    def width(self) -> int:
        """The current width of the shape (from its rect)."""
        return self.rect.width

    @property
    def height(self) -> int:
        """The current height of the shape (from its rect)."""
        return self.rect.height

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the shape on the given surface."""
        ...
