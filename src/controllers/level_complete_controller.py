import pygame

from engine.events import MessageChangedEvent

from .base_controller import BaseController


class LevelCompleteController(BaseController):
    """
    Handles input and transitions for the LevelCompleteView.
    Handles spacebar to advance to next level, and global controls via BaseController.
    Also handles LevelCompleteEvent and level advancement logic.
    """

    def __init__(
        self,
        game_state,
        level_manager,
        balls,
        game_controller,
        ui_manager,
        game_view,
        layout,
        on_advance_callback=None,
        audio_manager=None,
        quit_callback=None,
    ):
        super().__init__(
            audio_manager=audio_manager,
            quit_callback=quit_callback,
            ui_manager=ui_manager,
        )
        self.game_state = game_state
        self.level_manager = level_manager
        self.balls = balls
        self.game_controller = game_controller
        self.game_view = game_view
        self.layout = layout
        self.on_advance_callback = on_advance_callback
        self.waiting_for_launch_ref = None  # To be set by main if needed

    def handle_events(self, events):
        """Handle input/events for level complete view and global controls."""
        super().handle_events(events)
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.logger.debug(
                    "Spacebar pressed on LevelCompleteView. Advancing to next level."
                )
                self.advance_to_next_level()

    def advance_to_next_level(self):
        self.logger.debug(
            "advance_to_next_level called: advancing to next level and switching to game view/controller."
        )
        self.game_controller.level_complete = False  # Reset for new level
        self.game_state.set_level(self.game_state.level + 1)
        self.level_manager.get_next_level()
        if self.waiting_for_launch_ref is not None:
            self.waiting_for_launch_ref[0] = True
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": type("UIButtonClickEvent", (), {})()}))
        level_info = self.level_manager.get_level_info()
        level_title = level_info["title"]
        pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"event": MessageChangedEvent(level_title, color=(0, 255, 0), alignment="left")}))
        self.balls.clear()
        self.balls.append(self.game_controller.create_new_ball())
        self.game_controller.waiting_for_launch = True
        self.game_view.balls = self.balls
        self.ui_manager.set_view("game")
        # Optionally sync controller with view if needed

    def handle_event(self, event):
        self.logger.info(
            "handle_event called: LevelCompleteEvent received. Switching to level_complete view."
        )
        self.ui_manager.set_view("level_complete")

    def update(self, delta_time):
        """Update logic for level complete view (usually minimal)."""
        pass
