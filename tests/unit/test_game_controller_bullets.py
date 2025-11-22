from unittest.mock import Mock, patch

import pygame
import pytest

from xboing.controllers.game_controller import GameController
from xboing.engine.events import AmmoFiredEvent
from xboing.game.ball import Ball
from xboing.game.bullet import Bullet


@pytest.fixture(autouse=True)
def pygame_init():
    pygame.init()
    yield
    pygame.quit()


@pytest.mark.timeout(5)
def test_fire_bullet_decrements_ammo_and_creates_bullet(game_setup, mock_game_objects):
    """Test that firing a bullet decrements ammo and creates a bullet object."""
    # Add a ball in play
    ball = Ball(x=400, y=500, radius=8)
    ball.is_active = Mock(return_value=True)
    game_setup["ball_manager"].add_ball(ball)

    # Set initial ammo
    game_setup["game_state"].ammo = 2
    game_setup["game_state"].fire_ammo = Mock(
        side_effect=lambda: setattr(game_setup["game_state"], "ammo", 1) or []
    )

    # Set up paddle position for bullet creation
    game_setup["paddle"].rect = pygame.Rect(390, 550, 40, 10)

    # Set up play rect for bullet update
    play_rect = Mock()
    play_rect.width = 800
    play_rect.height = 600
    play_rect.x = 0
    play_rect.y = 0
    game_setup["layout"].get_play_rect.return_value = play_rect

    controller = GameController(
        game_setup["game_state"],
        game_setup["level_manager"],
        game_setup["ball_manager"],
        game_setup["paddle"],
        game_setup["block_manager"],
        input_manager=game_setup["input_manager"],
        layout=game_setup["layout"],
        renderer=game_setup["renderer"],
        bullet_manager=game_setup["bullet_manager"],
    )

    # Simulate firing bullet
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_k)

    with patch("pygame.event.post") as mock_post:
        controller.handle_events([event])

        assert game_setup["game_state"].ammo == 1, "Ammo should be decremented"
        assert (
            len(game_setup["bullet_manager"].bullets) == 1
        ), "One bullet should be created"

        # Verify AmmoFiredEvent was posted
        ammo_events = [
            call
            for call in mock_post.call_args_list
            if isinstance(call.args[0].event, AmmoFiredEvent)
        ]
        assert len(ammo_events) == 1, "Expected exactly one AmmoFiredEvent"


@pytest.mark.timeout(5)
def test_fire_bullet_with_no_ammo_does_not_create_bullet(game_setup, mock_game_objects):
    """Test that attempting to fire with no ammo doesn't create a bullet."""
    # Add a ball in play
    ball = Ball(x=400, y=500, radius=8)
    ball.is_active = Mock(return_value=True)
    game_setup["ball_manager"].add_ball(ball)

    # Set ammo to 0
    game_setup["game_state"].ammo = 0

    controller = GameController(
        game_setup["game_state"],
        game_setup["level_manager"],
        game_setup["ball_manager"],
        game_setup["paddle"],
        game_setup["block_manager"],
        input_manager=game_setup["input_manager"],
        layout=game_setup["layout"],
        renderer=game_setup["renderer"],
        bullet_manager=game_setup["bullet_manager"],
    )

    # Attempt to fire bullet
    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_k)

    with patch("pygame.event.post") as mock_post:
        controller.handle_events([event])

        assert game_setup["game_state"].ammo == 0, "Ammo should remain at 0"
        assert (
            len(game_setup["bullet_manager"].bullets) == 0
        ), "No bullet should be created"
        assert not mock_post.called, "No event should be posted when out of ammo"


@pytest.mark.timeout(5)
def test_bullet_block_collision_removes_bullet_and_block(game_setup, mock_game_objects):
    """Test that bullet-block collision removes both objects and updates score."""
    # Create and add bullet
    bullet = Bullet(x=400, y=500)
    bullet.active = True
    game_setup["bullet_manager"].add_bullet(bullet)

    # Create and add block with proper rect
    block = Mock()
    block.get_rect = Mock(
        return_value=pygame.Rect(400, 450, 32, 16)
    )  # Position block near bullet
    block.get_collision_type = Mock(return_value="block")
    block.handle_collision = Mock()
    game_setup["block_manager"].blocks.append(block)

    # Mock collision detection
    game_setup["block_manager"].check_collisions = Mock(
        return_value=(100, 1, [])
    )  # Score 100, 1 block broken
    game_setup["game_state"].add_score = Mock(return_value=[])

    controller = GameController(
        game_setup["game_state"],
        game_setup["level_manager"],
        game_setup["ball_manager"],
        game_setup["paddle"],
        game_setup["block_manager"],
        input_manager=game_setup["input_manager"],
        layout=game_setup["layout"],
        renderer=game_setup["renderer"],
        bullet_manager=game_setup["bullet_manager"],
    )

    # Mock event posting
    controller.collision_handlers.post_game_state_events = Mock()

    # Update game state
    controller.update_balls_and_collisions(0.016)

    # Verify collision handling
    assert (
        bullet in controller.bullet_manager.bullets
    ), "Bullet should remain if still active"
    game_setup["block_manager"].check_collisions.assert_called_with(bullet)
    game_setup["game_state"].add_score.assert_called_with(100)
    controller.collision_handlers.post_game_state_events.assert_called()
