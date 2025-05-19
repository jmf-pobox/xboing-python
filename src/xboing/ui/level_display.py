"""LevelDisplay: UI component for displaying the current level number using LED-style digits.

Subscribes to LevelChangedEvent and renders itself in the level window region.
"""

from typing import List

import pygame

from xboing.engine.events import LevelChangedEvent
from xboing.layout.game_layout import GameLayout
from xboing.renderers.digit_renderer import DigitRenderer


class LevelDisplay:
    """UI component for displaying the current level number using LED-style digits.

    Subscribes to LevelChangedEvent and renders itself in the level window region.
    Allows manual x positioning for layout compatibility.
    """

    def __init__(
        self,
        layout: GameLayout,
        digit_display: DigitRenderer,
        x: int = 510,
    ) -> None:
        """Initialize the LevelDisplay.

        Args:
        ----
            layout (GameLayout): The GameLayout instance.
            digit_display (DigitRenderer): The DigitRenderer instance.
            x (int, optional): The x position for the level display. Defaults to 510.

        """
        self.layout = layout
        self.digit_display = digit_display
        self.level: int = 1
        self.x: int = x

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle level update events and update the displayed level.

        Args:
        ----
            events (List[pygame.event.Event]): List of Pygame events to handle.

        """
        for event in events:
            if event.type == pygame.USEREVENT and isinstance(
                event.event, LevelChangedEvent
            ):
                self.level = event.event.level

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the level number as LED-style digits onto the given surface.

        Args:
        ----
            surface (pygame.Surface): The Pygame surface to draw on.

        """
        score_rect = self.layout.get_score_rect()
        # Render the level using DigitRenderer
        level_surf = self.digit_display.render_number(self.level)
        y = score_rect.y + (score_rect.height - level_surf.get_height()) // 2
        surface.blit(level_surf, (self.x, y))
