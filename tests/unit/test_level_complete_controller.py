from src.controllers.level_complete_controller import LevelCompleteController

def test_level_complete_controller_instantiation_and_methods():
    controller = LevelCompleteController(on_advance_callback=None)
    # Should not raise
    controller.handle_events([])
    controller.update(0.016) 