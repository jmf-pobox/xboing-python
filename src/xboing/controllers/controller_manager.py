"""Manages controller registration and switching for XBoing."""

import logging
from typing import Any, Dict, Optional

from xboing.utils.logging_decorators import log_entry_exit


class ControllerManager:
    """Manages all controllers and switches the active controller based on the current view."""

    def __init__(self) -> None:
        """Initialize the ControllerManager."""
        self.controllers: Dict[str, Any] = {}
        self._active_name: Optional[str] = None
        self.logger = logging.getLogger("xboing.ControllerManager")

    @log_entry_exit()
    def register_controller(self, name: str, controller: Any) -> None:
        """Register a controller with a given name.

        Args:
        ----
            name: The name of the controller.
            controller: The controller instance to register.

        """
        self.controllers[name] = controller
        self.logger.debug(f"Registered controller: {name}")

    @log_entry_exit()
    def set_controller(self, name: str) -> None:
        """Set the active controller by name.

        Args:
        ----
            name: The name of the controller to activate.

        Raises:
        ------
            ValueError: If the controller name is not registered.

        """
        if name in self.controllers:
            self._active_name = name
            self.logger.debug(f"Set active controller: {name}")
        else:
            self.logger.error(f"Controller '{name}' not registered.")
            raise ValueError(f"Controller '{name}' not registered.")

    @property
    def active_controller(self) -> Optional[Any]:
        """Get the currently active controller.

        Returns
        -------
            The active controller instance, or None if not set.

        """
        if self._active_name is not None:
            return self.controllers[self._active_name]
        return None
