"""Protocol definition for all content views in the XBoing UI system.

Defines the required interface for any view managed by UIManager.
"""

from typing import Protocol

import pygame


class View(Protocol):
    """Protocol for content views managed by UIManager.

    Requires draw, handle_event, activate, and deactivate methods.
    """

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the view onto the given surface."""
        raise NotImplementedError()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a single Pygame event."""
        raise NotImplementedError()

    def activate(self) -> None:
        """Activate the view."""
        raise NotImplementedError()

    def deactivate(self) -> None:
        """Deactivate the view."""
        raise NotImplementedError()
