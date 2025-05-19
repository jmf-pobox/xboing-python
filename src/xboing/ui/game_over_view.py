"""UI view for displaying the game over screen in XBoing."""

import logging
from typing import Callable

from injector import inject
import pygame

from xboing.engine.graphics import Renderer
from xboing.layout.game_layout import GameLayout

from .view import View


class GameOverView(View):
    """Content view for the game over screen. Draws only within the play window region.

    Calls GameOverController.reset_game when Space is pressed.
    """

    @inject
    def __init__(
        self,
        layout: GameLayout,
        renderer: Renderer,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        get_score_callback: Callable[[], int],
    ) -> None:
        """Initialize the GameOverView.

        Args:
        ----
            layout (GameLayout): The GameLayout instance.
            renderer (Renderer): The renderer instance.
            font (pygame.font.Font): The main font.
            small_font (pygame.font.Font): The font for secondary text.
            get_score_callback (Callable[[], int]): Callback to get the final score.

        """
        self.layout: GameLayout = layout
        self.renderer: Renderer = renderer
        self.font: pygame.font.Font = font
        self.small_font: pygame.font.Font = small_font
        self.get_score: Callable[[], int] = get_score_callback
        self.active: bool = False
        self.logger = logging.getLogger("xboing.GameOverView")

    def activate(self) -> None:
        """Activate the view."""
        self.active = True

    def deactivate(self) -> None:
        """Deactivate the view."""
        self.active = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a single Pygame event. Calls controller.reset_game if Space is pressed.

        Args:
        ----
            event (pygame.event.Event): The Pygame event to handle.

        """
        # No-op for now; remove unnecessary pass

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the game over overlay and final score onto the given surface.

        Args:
        ----
            surface (pygame.Surface): The Pygame surface to draw on.

        """
        play_rect = self.layout.get_play_rect()
        self.logger.debug(f"draw called. Drawing overlay in play_rect: {play_rect}")
        # Overlay only in play window
        overlay = pygame.Surface((play_rect.width, play_rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (play_rect.x, play_rect.y))
        # Text
        self.renderer.draw_text(
            "GAME OVER",
            self.font,
            (255, 50, 50),
            play_rect.centerx,
            play_rect.centery - 60,
            centered=True,
        )
        self.renderer.draw_text(
            "FINAL SCORE",
            self.small_font,
            (255, 255, 255),
            play_rect.centerx,
            play_rect.centery - 20,
            centered=True,
        )
        score = self.get_score()
        self.renderer.draw_text(
            str(score),
            self.font,
            (255, 255, 0),
            play_rect.centerx,
            play_rect.centery + 20,
            centered=True,
        )
        self.renderer.draw_text(
            "Press SPACE to restart",
            self.small_font,
            (200, 200, 200),
            play_rect.centerx,
            play_rect.centery + 70,
            centered=True,
        )
