"""
Input handling abstraction over SDL2/pygame.

This module provides keyboard and mouse input management,
abstracting the underlying pygame implementation.
"""

import logging

import pygame


class InputManager:
    """Manages keyboard and mouse input."""

    logger = logging.getLogger("xboing.InputManager")

    def __init__(self):
        """Initialize the input manager."""
        # Keyboard state
        self.keys_pressed = {}
        self.keys_down = set()
        self.keys_up = set()

        # Mouse state
        self.mouse_pos = (0, 0)
        self.mouse_buttons_pressed = [False, False, False]  # Left, middle, right
        self.mouse_buttons_down = [False, False, False]
        self.mouse_buttons_up = [False, False, False]
        self.mouse_motion = (0, 0)

    def update(self, events=None):
        """
        Update input state for the current frame.
        Should be called at the beginning of each frame.
        """
        if events is None:
            events = pygame.event.get()
        # Clear one-frame states
        self.keys_down.clear()
        self.keys_up.clear()
        self.mouse_buttons_down = [False, False, False]
        self.mouse_buttons_up = [False, False, False]
        self.mouse_motion = (0, 0)

        # Process events
        for event in events:  # Use the same events list!
            if event.type == pygame.QUIT:
                return False  # Signal to quit

            elif event.type == pygame.KEYDOWN:
                self.keys_pressed[event.key] = True
                self.keys_down.add(event.key)

            elif event.type == pygame.KEYUP:
                self.keys_pressed[event.key] = False
                self.keys_up.add(event.key)

            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
                self.mouse_motion = event.rel

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button <= 3:  # Only track main three buttons
                    button_idx = event.button - 1
                    self.mouse_buttons_pressed[button_idx] = True
                    self.mouse_buttons_down[button_idx] = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button <= 3:  # Only track main three buttons
                    button_idx = event.button - 1
                    self.mouse_buttons_pressed[button_idx] = False
                    self.mouse_buttons_up[button_idx] = True

        return True  # Continue

    def is_key_pressed(self, key):
        """Check if a key is currently pressed."""
        return self.keys_pressed.get(key, False)

    def is_key_down(self, key):
        """Check if a key was pressed this frame."""
        return key in self.keys_down

    def is_key_up(self, key):
        """Check if a key was released this frame."""
        return key in self.keys_up

    def get_mouse_position(self):
        """Get the current mouse position."""
        return self.mouse_pos

    def get_mouse_motion(self):
        """Get the mouse movement delta for this frame."""
        return self.mouse_motion

    def is_mouse_button_pressed(self, button):
        """
        Check if a mouse button is currently pressed.

        Args:
            button (int): Button index (0=left, 1=middle, 2=right)
        """
        if 0 <= button < 3:
            return self.mouse_buttons_pressed[button]
        return False

    def is_mouse_button_down(self, button):
        """
        Check if a mouse button was pressed this frame.

        Args:
            button (int): Button index (0=left, 1=middle, 2=right)
        """
        if 0 <= button < 3:
            return self.mouse_buttons_down[button]
        return False

    def is_mouse_button_up(self, button):
        """
        Check if a mouse button was released this frame.

        Args:
            button (int): Button index (0=left, 1=middle, 2=right)
        """
        if 0 <= button < 3:
            return self.mouse_buttons_up[button]
        return False
