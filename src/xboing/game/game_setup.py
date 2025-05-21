"""Game setup utilities for initializing core game objects in XBoing."""

from typing import Any, Dict

from xboing.game.ball_manager import BallManager
from xboing.game.block_manager import BlockManager
from xboing.game.bullet_manager import BulletManager
from xboing.game.level_manager import LevelManager
from xboing.game.paddle import Paddle
from xboing.renderers.bullet_renderer import BulletRenderer

# Constants (should match those in xboing.py)
PADDLE_WIDTH = 70
PADDLE_HEIGHT = 15


def create_game_objects(layout: Any) -> Dict[str, Any]:
    """Create and initialize core game objects (paddle, ball manager, block manager, level manager).

    Args:
    ----
        layout: The game layout object (must have get_play_rect method)

    Returns:
    -------
        Dict[str, Any]: Dictionary of game objects

    """
    play_rect = layout.get_play_rect()
    paddle_x = play_rect.x + (play_rect.width // 2) - (PADDLE_WIDTH // 2)
    paddle_y = play_rect.y + play_rect.height - Paddle.DIST_BASE
    paddle: Paddle = Paddle(paddle_x, paddle_y)
    ball_manager: BallManager = BallManager()
    block_manager: BlockManager = BlockManager(play_rect.x, play_rect.y)
    level_manager: LevelManager = LevelManager()
    level_manager.set_block_manager(block_manager)
    level_manager.set_layout(layout)
    level_manager.load_level(1)
    bullet_manager: BulletManager = BulletManager()
    bullet_renderer: BulletRenderer = BulletRenderer()
    return {
        "paddle": paddle,
        "ball_manager": ball_manager,
        "block_manager": block_manager,
        "level_manager": level_manager,
        "bullet_manager": bullet_manager,
        "bullet_renderer": bullet_renderer,
    }
