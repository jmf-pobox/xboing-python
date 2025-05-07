class BaseController:
    """
    Base class for all controllers. Controllers handle input/events and update logic for their associated view.
    """
    def handle_events(self, events):
        """Handle input/events for this controller."""
        pass

    def update(self, delta_time):
        """Update logic for this controller."""
        pass 