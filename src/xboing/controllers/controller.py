"""Base controller class for XBoing, defining the controller interface."""

from typing import Protocol

import pygame


class Controller(Protocol):
    """Protocol for controllers used in the main loop."""

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle a list of Pygame events."""
        raise NotImplementedError()

    def update(self, delta_ms: float) -> None:
        """Update the controller state for the given time delta."""
        raise NotImplementedError()
