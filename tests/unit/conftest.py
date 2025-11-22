from unittest.mock import Mock

import pygame
import pytest

from xboing.engine.events import (
    AmmoFiredEvent,
    GameOverEvent,
    LivesChangedEvent,
)
from xboing.game.ball_manager import BallManager
from xboing.game.block_manager import BlockManager
from xboing.game.bullet_manager import BulletManager
from xboing.game.paddle import Paddle


@pytest.fixture(autouse=True)
def pygame_setup():
    """Initialize pygame for all tests."""
    pygame.init()
    pygame.display.set_mode((800, 600))  # Create a display surface
    yield
    pygame.quit()


@pytest.fixture
def mock_game_objects():
    """Provide properly initialized mock game objects for testing."""

    class MockRect:
        def __init__(self):
            self.x = 0
            self.y = 0
            self.width = 100
            self.height = 20
            self.centerx = 50
            self.centery = 10
            self.left = 0
            self.right = 100
            self.top = 0
            self.bottom = 20

    return {"rect": MockRect(), "screen_rect": pygame.Rect(0, 0, 800, 600)}


@pytest.fixture
def game_setup(mock_game_objects):
    """Set up common game objects for tests."""
    # Create game state with proper mock methods
    game_state = Mock()
    game_state.fire_ammo.return_value = [AmmoFiredEvent(ammo=1)]
    game_state.add_score.return_value = []
    game_state.lose_life.return_value = [LivesChangedEvent(0), GameOverEvent()]
    game_state.has_ball_in_play = Mock(return_value=True)

    # Create level manager
    level_manager = Mock()
    level_manager.get_level_info.return_value = {"title": "Test Level"}

    # Create paddle
    paddle = Paddle(x=400, y=550)  # Position paddle in a reasonable place
    paddle.rect = pygame.Rect(
        375, 550, 50, 15
    )  # Set paddle rect for collision detection
    paddle.get_rect = Mock(return_value=paddle.rect)
    paddle.get_collision_type = Mock(return_value="paddle")
    paddle.handle_collision = Mock()

    # Create block manager with proper mock blocks
    block_manager = BlockManager(0, 0)
    block_manager.blocks = []
    block_manager.check_collisions = Mock(return_value=(0, 0, []))

    # Create renderer
    renderer = Mock()

    # Create input manager with proper mock methods
    input_manager = Mock()
    input_manager.get_mouse_position = Mock(return_value=(15, 0))
    input_manager.get_mouse_x = Mock(return_value=15)
    input_manager.is_key_pressed = Mock(return_value=False)

    # Create layout
    layout = Mock()
    layout.get_play_rect.return_value = mock_game_objects["screen_rect"]

    # Create managers
    ball_manager = BallManager()
    bullet_manager = BulletManager()

    # Set up collision system
    collision_system = Mock()
    collision_system.check_collisions = Mock()
    collision_system.register_collision_handler = Mock()

    return {
        "game_state": game_state,
        "level_manager": level_manager,
        "paddle": paddle,
        "block_manager": block_manager,
        "renderer": renderer,
        "input_manager": input_manager,
        "layout": layout,
        "ball_manager": ball_manager,
        "bullet_manager": bullet_manager,
        "collision_system": collision_system,
    }
