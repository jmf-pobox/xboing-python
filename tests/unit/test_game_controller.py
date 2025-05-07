from src.controllers.game_controller import GameController
from unittest.mock import Mock

def test_game_controller_instantiation_and_methods():
    game_state = Mock()
    level_manager = Mock()
    balls = []
    paddle = Mock()
    block_manager = Mock()
    event_bus = Mock()
    controller = GameController(game_state, level_manager, balls, paddle, block_manager, event_bus)
    # Should not raise
    controller.handle_events([])
    controller.update(0.016) 