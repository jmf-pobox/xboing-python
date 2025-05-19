"""Controller for handling window events and UI management in XBoing."""

import logging
from typing import Callable, List, Optional

import pygame

from xboing.controllers.controller import Controller
from xboing.engine.audio_manager import AudioManager
from xboing.ui.ui_manager import UIManager


class WindowController(Controller):
    """Handles global/system events (quit, volume, mute, etc.) and is always active.

    No longer a base class for per-view controllers.
    """

    def __init__(
        self,
        audio_manager: Optional[AudioManager] = None,
        quit_callback: Optional[Callable[[], None]] = None,
        ui_manager: Optional[UIManager] = None,
    ) -> None:
        """Initialize the WindowController.

        Args:
        ----
            audio_manager: Manager for sound effects and volume control.
            quit_callback: Function to call when quitting the game.
            ui_manager: Manager for UI views and transitions.

        """
        self.audio_manager = audio_manager
        self.quit_callback = quit_callback
        self.ui_manager = ui_manager
        self.logger = logging.getLogger(f"xboing.{self.__class__.__name__}")

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle input/events for this controller, including global controls.

        Processes global controls:
        - +/= keys: Increase volume
        - - key: Decrease volume
        - M key: Toggle mute
        - Q/Ctrl+Q/Cmd+Q: Quit game
        - Shift+/: Show instructions

        Args:
        ----
            events: List of pygame events to process.

        """
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Volume up
                if event.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    if self.audio_manager:
                        new_volume = min(1.0, self.audio_manager.get_volume() + 0.1)
                        self.audio_manager.set_volume(new_volume)
                # Volume down
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    if self.audio_manager:
                        new_volume = max(0.0, self.audio_manager.get_volume() - 0.1)
                        self.audio_manager.set_volume(new_volume)
                # Mute toggle
                elif event.key == pygame.K_m:
                    if self.audio_manager:
                        if self.audio_manager.is_muted():
                            self.audio_manager.unmute()
                        else:
                            self.audio_manager.mute()
                # Quit (Ctrl+Q or Q)
                elif event.key == pygame.K_q and (
                    event.mod & pygame.KMOD_CTRL
                    or event.mod & pygame.KMOD_META
                    or event.mod == 0
                ):
                    if self.quit_callback:
                        self.quit_callback()
                # Instructions hotkey (Shift + / for '?')
                elif (
                    event.key == pygame.K_SLASH
                    and (event.mod & pygame.KMOD_SHIFT)
                    and self.ui_manager
                ):
                    self.ui_manager.set_view("instructions")
            elif event.type == pygame.WINDOWENTER:
                pygame.mouse.set_visible(False)
            elif event.type == pygame.WINDOWLEAVE:
                pygame.mouse.set_visible(True)

    def update(self, delta_ms: float) -> None:
        """Update logic for this controller.

        This base implementation does nothing and should be overridden by subclasses
        that need to update game state or perform other actions each frame.

        Args:
        ----
            delta_time: Time elapsed since the last update in seconds.

        """
        # No-op for now

    def quit_game(self) -> None:
        """Trigger the quit callback if provided.

        Controllers should call this method instead of calling the quit_callback directly
        to ensure proper logging and consistent behavior.
        """
        self.logger.info("quit_game called from WindowController.")
        if self.quit_callback:
            self.quit_callback()
