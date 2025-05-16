import pygame


class UIManager:
    """
    Manages all UI components, content views, and bars for the application.

    UIManager is responsible for:
    - Registering and switching between different content views (e.g., game, game over, instructions).
    - Managing top and bottom UI bars.
    - Tracking the currently active and previous views.
    - Dispatching events to the always-active WindowController and the active view's controller.
    - Drawing all registered UI components onto the main surface.
    - Providing a unified interface for UI setup and event handling.

    Typical usage:
        ui_manager = UIManager(window_controller, view_controller_map)
        ui_manager.setup_ui(views=..., top_bar=..., bottom_bar=..., initial_view=...)
        ui_manager.handle_events(events)
        ui_manager.draw_all(surface)

    Attributes:
        top_bar: The top UI bar component.
        bottom_bar: The bottom UI bar component.
        views: Dictionary mapping view names to view objects.
        current_view: The currently active view object.
        current_name: The name of the currently active view.
        previous_view: The name of the previously active view.
        window_controller: The always-active controller for global events.
        view_controller_map: Mapping of view names to their controllers.
    """

    def __init__(self, window_controller=None, view_controller_map=None):
        """
        Initialize the UIManager.

        Args:
            window_controller: The always-active controller for global events.
            view_controller_map: Mapping of view names to their controllers.
        """
        self.top_bar = None
        self.bottom_bar = None
        self.views = {}
        self.current_view = None
        self.current_name = None
        self.previous_view = None  # Track previous view
        self._view_change_callbacks = []
        self.window_controller = window_controller
        self.view_controller_map = view_controller_map or {}

    def register_top_bar(self, top_bar):
        """
        Register the top UI bar component.

        Args:
            top_bar: The top bar UI component to register.
        """
        self.top_bar = top_bar

    def register_bottom_bar(self, bottom_bar):
        """
        Register the bottom UI bar component.

        Args:
            bottom_bar: The bottom bar UI component to register.
        """
        self.bottom_bar = bottom_bar

    def register_view(self, name, view):
        """
        Register a content view with a given name.

        Args:
            name: The name of the view.
            view: The view object to register.
        """
        self.views[name] = view
        if self.current_view is None:
            self.set_view(name)

    def register_view_change_callback(self, callback):
        """
        Register a callback to be called when the view changes.

        Args:
            callback: A callable that takes the new view name as its argument.
        """
        self._view_change_callbacks.append(callback)

    def set_view(self, name):
        """
        Set the active view by name.

        Args:
            name: The name of the view to activate.

        Raises:
            ValueError: If the view name is not registered.
        """
        if name in self.views:
            if self.current_view is not None:
                self.current_view.deactivate()
            # Track previous view unless already in instructions
            if self.current_name != "instructions":
                self.previous_view = self.current_name
            self.current_view = self.views[name]
            self.current_name = name
            self.current_view.activate()
            for cb in self._view_change_callbacks:
                cb(name)
        else:
            raise ValueError(f"View '{name}' not registered.")

    def draw_all(self, surface):
        """
        Draw the current view, top bar, and bottom bar onto the given surface.

        Args:
            surface: The Pygame surface to draw on.
        """
        if self.current_view:
            self.current_view.draw(surface)
        if self.top_bar:
            self.top_bar.draw(surface)
        if self.bottom_bar:
            self.bottom_bar.draw(surface)

    def setup_ui(self, *, views=None, top_bar=None, bottom_bar=None, initial_view=None):
        """
        Register all UI components in one place. Accepts dict of views, top/bottom bars, and initial view name.

        Args:
            views: Dictionary of view names to view objects.
            top_bar: The top bar UI component.
            bottom_bar: The bottom bar UI component.
            initial_view: The name of the initial view to activate.
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
        """
        Handle and dispatch events to the window controller, active view's controller, and UI bars.

        Args:
            events: List of Pygame events to handle.
        """
        from engine.events import GameOverEvent, LevelCompleteEvent

        # Dispatch to always-active window controller
        if self.window_controller:
            self.window_controller.handle_events(events)
        # Dispatch to the active view's controller
        if self.current_name and self.current_name in self.view_controller_map:
            controller = self.view_controller_map[self.current_name]
            if controller:
                controller.handle_events(events)
        # UIManager's own event handling
        for event in events:
            if event.type == pygame.USEREVENT and isinstance(
                event.event, GameOverEvent
            ):
                self.set_view("game_over")
            elif event.type == pygame.USEREVENT and isinstance(
                event.event, LevelCompleteEvent
            ):
                self.set_view("level_complete")
        # Forward events to top_bar and bottom_bar (assume they implement handle_events)
        if self.top_bar:
            self.top_bar.handle_events(events)
        if self.bottom_bar:
            self.bottom_bar.handle_events(events)
