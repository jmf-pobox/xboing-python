"""
TopBarView: UI bar at the top of the XBoing window.
Displays score, lives, level, timer, message, and special status.
"""

from typing import Any, List

import pygame


class TopBarView:
    """
    UI bar at the top of the XBoing window.
    Displays score, lives, level, timer, message, and special status.
    """

    def __init__(
        self,
        score_display: Any,
        lives_display_component: Any,
        level_display_component: Any,
        timer_display_component: Any,
        message_display_component: Any,
        special_display_component: Any,
    ) -> None:
        """
        Initialize the TopBarView.

        Args:
            score_display: The ScoreDisplay component.
            lives_display_component: The LivesDisplayComponent.
            level_display_component: The LevelDisplay component.
            timer_display_component: The TimerDisplay component.
            message_display_component: The MessageDisplay component.
            special_display_component: The SpecialDisplay component.
        """
        self.score_display = score_display
        self.lives_display_component = lives_display_component
        self.level_display_component = level_display_component
        self.timer_display_component = timer_display_component
        self.message_display_component = message_display_component
        self.special_display_component = special_display_component

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """
        Forward events to all top bar components.

        Args:
            events (List[pygame.event.Event]): List of Pygame events to handle.
        """
        self.score_display.handle_events(events)
        self.lives_display_component.handle_events(events)
        self.level_display_component.handle_events(events)
        self.timer_display_component.handle_events(events)
        self.message_display_component.handle_events(events)
        self.special_display_component.handle_events(events)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw all top bar components onto the given surface.

        Args:
            surface (pygame.Surface): The Pygame surface to draw on.
        """
        self.score_display.draw(surface)
        self.lives_display_component.draw(surface)
        self.level_display_component.draw(surface)
        self.timer_display_component.draw(surface)
        self.message_display_component.draw(surface)
        self.special_display_component.draw(surface)
