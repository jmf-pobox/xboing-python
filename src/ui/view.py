"""
Protocol definition for all content views in the XBoing UI system.
Defines the required interface for any view managed by UIManager.
"""

from typing import Protocol

import pygame


class View(Protocol):
    """
    Protocol for content views managed by UIManager.
    Requires draw, handle_event, activate, and deactivate methods.
    """

    def draw(self, surface: pygame.Surface) -> None: ...
    def handle_event(self, event: pygame.event.Event) -> None: ...
    def activate(self) -> None: ...
    def deactivate(self) -> None: ...
