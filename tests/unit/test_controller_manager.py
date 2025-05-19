from unittest.mock import Mock

import pytest

from xboing.controllers.controller_manager import ControllerManager


def test_controller_manager_registration_and_switching():
    cm = ControllerManager()
    game_controller = Mock()
    instructions_controller = Mock()
    level_complete_controller = Mock()

    # Register controllers
    cm.register_controller("game", game_controller)
    cm.register_controller("instructions", instructions_controller)
    cm.register_controller("level_complete", level_complete_controller)

    # Set and check active controller
    cm.set_controller("game")
    assert cm.active_controller is game_controller
    cm.set_controller("instructions")
    assert cm.active_controller is instructions_controller
    cm.set_controller("level_complete")
    assert cm.active_controller is level_complete_controller

    # Test error on unknown controller
    with pytest.raises(ValueError):
        cm.set_controller("unknown")
