"""UI view for displaying the game over screen in XBoing."""

import logging
from typing import Callable, List, Optional, Tuple

from injector import inject
import pygame

from xboing.engine.graphics import Renderer
from xboing.layout.game_layout import GameLayout
from xboing.renderers.composite_renderer import CompositeRenderer
from xboing.renderers.row_renderer import RowRenderer, TextRowRenderer

from .view_with_background import ViewWithBackground


class GameOverView(ViewWithBackground):
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
        super().__init__(layout)
        self.renderer: Renderer = renderer
        self.font: pygame.font.Font = font
        self.small_font: pygame.font.Font = small_font
        self.get_score: Callable[[], int] = get_score_callback
        self.active: bool = False
        self.logger = logging.getLogger("xboing.GameOverView")
        self._row_renderers_with_y: List[Tuple[RowRenderer, int]] = []
        self._composite_renderer: Optional[CompositeRenderer] = None

    def activate(self) -> None:
        """Activate the view and prepare renderers."""
        self.active = True
        self._prepare_renderers()

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

    def _prepare_renderers(self) -> None:
        """Prepare the list of (renderer, y) pairs for the game over text rows."""
        play_rect = self.layout.get_play_rect()
        # Y coordinates for each row (approximate, can be tuned)
        y_coords = [
            play_rect.centery - 60,  # GAME OVER
            play_rect.centery - 20,  # FINAL SCORE
            play_rect.centery + 20,  # score
            play_rect.centery + 70,  # Press SPACE
        ]
        score = self.get_score()
        self._row_renderers_with_y = [
            (TextRowRenderer("GAME OVER", self.font, (255, 50, 50)), y_coords[0]),
            (
                TextRowRenderer("FINAL SCORE", self.small_font, (255, 255, 255)),
                y_coords[1],
            ),
            (TextRowRenderer(str(score), self.font, (255, 255, 0)), y_coords[2]),
            (
                TextRowRenderer(
                    "Press SPACE to restart", self.small_font, (200, 200, 200)
                ),
                y_coords[3],
            ),
        ]
        self._composite_renderer = CompositeRenderer(self._row_renderers_with_y)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the game over overlay and final score using stateless renderers."""
        play_rect = self.layout.get_play_rect()
        self.logger.debug(f"draw called. Drawing overlay in play_rect: {play_rect}")
        # Draw the play area background (via ViewWithBackground)
        super().draw(surface)
        # Overlay only in play window
        overlay = pygame.Surface((play_rect.width, play_rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (play_rect.x, play_rect.y))
        # Draw all text rows using composite renderer
        if self._composite_renderer:
            self._composite_renderer.render(
                surface,
                play_rect.centerx,
                len(self._row_renderers_with_y),
            )

    def update(self, delta_ms: float) -> None:
        """Update the view (currently a stub)."""
        # No-op for now
