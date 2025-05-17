from controllers.level_complete_controller import LevelCompleteController


class Dummy:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None


def test_level_complete_controller_instantiation_and_methods():
    # Provide all required arguments as dummies/mocks
    game_state = Dummy()
    level_manager = Dummy()
    balls = []
    game_controller = Dummy()
    ui_manager = Dummy()
    game_view = Dummy()
    layout = Dummy()
    controller = LevelCompleteController(
        game_state,
        level_manager,
        balls,
        game_controller,
        ui_manager,
        game_view,
        layout,
        on_advance_callback=None,
    )
    # Should not raise
    controller.handle_events([])
    controller.update(0.016)
