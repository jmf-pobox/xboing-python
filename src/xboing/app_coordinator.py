"""Application coordinator for XBoing, managing high-level app flow and orchestration."""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from xboing.controllers.controller_manager import ControllerManager
    from xboing.ui.ui_manager import UIManager


class AppCoordinator:
    """Coordinates synchronization between the UIManager and ControllerManager.

    Ensures the active controller matches the current view.
    """

    def __init__(
        self, ui_manager: "UIManager", controller_manager: "ControllerManager"
    ) -> None:
        """Initialize the AppCoordinator and register the view change callback.

        Args:
        ----
            ui_manager: The UIManager instance managing UI views.
            controller_manager: The ControllerManager instance managing controllers.

        """
        self.logger = logging.getLogger("xboing.AppCoordinator")
        self.ui_manager = ui_manager
        self.controller_manager = controller_manager
        self.ui_manager.register_view_change_callback(self.on_view_change)
        # Initial sync
        if self.ui_manager.current_name:
            self.on_view_change(self.ui_manager.current_name)

    def on_view_change(self, view_name: str) -> None:
        """Sync the active controller to the current view name.

        Args:
        ----
            view_name: The name of the view that became active.

        """
        self.logger.debug(f"AppCoordinator: Syncing controller to view: {view_name}")
        if view_name in self.controller_manager.controllers:
            self.controller_manager.set_controller(view_name)
