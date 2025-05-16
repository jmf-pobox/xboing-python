import logging


class AppCoordinator:
    def __init__(self, ui_manager, controller_manager):
        self.logger = logging.getLogger("xboing.AppCoordinator")
        self.ui_manager = ui_manager
        self.controller_manager = controller_manager
        self.ui_manager.register_view_change_callback(self.on_view_change)
        # Initial sync
        if self.ui_manager.current_name:
            self.on_view_change(self.ui_manager.current_name)

    def on_view_change(self, view_name):
        self.logger.debug(f"AppCoordinator: Syncing controller to view: {view_name}")
        if view_name in self.controller_manager.controllers:
            self.controller_manager.set_controller(view_name)
