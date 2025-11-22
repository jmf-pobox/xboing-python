"""Paddle input controller for handling paddle movement via keyboard and mouse.

This module defines the PaddleInputController class, which is responsible for
handling paddle movement input via keyboard and mouse, including support for
reverse controls.
"""

from typing import Optional

import pygame

from xboing.engine.input import InputManager
from xboing.game.paddle import Paddle
from xboing.layout.game_layout import GameLayout


class PaddleInputController:
    """Controller for handling paddle movement input."""

    def __init__(
        self, paddle: Paddle, input_manager: InputManager, layout: GameLayout
    ) -> None:
        """Initialize the paddle input controller.

        Args:
            paddle: The paddle to control.
            input_manager: The input manager for getting input state.
            layout: The game layout for getting play area dimensions.

        """
        self.paddle = paddle
        self.input_manager = input_manager
        self.layout = layout
        self.reverse = False
        self._last_mouse_x: Optional[int] = None

    def handle_keyboard_movement(self, delta_ms: float) -> None:
        """Handle paddle movement via keyboard.

        Args:
            delta_ms: Time elapsed since last update in milliseconds.

        """
        paddle_direction = 0
        # Support both arrow keys and j/l keys for left/right
        left_keys = [pygame.K_LEFT, pygame.K_j]
        right_keys = [pygame.K_RIGHT, pygame.K_l]
        left_pressed = any(self.input_manager.is_key_pressed(k) for k in left_keys)
        right_pressed = any(self.input_manager.is_key_pressed(k) for k in right_keys)

        if self.reverse:
            if left_pressed:
                paddle_direction = 1
            elif right_pressed:
                paddle_direction = -1
        elif left_pressed:
            paddle_direction = -1
        elif right_pressed:
            paddle_direction = 1

        play_rect = self.layout.get_play_rect()
        self.paddle.set_direction(paddle_direction)
        self.paddle.update(delta_ms, play_rect.width, play_rect.x)

    def handle_mouse_movement(self) -> None:
        """Handle paddle movement via mouse."""
        play_rect = self.layout.get_play_rect()
        mouse_pos = self.input_manager.get_mouse_position()
        mouse_x = mouse_pos[0]

        if self._last_mouse_x is not None and self._last_mouse_x != mouse_x:
            if self.reverse:
                center_x = play_rect.x + play_rect.width // 2
                mirrored_x = 2 * center_x - mouse_x
                local_x = mirrored_x - play_rect.x - self.paddle.width // 2
            else:
                local_x = mouse_x - play_rect.x - self.paddle.width // 2
            self.paddle.move_to(local_x, play_rect.width, play_rect.x)

        self._last_mouse_x = mouse_x

    def update(self, delta_ms: float) -> None:
        """Update paddle position based on input.

        Args:
            delta_ms: Time elapsed since last update in milliseconds.

        """
        self.handle_keyboard_movement(delta_ms)
        self.handle_mouse_movement()

    def set_reverse(self, value: bool) -> None:
        """Set the reverse paddle control state.

        Args:
            value: The new reverse state.

        """
        self.reverse = value

    def get_last_mouse_x(self) -> Optional[int]:
        """Get the last mouse x position.

        Returns:
            The last mouse x position, or None if no mouse movement has been detected.

        """
        return self._last_mouse_x

    def set_last_mouse_x(self, value: Optional[int]) -> None:
        """Set the last mouse x position.

        Args:
            value: The new last mouse x position.

        """
        self._last_mouse_x = value
