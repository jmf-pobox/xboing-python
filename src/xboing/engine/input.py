"""Input handling abstraction over SDL2/pygame.

This module provides keyboard and mouse input management,
abstracting the underlying pygame implementation.
"""

import logging
from typing import Dict, List, Optional, Sequence, Set, Tuple

import pygame


class InputManager:
    """Manages keyboard and mouse input."""

    logger = logging.getLogger("xboing.InputManager")
    MAX_MOUSE_BUTTONS = 3  # Number of supported mouse buttons (left, middle, right)

    def __init__(self) -> None:
        """Initialize the input manager."""
        # Keyboard state
        self.keys_pressed: Dict[int, bool] = {}
        self.keys_down: Set[int] = set()
        self.keys_up: Set[int] = set()

        # Mouse state
        self.mouse_pos: Tuple[int, int] = (0, 0)
        self.mouse_buttons_pressed: List[bool] = [
            False,
            False,
            False,
        ]  # Left, middle, right
        self.mouse_buttons_down: List[bool] = [False, False, False]
        self.mouse_buttons_up: List[bool] = [False, False, False]
        self.mouse_motion: Tuple[int, int] = (0, 0)

        self.key_map: Dict[int, str] = {}  # TODO: Populate with actual key mappings

    def update(self, events: Optional[Sequence[pygame.event.Event]] = None) -> bool:
        """Update input state for the current frame."""
        if events is None:
            events = pygame.event.get()
        # Clear one-frame states
        self.keys_down.clear()
        self.keys_up.clear()
        self.mouse_buttons_down = [False, False, False]
        self.mouse_buttons_up = [False, False, False]
        self.mouse_motion = (0, 0)

        # Process events
        for event in events:
            if event.type == pygame.QUIT:
                return False  # Signal to quit

            if event.type == pygame.KEYDOWN:
                self.keys_pressed[event.key] = True
                self.keys_down.add(event.key)
                try:
                    key_name = pygame.key.name(event.key)
                except Exception:
                    key_name = str(event.key)
                self.logger.debug(f"[InputManager] KEYDOWN: {event.key} ({key_name})")

            if event.type == pygame.KEYUP:
                self.keys_pressed[event.key] = False
                self.keys_up.add(event.key)
                try:
                    key_name = pygame.key.name(event.key)
                except Exception:
                    key_name = str(event.key)
                self.logger.debug(f"[InputManager] KEYUP: {event.key} ({key_name})")

            if event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                self.mouse_motion = event.rel

            if (
                event.type == pygame.MOUSEBUTTONDOWN
                and event.button <= self.MAX_MOUSE_BUTTONS
            ):
                button_idx = event.button - 1
                self.mouse_buttons_pressed[button_idx] = True
                self.mouse_buttons_down[button_idx] = True

            if (
                event.type == pygame.MOUSEBUTTONUP
                and event.button <= self.MAX_MOUSE_BUTTONS
            ):
                button_idx = event.button - 1
                self.mouse_buttons_pressed[button_idx] = False
                self.mouse_buttons_up[button_idx] = True

        return True  # Continue

    def is_key_pressed(self, key: int) -> bool:
        """Check if a key is currently pressed."""
        return self.keys_pressed.get(key, False)

    def is_key_down(self, key: int) -> bool:
        """Check if a key was pressed this frame."""
        return key in self.keys_down

    def is_key_up(self, key: int) -> bool:
        """Check if a key was released this frame."""
        return key in self.keys_up

    def get_mouse_position(self) -> Tuple[int, int]:
        """Get the current mouse position."""
        return self.mouse_pos

    def get_mouse_motion(self) -> Tuple[int, int]:
        """Get the mouse movement delta for this frame."""
        return self.mouse_motion

    def is_mouse_button_pressed(self, button: int) -> bool:
        """Check if a mouse button is currently pressed.

        Args:
        ----
            button (int): Button index (0=left, 1=middle, 2=right)

        """
        if 0 <= button < self.MAX_MOUSE_BUTTONS:
            return self.mouse_buttons_pressed[button]
        return False

    def is_mouse_button_down(self, button: int) -> bool:
        """Check if a mouse button was pressed this frame.

        Args:
        ----
            button (int): Button index (0=left, 1=middle, 2=right)

        """
        if 0 <= button < self.MAX_MOUSE_BUTTONS:
            return self.mouse_buttons_down[button]
        return False

    def is_mouse_button_up(self, button: int) -> bool:
        """Check if a mouse button was released this frame.

        Args:
        ----
            button (int): Button index (0=left, 1=middle, 2=right)

        """
        if 0 <= button < self.MAX_MOUSE_BUTTONS:
            return self.mouse_buttons_up[button]
        return False

    def get_key_name(self, key_code: int) -> str:
        """Return the name of the key for the given key code."""
        if key_code in self.key_map:
            return str(self.key_map[key_code])
        return str(key_code)
