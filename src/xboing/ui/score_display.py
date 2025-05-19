"""ScoreDisplay: UI component for displaying the player's score using LED-style digits.

Subscribes to ScoreChangedEvent and renders itself in the score window region.
"""

from typing import List

import pygame

from xboing.engine.events import ScoreChangedEvent
from xboing.layout.game_layout import GameLayout
from xboing.renderers.digit_renderer import DigitRenderer


class ScoreDisplay:
    """UI component for displaying the player's score using LED-style digits.

    Subscribes to ScoreChangedEvent and renders itself in the score window region.
    Allows manual x positioning for layout compatibility.
    Renders as a fixed-width, right-justified display (default 6 digits).
    """

    def __init__(
        self,
        layout: GameLayout,
        digit_display: DigitRenderer,
        x: int = 220,
        width: int = 6,
    ) -> None:
        """Initialize the ScoreDisplay.

        Args:
        ----
            layout (GameLayout): The GameLayout instance.
            digit_display (DigitRenderer): The DigitRenderer instance.
            x (int, optional): The x position for the score display. Defaults to 220.
            width (int, optional): The number of digits to display. Defaults to 6.

        """
        self.layout = layout
        self.digit_display = digit_display
        self.score: int = 0
        self.x = x
        self.width = width

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle score update events and update the displayed score.

        Args:
        ----
            events (List[pygame.event.Event]): List of Pygame events to handle.

        """
        for event in events:
            if event.type == pygame.USEREVENT and isinstance(
                event.event, ScoreChangedEvent
            ):
                self.score = event.event.score

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the score as a fixed-width, right-justified number onto the given surface.

        Args:
        ----
            surface (pygame.Surface): The Pygame surface to draw on.

        """
        score_rect = self.layout.get_score_rect()
        # Render the score as a fixed-width, right-justified number
        score_surf = self.digit_display.render_number(
            self.score, width=self.width, right_justified=True
        )
        y = score_rect.y + (score_rect.height - score_surf.get_height()) // 2
        surface.blit(score_surf, (self.x, y))
