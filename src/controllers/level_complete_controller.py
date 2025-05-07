from .base_controller import BaseController

class LevelCompleteController(BaseController):
    """
    Handles input and transitions for the LevelCompleteView.
    """
    def __init__(self, on_advance_callback=None):
        self.on_advance_callback = on_advance_callback

    def handle_events(self, events):
        """Handle input/events for level complete view."""
        pass

    def update(self, delta_time):
        """Update logic for level complete view (usually minimal)."""
        pass 