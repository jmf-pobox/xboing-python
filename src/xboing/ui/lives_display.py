"""LivesDisplayComponent: UI component for displaying the player's remaining lives as ball images.

Subscribes to LivesChangedEvent and renders itself in the lives window region.
"""

from typing import List, Tuple

import pygame

from xboing.engine.events import LivesChangedEvent
from xboing.layout.game_layout import GameLayout
from xboing.renderers.lives_renderer import LivesRenderer

LIVES_TOP_Y = 12


class LivesDisplayComponent:
    """UI component for displaying the player's remaining lives as ball images.

    Subscribes to LivesChangedEvent and renders itself in the lives window region.
    Allows manual x positioning for layout compatibility.
    """

    def __init__(
        self,
        layout: GameLayout,
        lives_display_util: LivesRenderer,
        x: int = 365,
        max_lives: int = 3,
    ) -> None:
        """Initialize the LivesDisplayComponent.

        Args:
        ----
            layout (GameLayout): The GameLayout instance.
            lives_display_util (LivesRenderer): The LivesRenderer instance.
            x (int, optional): The x position for the lives display. Defaults to 365.
            max_lives (int, optional): The maximum number of lives to display. Defaults to 3.

        """
        self.layout = layout
        self.lives_display_util = lives_display_util
        self.lives: int = max_lives
        self.max_lives: int = max_lives
        self.x: int = x

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle lives update events and update the displayed lives.

        Args:
        ----
            events (List[pygame.event.Event]): List of Pygame events to handle.

        """
        for event in events:
            if event.type == pygame.USEREVENT and isinstance(
                event.event, LivesChangedEvent
            ):
                self.lives = event.event.lives

    def get_y_and_height(self) -> Tuple[int, int]:
        """Return the y position and height of the lives display for alignment."""
        lives_surf = self.lives_display_util.render(
            self.lives, spacing=10, scale=1.0, max_lives=self.max_lives
        )
        return (LIVES_TOP_Y, lives_surf.get_height())

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the lives as ball images onto the given surface.

        Args:
        ----
            surface (pygame.Surface): The Pygame surface to draw on.

        """
        lives_surf = self.lives_display_util.render(
            self.lives, spacing=10, scale=1.0, max_lives=self.max_lives
        )
        y = LIVES_TOP_Y
        surface.blit(lives_surf, (self.x, y))
