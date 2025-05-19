"""TimerDisplay: UI component for displaying the remaining time in the timer window region.

Subscribes to TimerUpdatedEvent and renders itself using the renderer.
"""

from typing import List

import pygame

from xboing.engine.events import TimerUpdatedEvent
from xboing.engine.graphics import Renderer
from xboing.layout.game_layout import GameLayout


class TimerDisplay:
    """UI component for displaying the remaining time in the timer window region.

    Subscribes to TimerUpdatedEvent and renders itself using the renderer.
    """

    def __init__(
        self, layout: GameLayout, renderer: Renderer, font: pygame.font.Font
    ) -> None:
        """Initialize the TimerDisplay.

        Args:
        ----
            layout: The GameLayout instance.
            renderer: The renderer instance.
            font: The font to use for the timer.

        """
        self.layout = layout
        self.renderer = renderer
        self.font = font
        self.time_remaining = 0

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle timer update events and update the displayed time.

        Args:
        ----
            events: List of Pygame events to handle.

        """
        for event in events:
            if event.type == pygame.USEREVENT and isinstance(
                event.event, TimerUpdatedEvent
            ):
                self.time_remaining = event.event.time_remaining

    def draw(self, _surface: pygame.Surface) -> None:
        """Draw the timer onto the given surface.

        Args:
        ----
            surface: The Pygame surface to draw on.

        """
        timer_rect = self.layout.get_timer_rect()
        y = timer_rect.y + (timer_rect.height // 2)
        x = timer_rect.x + (timer_rect.width // 2)
        color = (0, 255, 0)
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        timer_str = f"{minutes:02}:{seconds:02}"
        self.renderer.draw_text(
            timer_str,
            self.font,
            color,
            x,
            y,
            centered=True,
        )
