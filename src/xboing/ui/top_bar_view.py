"""TopBarView: UI bar at the top of the XBoing window.

Displays score, lives, level, timer, message, and special status.
"""

from typing import List

import pygame

from xboing.ui.ammo_display import AmmoDisplayComponent
from xboing.ui.level_display import LevelDisplay
from xboing.ui.lives_display import LivesDisplayComponent
from xboing.ui.score_display import ScoreDisplay


class TopBarView:
    """UI bar at the top of the XBoing window.

    Displays score, lives, level, timer, message, and special status.
    """

    def __init__(
        self,
        score_display: ScoreDisplay,
        lives_display_component: LivesDisplayComponent,
        level_display_component: LevelDisplay,
        ammo_display_component: AmmoDisplayComponent,
    ) -> None:
        """Initialize the TopBarView.

        Args:
        ----
            score_display: The ScoreDisplay component.
            lives_display_component: The LivesDisplayComponent.
            level_display_component: The LevelDisplay component.
            ammo_display_component: The AmmoDisplayComponent.

        """
        self.score_display = score_display
        self.lives_display_component = lives_display_component
        self.level_display_component = level_display_component
        self.ammo_display_component = ammo_display_component

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Forward events to all top bar components.

        Args:
        ----
            events (List[pygame.event.Event]): List of Pygame events to handle.

        """
        self.score_display.handle_events(events)
        self.lives_display_component.handle_events(events)
        self.ammo_display_component.handle_events(events)
        self.level_display_component.handle_events(events)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all top bar components onto the given surface.

        Args:
        ----
            surface (pygame.Surface): The Pygame surface to draw on.

        """
        self.score_display.draw(surface)
        self.lives_display_component.draw(surface)
        self.ammo_display_component.draw(surface)
        self.level_display_component.draw(surface)
