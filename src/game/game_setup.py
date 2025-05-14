from game.level_manager import LevelManager
from game.paddle import Paddle
from game.sprite_block import SpriteBlockManager

# Constants (should match those in main.py)
PADDLE_WIDTH = 70
PADDLE_HEIGHT = 15


def create_game_objects(layout):
    play_rect = layout.get_play_rect()
    paddle_x = play_rect.x + (play_rect.width // 2) - (PADDLE_WIDTH // 2)
    paddle_y = play_rect.y + play_rect.height - Paddle.DIST_BASE
    paddle = Paddle(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
    balls = []
    block_manager = SpriteBlockManager(play_rect.x, play_rect.y)
    level_manager = LevelManager()
    level_manager.set_block_manager(block_manager)
    level_manager.set_layout(layout)
    level_manager.load_level(1)
    return {
        "paddle": paddle,
        "balls": balls,
        "block_manager": block_manager,
        "level_manager": level_manager,
    }
