"""Tests for the PaddleInputController class."""

from unittest.mock import Mock

import pygame
import pytest

from xboing.controllers.paddle_input_controller import PaddleInputController
from xboing.engine.input import InputManager
from xboing.game.paddle import Paddle
from xboing.layout.game_layout import GameLayout


@pytest.fixture
def mock_paddle():
    """Create a mock paddle for testing."""
    paddle = Mock(spec=Paddle)
    paddle.width = 80
    return paddle


@pytest.fixture
def mock_input_manager():
    """Create a mock input manager for testing."""
    input_manager = Mock(spec=InputManager)
    return input_manager


@pytest.fixture
def mock_layout():
    """Create a mock layout for testing."""
    layout = Mock(spec=GameLayout)
    play_rect = Mock()
    play_rect.x = 0
    play_rect.width = 800
    layout.get_play_rect.return_value = play_rect
    return layout


@pytest.fixture
def controller(mock_paddle, mock_input_manager, mock_layout):
    """Create a PaddleInputController for testing."""
    return PaddleInputController(mock_paddle, mock_input_manager, mock_layout)


def test_initialization(controller, mock_paddle, mock_input_manager, mock_layout):
    """Test that the controller is initialized correctly."""
    assert controller.paddle == mock_paddle
    assert controller.input_manager == mock_input_manager
    assert controller.layout == mock_layout
    assert controller.reverse is False
    assert controller._last_mouse_x is None


def test_handle_keyboard_movement_left(controller, mock_input_manager, mock_paddle):
    """Test handling keyboard movement with left key pressed."""
    # Set up input manager to return left key pressed
    mock_input_manager.is_key_pressed.side_effect = lambda k: k in [
        pygame.K_LEFT,
        pygame.K_j,
    ]

    # Call the method
    controller.handle_keyboard_movement(16.67)

    # Verify paddle direction was set to left (-1)
    mock_paddle.set_direction.assert_called_with(-1)
    mock_paddle.update.assert_called_once()


def test_handle_keyboard_movement_right(controller, mock_input_manager, mock_paddle):
    """Test handling keyboard movement with right key pressed."""
    # Set up input manager to return right key pressed
    mock_input_manager.is_key_pressed.side_effect = lambda k: k in [
        pygame.K_RIGHT,
        pygame.K_l,
    ]

    # Call the method
    controller.handle_keyboard_movement(16.67)

    # Verify paddle direction was set to right (1)
    mock_paddle.set_direction.assert_called_with(1)
    mock_paddle.update.assert_called_once()


def test_handle_keyboard_movement_reverse(controller, mock_input_manager, mock_paddle):
    """Test handling keyboard movement with reverse controls."""
    # Set up input manager to return left key pressed
    mock_input_manager.is_key_pressed.side_effect = lambda k: k in [
        pygame.K_LEFT,
        pygame.K_j,
    ]

    # Set reverse to True
    controller.reverse = True

    # Call the method
    controller.handle_keyboard_movement(16.67)

    # Verify paddle direction was set to right (1) due to reverse
    mock_paddle.set_direction.assert_called_with(1)
    mock_paddle.update.assert_called_once()


def test_handle_mouse_movement(controller, mock_input_manager, mock_paddle):
    """Test handling mouse movement."""
    # Set up input manager to return mouse position
    mock_input_manager.get_mouse_position.return_value = (400, 300)

    # Set last mouse position to trigger movement
    controller._last_mouse_x = 300

    # Call the method
    controller.handle_mouse_movement()

    # Verify paddle was moved to the correct position
    mock_paddle.move_to.assert_called_once()
    assert controller._last_mouse_x == 400


def test_handle_mouse_movement_reverse(
    controller, mock_input_manager, mock_paddle, mock_layout
):
    """Test handling mouse movement with reverse controls."""
    # Set up input manager to return mouse position
    mock_input_manager.get_mouse_position.return_value = (200, 300)

    # Set last mouse position to trigger movement
    controller._last_mouse_x = 300

    # Set reverse to True
    controller.reverse = True

    # Call the method
    controller.handle_mouse_movement()

    # Verify paddle was moved to the correct position (mirrored)
    mock_paddle.move_to.assert_called_once()
    assert controller._last_mouse_x == 200


def test_update_calls_both_handlers(controller):
    """Test that update calls both keyboard and mouse handlers."""
    # Mock the handlers
    controller.handle_keyboard_movement = Mock()
    controller.handle_mouse_movement = Mock()

    # Call update
    controller.update(16.67)

    # Verify both handlers were called
    controller.handle_keyboard_movement.assert_called_with(16.67)
    controller.handle_mouse_movement.assert_called_once()


def test_set_reverse(controller):
    """Test setting the reverse state."""
    assert controller.reverse is False

    controller.set_reverse(True)
    assert controller.reverse is True

    controller.set_reverse(False)
    assert controller.reverse is False
