from typing import Any, Callable, Optional

import pygame
from injector import inject

from .base_controller import BaseController


class InstructionsController(BaseController):
    """
    Handles input and transitions for the InstructionsView.
    Handles spacebar to exit instructions, and global controls via BaseController.
    """

    @inject
    def __init__(
        self,
        on_exit_callback: Optional[Callable[..., None]] = None,
        audio_manager: Any = None,
        quit_callback: Optional[Callable[..., None]] = None,
        ui_manager: Any = None,
    ):
        super().__init__(
            audio_manager=audio_manager,
            quit_callback=quit_callback,
            ui_manager=ui_manager,
        )
        self.on_exit_callback = on_exit_callback

    def handle_events(self, events):
        """Handle input/events for instructions view and global controls."""
        super().handle_events(events)
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.logger.debug(
                    "Spacebar pressed on InstructionsView. Exiting instructions."
                )
                if self.on_exit_callback:
                    self.on_exit_callback()

    def update(self, delta_time):
        """Update logic for instructions view (usually minimal)."""
        pass

    def handle_event(self, event):
        pass  # No EventBus events handled yet, but protocol is implemented for future use
