"""Integration tests for GameController with input controllers."""

from unittest.mock import Mock, patch

import pygame
import pytest

from xboing.controllers.game_controller import GameController
from xboing.controllers.game_input_controller import GameInputController
from xboing.controllers.paddle_input_controller import PaddleInputController
from xboing.engine.events import (
    BallLostEvent,
    BallShotEvent,
)
from xboing.engine.input import InputManager
from xboing.game.ball_manager import BallManager
from xboing.game.block_manager import BlockManager
from xboing.game.bullet_manager import BulletManager
from xboing.game.game_state import GameState
from xboing.game.level_manager import LevelManager
from xboing.game.paddle import Paddle
from xboing.layout.game_layout import GameLayout


@pytest.fixture
def mock_game_objects():
    """Create mock game objects for testing."""
    game_state = Mock(spec=GameState)
    level_manager = Mock(spec=LevelManager)
    ball_manager = Mock(spec=BallManager)
    paddle = Mock(spec=Paddle)
    block_manager = Mock(spec=BlockManager)
    bullet_manager = Mock(spec=BulletManager)
    input_manager = Mock(spec=InputManager)
    layout = Mock(spec=GameLayout)
    renderer = Mock()

    # Set up play rect
    play_rect = Mock()
    play_rect.x = 0
    play_rect.y = 0
    play_rect.width = 800
    play_rect.height = 600
    layout.get_play_rect.return_value = play_rect

    # Set up paddle
    paddle.width = 80
    # Create a mock rect for the paddle
    paddle_rect = Mock()
    paddle_rect.centerx = 400
    paddle_rect.top = 500
    # Attach the mock rect to the paddle
    type(paddle).rect = paddle_rect

    # Set up ball_manager.balls to be a list
    ball_manager.balls = []

    # Set up block_manager.blocks to be a list
    block_manager.blocks = []

    # Set up bullet_manager.bullets to be a list
    bullet_manager.bullets = []

    # Set up input_manager.get_mouse_position to return a tuple
    input_manager.get_mouse_position.return_value = (400, 300)

    # Set up level manager
    level_manager.get_level_info.return_value = {"title": "Test Level"}

    # Set up game state
    game_state.ammo = 5
    game_state.fire_ammo.return_value = []
    level_state = Mock()
    level_state.get_bonus_time.return_value = 120
    game_state.level_state = level_state
    game_state.set_timer.return_value = []

    return {
        "game_state": game_state,
        "level_manager": level_manager,
        "ball_manager": ball_manager,
        "paddle": paddle,
        "block_manager": block_manager,
        "bullet_manager": bullet_manager,
        "input_manager": input_manager,
        "layout": layout,
        "renderer": renderer,
        "play_rect": play_rect,
    }


@pytest.fixture
def game_controller(mock_game_objects):
    """Create a GameController for testing."""
    return GameController(
        mock_game_objects["game_state"],
        mock_game_objects["level_manager"],
        mock_game_objects["ball_manager"],
        mock_game_objects["paddle"],
        mock_game_objects["block_manager"],
        mock_game_objects["input_manager"],
        mock_game_objects["layout"],
        mock_game_objects["renderer"],
        mock_game_objects["bullet_manager"],
    )


def test_game_controller_creates_input_controllers(game_controller):
    """Test that GameController creates input controllers."""
    assert isinstance(game_controller.paddle_input, PaddleInputController)
    assert isinstance(game_controller.game_input, GameInputController)


def test_game_controller_delegates_to_paddle_input(game_controller, mock_game_objects):
    """Test that GameController delegates to PaddleInputController."""
    # Mock the paddle input update method
    game_controller.paddle_input.update = Mock()

    # Call the update method
    with patch("pygame.event.post"):
        game_controller.update(16.67)

    # Verify paddle input update was called
    game_controller.paddle_input.update.assert_called_with(16.67)


def test_game_controller_delegates_to_game_input_for_events(
    game_controller, mock_game_objects
):
    """Test that GameController delegates to GameInputController for events."""
    # Mock the game input handle_events method
    game_controller.game_input.handle_events = Mock(return_value=[])

    # Create an event
    event = Mock()

    # Call the handle_events method
    game_controller.handle_events([event])

    # Verify game input handle_events was called
    game_controller.game_input.handle_events.assert_called_with([event])


def test_game_controller_delegates_to_game_input_for_debug_keys(
    game_controller, mock_game_objects
):
    """Test that GameController delegates to GameInputController for debug keys."""
    # Mock the game input handle_debug_keys method
    game_controller.game_input.handle_debug_keys = Mock(return_value=[])

    # Call the update method
    with patch("pygame.event.post"):
        game_controller.update(16.67)

    # Verify game input handle_debug_keys was called
    game_controller.game_input.handle_debug_keys.assert_called_once()


def test_game_controller_delegates_to_game_input_for_stuck_ball_timer(
    game_controller, mock_game_objects
):
    """Test that GameController delegates to GameInputController for stuck ball timer."""
    # Mock the game input update_stuck_ball_timer method
    game_controller.game_input.update_stuck_ball_timer = Mock(return_value=[])

    # Call the update method
    with patch("pygame.event.post"):
        game_controller.update(16.67)

    # Verify game input update_stuck_ball_timer was called
    game_controller.game_input.update_stuck_ball_timer.assert_called_with(16.67)


def test_game_controller_posts_events_from_game_input(
    game_controller, mock_game_objects
):
    """Test that GameController posts events from GameInputController."""
    # Create an event
    event = pygame.event.Event(pygame.USEREVENT, {"event": BallShotEvent()})

    # Mock the game input handle_events method to return the event
    game_controller.game_input.handle_events = Mock(return_value=[event])

    # Call the handle_events method
    with patch("pygame.event.post") as mock_post:
        game_controller.handle_events([Mock()])

        # Verify event was posted
        mock_post.assert_called_with(event)


def test_game_controller_handles_ball_lost_event(game_controller, mock_game_objects):
    """Test that GameController handles BallLostEvent."""
    # Create a BallLostEvent
    event = pygame.event.Event(pygame.USEREVENT, {"event": BallLostEvent()})

    # Mock the game input handle_events method to return empty list
    game_controller.game_input.handle_events = Mock(return_value=[])

    # Mock the handle_life_loss method
    game_controller.handle_life_loss = Mock()

    # Call the handle_events method with the BallLostEvent
    with patch("pygame.event.post"):
        game_controller.handle_events([event])

    # Verify handle_life_loss was called
    game_controller.handle_life_loss.assert_called_once()


def test_game_controller_checks_paused_state(game_controller, mock_game_objects):
    """Test that GameController checks paused state from GameInputController."""
    # Mock the game input is_paused method
    game_controller.game_input.is_paused = Mock(return_value=True)

    # Call the update method
    with patch("pygame.event.post"):
        game_controller.update(16.67)

    # Verify is_paused was called and early return happened (paddle_input.update not called)
    game_controller.game_input.is_paused.assert_called_once()
    assert not hasattr(game_controller.paddle_input, "update.called")


def test_game_controller_reverse_state_synced(game_controller):
    """Test that reverse state is synced between GameController and input controllers."""
    # Call toggle_reverse
    with patch("pygame.event.post"):
        game_controller.toggle_reverse()

    # Verify both controllers have reverse set
    assert game_controller.collision_handlers.reverse is True
    assert game_controller.paddle_input.reverse is True

    # Call set_reverse(False)
    with patch("pygame.event.post"):
        game_controller.set_reverse(False)

    # Verify both controllers have reverse reset
    assert game_controller.collision_handlers.reverse is False
    assert game_controller.paddle_input.reverse is False
