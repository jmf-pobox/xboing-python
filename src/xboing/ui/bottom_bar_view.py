"""BottomBarView: UI bar at the bottom of the XBoing window.

Displays message, special status, and timer.
"""

from typing import List

import pygame

from xboing.ui.message_display import MessageDisplay
from xboing.ui.special_display import SpecialDisplay
from xboing.ui.timer_display import TimerDisplay


class BottomBarView:
    """UI bar at the bottom of the XBoing window.

    Displays message, special status, and timer.
    """

    def __init__(
        self,
        message_display_component: MessageDisplay,
        special_display_component: SpecialDisplay,
        timer_display_component: TimerDisplay,
    ) -> None:
        """Initialize the BottomBarView.

        Args:
        ----
            message_display_component: The MessageDisplay component.
            special_display_component: The SpecialDisplay component.
            timer_display_component: The TimerDisplay component.

        """
        self.message_display_component = message_display_component
        self.special_display_component = special_display_component
        self.timer_display_component = timer_display_component

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Forward events to all bottom bar components.

        Args:
        ----
            events (List[pygame.event.Event]): List of Pygame events to handle.

        """
        self.message_display_component.handle_events(events)
        self.special_display_component.handle_events(events)
        self.timer_display_component.handle_events(events)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all bottom bar components onto the given surface.

        Args:
        ----
            surface (pygame.Surface): The Pygame surface to draw on.

        """
        self.message_display_component.draw(surface)
        self.special_display_component.draw(surface)
        self.timer_display_component.draw(surface)
