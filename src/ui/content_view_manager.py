class ContentViewManager:
    def __init__(self):
        self.views = {}
        self.current_view = None
        self.current_name = None

    def register_view(self, name, view):
        self.views[name] = view
        if self.current_view is None:
            self.set_view(name)

    def set_view(self, name):
        if name in self.views:
            self.current_view = self.views[name]
            self.current_name = name
        else:
            raise ValueError(f"View '{name}' not registered.")

    def draw(self, surface):
        if self.current_view:
            self.current_view.draw(surface) 