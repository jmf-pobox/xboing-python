class ControllerManager:
    """
    Manages all controllers and switches the active controller based on the current view.
    """
    def __init__(self):
        self.controllers = {}
        self._active_name = None

    def register_controller(self, name, controller):
        self.controllers[name] = controller

    def set_controller(self, name):
        if name in self.controllers:
            self._active_name = name
        else:
            raise ValueError(f"Controller '{name}' not registered.")

    @property
    def active_controller(self):
        if self._active_name is not None:
            return self.controllers[self._active_name]
        return None 