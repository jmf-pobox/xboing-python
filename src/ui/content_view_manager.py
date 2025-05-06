from .content_view import ContentView
import logging


class ContentViewManager:
    def __init__(self):
        self.views: dict[str, ContentView] = {}
        self.current_view: ContentView | None = None
        self.current_name: str | None = None
        self.logger = logging.getLogger("xboing.ContentViewManager")

    def register_view(self, name: str, view: ContentView):
        self.views[name] = view
        if self.current_view is None:
            self.set_view(name)

    def set_view(self, name: str):
        if name in self.views:
            if self.current_view is not None and hasattr(self.current_view, 'deactivate'):
                self.logger.info(f"Deactivating view: {self.current_name}")
                self.current_view.deactivate()
            self.logger.info(f"Switching to view: {name}")
            self.current_view = self.views[name]
            self.current_name = name
            if hasattr(self.current_view, 'activate'):
                self.logger.info(f"Activating view: {name}")
                self.current_view.activate()
        else:
            self.logger.error(f"View '{name}' not registered.")
            raise ValueError(f"View '{name}' not registered.")

    def draw(self, surface):
        if self.current_view:
            self.current_view.draw(surface) 