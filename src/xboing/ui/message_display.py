"""MessageDisplay: UI component for displaying messages in the message window region.

Subscribes to MessageChangedEvent and renders itself using the renderer.
"""

from typing import List

import pygame

from xboing.engine.events import MessageChangedEvent
from xboing.engine.graphics import Renderer
from xboing.layout.game_layout import GameLayout


class MessageDisplay:
    """UI component for displaying messages in the message window region.

    Subscribes to MessageChangedEvent and renders itself using renderer.draw_text.
    Style matches the timer: bright green, same font size.
    """

    def __init__(
        self,
        layout: GameLayout,
        renderer: Renderer,
        font: pygame.font.Font,
    ) -> None:
        """Initialize the MessageDisplay.

        Args:
        ----
            layout (GameLayout): The GameLayout instance.
            renderer (Renderer): The renderer instance.
            font (pygame.font.Font): The font to use for messages.

        """
        self.layout = layout
        self.renderer = renderer
        self.font = font
        self.message: str = ""
        self.alignment: str = "left"

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle message update events and update the displayed message.

        Args:
        ----
            events (List[pygame.event.Event]): List of Pygame events to handle.

        """
        for event in events:
            if event.type == pygame.USEREVENT and isinstance(
                event.event, MessageChangedEvent
            ):
                self.message = event.event.message
                self.alignment = event.event.alignment

    def draw(self, _surface: pygame.Surface) -> None:
        """Draw the message onto the given surface.

        Args:
        ----
            surface (pygame.Surface): The Pygame surface to draw on.

        """
        message_rect = self.layout.get_message_rect()
        y = message_rect.y + (message_rect.height // 2)
        if self.alignment == "center":
            x = message_rect.x + (message_rect.width // 2)
            centered = True
        else:
            x = message_rect.x + 10  # Left margin
            centered = False
        # Always use bright green, matching the timer
        color = (0, 255, 0)
        self.renderer.draw_text(
            self.message,
            self.font,
            color,
            x,
            y,
            centered=centered,
        )
