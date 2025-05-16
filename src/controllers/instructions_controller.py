from typing import Any, Callable, Optional

import pygame
from injector import inject


class InstructionsController:
    """
    Handles input and transitions for the InstructionsView.
    Handles spacebar to exit instructions.
    """

    @inject
    def __init__(
        self,
        on_exit_callback: Optional[Callable[..., None]] = None,
        audio_manager: Any = None,
        quit_callback: Optional[Callable[..., None]] = None,
        ui_manager: Any = None,
    ):
        self.on_exit_callback = on_exit_callback

    def handle_events(self, events):
        """Handle input/events for instructions view and global controls."""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.on_exit_callback:
                    self.on_exit_callback()

    def update(self, delta_time):
        """Update logic for instructions view (usually minimal)."""
        pass

    def handle_event(self, event):
        pass  # No EventBus events handled yet, but protocol is implemented for future use
