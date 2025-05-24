from unittest.mock import create_autospec

from xboing.controllers.level_complete_controller import LevelCompleteController
from xboing.ui.ui_manager import UIManager


class Dummy:
    def __getattr__(self, name):
        """Return a dummy callable for any attribute access (test stub)."""
        return lambda *args, **kwargs: None


def test_level_complete_controller_instantiation_and_methods():
    # Provide all required arguments as dummies/mocks
    game_state = Dummy()
    level_manager = Dummy()
    balls = []
    game_controller = Dummy()
    ui_manager = create_autospec(UIManager)
    game_view = Dummy()
    layout = Dummy()
    controller = LevelCompleteController(
        balls,
        ui_manager,
        game_view,
        layout,
        game_state,
        game_controller,
        level_manager,
        on_advance_callback=None,
    )
    # Should not raise
    controller.handle_events([])
    controller.update(0.016)
