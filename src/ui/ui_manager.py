class UIManager:
    """
    UIManager owns and coordinates all UI components, content views, and bars, and manages which view is active.
    """

    def __init__(self):
        self.top_bar = None
        self.bottom_bar = None
        self.views = {}
        self.current_view = None
        self.current_name = None
        self._view_change_callbacks = []

    def register_top_bar(self, top_bar):
        self.top_bar = top_bar

    def register_bottom_bar(self, bottom_bar):
        self.bottom_bar = bottom_bar

    def register_view(self, name, view):
        self.views[name] = view
        if self.current_view is None:
            self.set_view(name)

    def register_view_change_callback(self, callback):
        self._view_change_callbacks.append(callback)

    def set_view(self, name):
        if name in self.views:
            if self.current_view is not None and hasattr(
                self.current_view, "deactivate"
            ):
                self.current_view.deactivate()
            self.current_view = self.views[name]
            self.current_name = name
            if hasattr(self.current_view, "activate"):
                self.current_view.activate()
            for cb in self._view_change_callbacks:
                cb(name)
        else:
            raise ValueError(f"View '{name}' not registered.")

    def draw_all(self, surface):
        if self.current_view:
            self.current_view.draw(surface)
        if self.top_bar:
            self.top_bar.draw(surface)
        if self.bottom_bar:
            self.bottom_bar.draw(surface)

    def setup_ui(self, *, views=None, top_bar=None, bottom_bar=None, initial_view=None):
        """
        Register all UI components in one place. Accepts dict of views, top/bottom bars, and initial view name.
        """
        if top_bar:
            self.register_top_bar(top_bar)
        if bottom_bar:
            self.register_bottom_bar(bottom_bar)
        if views:
            for name, view in views.items():
                self.register_view(name, view)
        if initial_view:
            self.set_view(initial_view)

    def handle_events(self, events):
        from engine.events import GameOverEvent, LevelCompleteEvent
        for event in events:
            if hasattr(event, 'event') and isinstance(event.event, GameOverEvent):
                self.set_view("game_over")
            elif hasattr(event, 'event') and isinstance(event.event, LevelCompleteEvent):
                self.set_view("level_complete")

        # Forward events to top_bar and bottom_bar if they have handle_events methods
        if self.top_bar and hasattr(self.top_bar, 'handle_events'):
            self.top_bar.handle_events(events)
        if self.bottom_bar and hasattr(self.bottom_bar, 'handle_events'):
            self.bottom_bar.handle_events(events)
