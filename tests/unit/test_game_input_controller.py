"""Tests for the GameInputController class."""

from unittest.mock import Mock

import pygame
import pytest

from xboing.controllers.game_input_controller import GameInputController
from xboing.engine.events import (
    AmmoFiredEvent,
    ApplauseEvent,
    BallLostEvent,
    BallShotEvent,
    LevelCompleteEvent,
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
def mock_game_state():
    """Create a mock game state for testing."""
    game_state = Mock(spec=GameState)
    game_state.ammo = 5
    game_state.fire_ammo.return_value = []
    level_state = Mock()
    level_state.get_bonus_time.return_value = 120
    game_state.level_state = level_state
    game_state.set_timer.return_value = []
    return game_state


@pytest.fixture
def mock_level_manager():
    """Create a mock level manager for testing."""
    level_manager = Mock(spec=LevelManager)
    level_manager.get_level_info.return_value = {"title": "Test Level"}
    return level_manager


@pytest.fixture
def mock_ball_manager():
    """Create a mock ball manager for testing."""
    ball_manager = Mock(spec=BallManager)
    ball_manager.has_ball_in_play.return_value = False
    ball = Mock()
    ball.stuck_to_paddle = True
    ball_manager.balls = [ball]
    return ball_manager


@pytest.fixture
def mock_paddle():
    """Create a mock paddle for testing."""
    paddle = Mock(spec=Paddle)
    paddle.rect.centerx = 400
    paddle.rect.top = 500
    return paddle


@pytest.fixture
def mock_block_manager():
    """Create a mock block manager for testing."""
    block_manager = Mock(spec=BlockManager)
    block_manager.blocks = []
    return block_manager


@pytest.fixture
def mock_bullet_manager():
    """Create a mock bullet manager for testing."""
    bullet_manager = Mock(spec=BulletManager)
    return bullet_manager


@pytest.fixture
def mock_input_manager():
    """Create a mock input manager for testing."""
    input_manager = Mock(spec=InputManager)
    return input_manager


@pytest.fixture
def mock_layout():
    """Create a mock layout for testing."""
    layout = Mock(spec=GameLayout)
    return layout


@pytest.fixture
def controller(
    mock_game_state,
    mock_level_manager,
    mock_ball_manager,
    mock_paddle,
    mock_block_manager,
    mock_bullet_manager,
    mock_input_manager,
    mock_layout,
):
    """Create a GameInputController for testing."""
    return GameInputController(
        mock_game_state,
        mock_level_manager,
        mock_ball_manager,
        mock_paddle,
        mock_block_manager,
        mock_bullet_manager,
        mock_input_manager,
        mock_layout,
    )


def test_initialization(
    controller,
    mock_game_state,
    mock_level_manager,
    mock_ball_manager,
    mock_paddle,
    mock_block_manager,
    mock_bullet_manager,
    mock_input_manager,
    mock_layout,
):
    """Test that the controller is initialized correctly."""
    assert controller.game_state == mock_game_state
    assert controller.level_manager == mock_level_manager
    assert controller.ball_manager == mock_ball_manager
    assert controller.paddle == mock_paddle
    assert controller.block_manager == mock_block_manager
    assert controller.bullet_manager == mock_bullet_manager
    assert controller.input_manager == mock_input_manager
    assert controller.layout == mock_layout
    assert controller.paused is False
    assert controller.stuck_ball_timer == 0.0
    assert controller.ball_auto_active_delay_ms == 3000.0


def test_handle_events_quit(controller):
    """Test handling quit event."""
    # Create a quit event
    quit_event = Mock()
    quit_event.type = pygame.QUIT

    # Call the method
    events = controller.handle_events([quit_event])

    # Verify a quit event was returned
    assert len(events) == 1
    assert events[0].type == pygame.QUIT


def test_handle_events_q_key(controller):
    """Test handling Q key event."""
    # Create a Q key event
    q_key_event = Mock()
    q_key_event.type = pygame.KEYDOWN
    q_key_event.key = pygame.K_q

    # Call the method
    events = controller.handle_events([q_key_event])

    # Verify a quit event was returned
    assert len(events) == 1
    assert events[0].type == pygame.QUIT


def test_handle_events_p_key(controller):
    """Test handling P key event."""
    # Create a P key event
    p_key_event = Mock()
    p_key_event.type = pygame.KEYDOWN
    p_key_event.key = pygame.K_p

    # Call the method
    controller.handle_events([p_key_event])

    # Verify paused state was toggled
    assert controller.paused is True

    # Toggle back
    controller.handle_events([p_key_event])
    assert controller.paused is False


def test_handle_events_k_key_with_ball_in_play(
    controller, mock_ball_manager, mock_game_state, mock_bullet_manager
):
    """Test handling K key event with ball in play."""
    # Set up ball manager to have a ball in play
    mock_ball_manager.has_ball_in_play.return_value = True

    # Create a K key event
    k_key_event = Mock()
    k_key_event.type = pygame.KEYDOWN
    k_key_event.key = pygame.K_k

    # Call the method
    events = controller.handle_events([k_key_event])

    # Verify ammo was fired and bullet was created
    mock_game_state.fire_ammo.assert_called_once()
    mock_bullet_manager.add_bullet.assert_called_once()

    # Verify AmmoFiredEvent was returned
    assert any(isinstance(getattr(e, "event", None), AmmoFiredEvent) for e in events)


def test_handle_events_k_key_without_ball_in_play(
    controller, mock_ball_manager, mock_game_state
):
    """Test handling K key event without ball in play."""
    # Set up ball manager to not have a ball in play
    mock_ball_manager.has_ball_in_play.return_value = False

    # Create a K key event
    k_key_event = Mock()
    k_key_event.type = pygame.KEYDOWN
    k_key_event.key = pygame.K_k

    # Call the method
    events = controller.handle_events([k_key_event])

    # Verify balls were released
    for ball in mock_ball_manager.balls:
        ball.release_from_paddle.assert_called_once()

    # Verify timer was set and BallShotEvent was returned
    mock_game_state.set_timer.assert_called_once()
    assert any(isinstance(getattr(e, "event", None), BallShotEvent) for e in events)


def test_handle_events_mouse_button(controller, mock_ball_manager, mock_game_state):
    """Test handling mouse button event."""
    # Set up ball manager to not have a ball in play
    mock_ball_manager.has_ball_in_play.return_value = False

    # Create a mouse button event
    mouse_event = Mock()
    mouse_event.type = pygame.MOUSEBUTTONDOWN

    # Call the method
    events = controller.handle_events([mouse_event])

    # Verify balls were released
    for ball in mock_ball_manager.balls:
        ball.release_from_paddle.assert_called_once()

    # Verify timer was set and BallShotEvent was returned
    mock_game_state.set_timer.assert_called_once()
    assert any(isinstance(getattr(e, "event", None), BallShotEvent) for e in events)


def test_handle_events_ball_lost(controller):
    """Test handling BallLostEvent."""
    # Create a BallLostEvent
    ball_lost_event = Mock()
    ball_lost_event.type = pygame.USEREVENT
    ball_lost_event.event = BallLostEvent()

    # Call the method
    events = controller.handle_events([ball_lost_event])

    # Verify BallLostEvent is not returned (to avoid duplicate sound effects)
    # The event is already in the event queue and will be handled by GameController
    assert len(events) == 0


def test_handle_debug_keys_x_key(
    controller, mock_input_manager, mock_block_manager, mock_game_state
):
    """Test handling X key for debug."""
    # Set up input manager to return X key pressed
    mock_input_manager.is_key_pressed.side_effect = lambda k: k == pygame.K_x

    # Add a block to the block manager
    block = Mock()
    mock_block_manager.blocks = [block]

    # Call the method
    events = controller.handle_debug_keys()

    # Verify block was hit and blocks were cleared
    block.hit.assert_called_once()
    assert mock_block_manager.blocks == []

    # Verify level complete was set and events were returned
    mock_game_state.level_state.set_level_complete.assert_called_once()
    assert len(events) == 2
    assert any(
        isinstance(getattr(e, "event", None), LevelCompleteEvent) for e in events
    )
    assert any(isinstance(getattr(e, "event", None), ApplauseEvent) for e in events)


def test_update_stuck_ball_timer_no_stuck_balls(controller, mock_ball_manager):
    """Test updating stuck ball timer with no stuck balls."""
    # Set up ball manager to have no stuck balls
    ball = Mock()
    ball.stuck_to_paddle = False
    mock_ball_manager.balls = [ball]

    # Call the method
    events = controller.update_stuck_ball_timer(16.67)

    # Verify timer was reset and no events were returned
    assert controller.stuck_ball_timer == 0.0
    assert len(events) == 0


def test_update_stuck_ball_timer_with_stuck_balls(controller, mock_ball_manager):
    """Test updating stuck ball timer with stuck balls."""
    # Set up ball manager to have stuck balls
    ball = Mock()
    ball.stuck_to_paddle = True
    mock_ball_manager.balls = [ball]

    # Set timer to just below threshold
    controller.stuck_ball_timer = controller.ball_auto_active_delay_ms - 10

    # Call the method
    events = controller.update_stuck_ball_timer(16.67)

    # Verify timer was incremented past threshold and balls were released
    ball.release_from_paddle.assert_called_once()

    # Verify timer was reset after release
    assert controller.stuck_ball_timer == 0.0

    # Verify BallShotEvent was returned
    assert len(events) == 1
    assert isinstance(events[0].event, BallShotEvent)


def test_is_paused(controller):
    """Test checking if game is paused."""
    assert controller.is_paused() is False

    controller.paused = True
    assert controller.is_paused() is True

    controller.paused = False
    assert controller.is_paused() is False
