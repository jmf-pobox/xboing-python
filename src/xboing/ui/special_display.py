"""SpecialDisplay: UI component for displaying the status of special power-ups in the special window region.

Subscribes to special events and renders their state as colored labels.
"""

from typing import Any, Dict, List, Tuple

import pygame

from xboing.engine.events import SPECIAL_EVENT_MAP
from xboing.engine.graphics import Renderer
from xboing.layout.game_layout import GameLayout


class SpecialDisplay:
    """UI component for displaying the status of special power-ups in the special window region.

    Subscribes to events for each special and renders their state as colored labels.
    """

    LABELS: List[Tuple[str, str]] = [
        ("Reverse", "reverse"),
        ("Save", "save"),
        ("NoWall", "nowall"),
        ("x2", "x2"),
        ("Sticky", "sticky"),
        ("FastGun", "fastgun"),
        ("Killer", "killer"),
        ("x4", "x4"),
    ]
    EVENT_MAP: Dict[str, Any] = SPECIAL_EVENT_MAP

    def __init__(
        self,
        layout: GameLayout,
        renderer: Renderer,
        font: pygame.font.Font,
    ) -> None:
        """Initialize the SpecialDisplay.

        Args:
        ----
            layout (GameLayout): The GameLayout instance.
            renderer (Renderer): The renderer instance.
            font (pygame.font.Font): The font to use for labels.

        """
        self.layout: GameLayout = layout
        self.renderer: Renderer = renderer
        self.font: pygame.font.Font = font
        # State for each special (all off by default)
        self.state: Dict[str, bool] = {key: False for _, key in self.LABELS}

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle special power-up events and update state.

        Args:
        ----
            events (List[pygame.event.Event]): List of Pygame events to handle.

        """
        for event in events:
            for key, event_cls in self.EVENT_MAP.items():
                if event.type == pygame.USEREVENT and isinstance(
                    event.event, event_cls
                ):
                    self.state[key] = event.event.active

    def draw(self, _surface: pygame.Surface) -> None:
        """Draw the special power-up labels and their states.

        Args:
        ----
            surface (pygame.Surface): The Pygame surface to draw on.

        """
        special_rect = self.layout.special_window.rect.rect
        x0, y0 = special_rect.x + 5, special_rect.y + 3
        col_width = 49
        row_height = self.font.get_height() + 5
        for idx, (label, key) in enumerate(self.LABELS):
            col = idx % 4
            row = idx // 4
            x = x0 + col * col_width
            y = y0 + row * row_height
            color = (255, 255, 0) if self.state[key] else (255, 255, 255)
            self.renderer.draw_text(label, self.font, color, x, y, centered=False)
