class UIManager:
    """
    UIManager owns and coordinates all UI components, content views, overlays, and manages which view is active.
    """
    def __init__(self):
        # Registry for UI components, content views, overlays
        self.top_bar = None
        self.bottom_bar = None
        self.content_view_manager = None
        self.overlays = []  # Stack/list of overlays

    def register_top_bar(self, top_bar):
        self.top_bar = top_bar

    def register_bottom_bar(self, bottom_bar):
        self.bottom_bar = bottom_bar

    def register_content_view_manager(self, content_view_manager):
        self.content_view_manager = content_view_manager

    def add_overlay(self, overlay):
        self.overlays.append(overlay)

    def remove_overlay(self, overlay):
        if overlay in self.overlays:
            self.overlays.remove(overlay)

    def draw_all(self, surface):
        """Draw all UI elements in the correct order."""
        if self.content_view_manager:
            self.content_view_manager.draw(surface)
        if self.top_bar:
            self.top_bar.draw(surface)
        if self.bottom_bar:
            self.bottom_bar.draw(surface)
        for overlay in self.overlays:
            overlay.draw(surface) 