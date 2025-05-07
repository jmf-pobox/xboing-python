from src.controllers.instructions_controller import InstructionsController

def test_instructions_controller_instantiation_and_methods():
    controller = InstructionsController(on_exit_callback=None)
    # Should not raise
    controller.handle_events([])
    controller.update(0.016) 