import logging

from utils.logging_decorators import log_entry_exit


class ControllerManager:
    """
    Manages all controllers and switches the active controller based on the current view.
    """

    def __init__(self):
        self.controllers = {}
        self._active_name = None
        self.logger = logging.getLogger("xboing.ControllerManager")

    @log_entry_exit()
    def register_controller(self, name, controller):
        self.controllers[name] = controller
        self.logger.debug(f"Registered controller: {name}")

    @log_entry_exit()
    def set_controller(self, name):
        if name in self.controllers:
            self._active_name = name
            self.logger.debug(f"Set active controller: {name}")
        else:
            self.logger.error(f"Controller '{name}' not registered.")
            raise ValueError(f"Controller '{name}' not registered.")

    @property
    def active_controller(self):
        if self._active_name is not None:
            return self.controllers[self._active_name]
        return None
