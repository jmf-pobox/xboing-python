"""Controller for handling instructions view and related events in XBoing."""

from typing import Any, Callable, List, Optional

from injector import inject
import pygame

from xboing.controllers.controller import Controller
from xboing.engine.audio_manager import AudioManager
from xboing.ui.ui_manager import UIManager


class InstructionsController(Controller):
    """Handles input and transitions for the InstructionsView.

    Handles spacebar to exit instructions.
    """

    @inject
    def __init__(
        self,
        on_exit_callback: Optional[Callable[[], None]] = None,
        audio_manager: Optional[AudioManager] = None,
        quit_callback: Optional[Callable[[], None]] = None,
        ui_manager: Optional[UIManager] = None,
    ) -> None:
        """Initialize the InstructionsController.

        Args:
        ----
            on_exit_callback: Callback to exit the instructions view.
            audio_manager: The AudioManager instance (optional, for future use).
            quit_callback: Callback to quit the game (optional, for future use).
            ui_manager: The UIManager instance (optional, for future use).

        """
        self.on_exit_callback = on_exit_callback
        self.audio_manager = audio_manager
        self.quit_callback = quit_callback
        self.ui_manager = ui_manager

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle input/events for instructions view and global controls.

        Args:
        ----
            events: List of Pygame events to process.

        """
        for event in events:
            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                and self.on_exit_callback
            ):
                self.on_exit_callback()

    def update(self, delta_ms: float) -> None:
        """Update logic for instructions view (usually minimal).

        Args:
        ----
            delta_time: Time elapsed since last update in milliseconds.

        """
        # No-op for now

    def handle_event(self, event: Any) -> None:
        """Handle a single event (protocol stub for future use).

        Args:
        ----
            event: A single event object (type may vary).

        """
        # No-op for now
