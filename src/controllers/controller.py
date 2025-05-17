"""Base controller class for XBoing, defining the controller interface."""

from typing import List

import pygame
from typing_extensions import Protocol


class Controller(Protocol):
    """Protocol for controllers used in the main loop."""

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle a list of Pygame events."""
        raise NotImplementedError()

    def update(self, delta_ms: float) -> None:
        """Update the controller state for the given time delta."""
        raise NotImplementedError()
