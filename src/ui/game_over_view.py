import logging
from typing import Callable, Optional

import pygame
from injector import inject

from .content_view import ContentView


class GameOverView(ContentView):
    """
    Content view for the game over screen. Draws only within the play window region.
    Calls reset_game callback when Space is pressed.
    """

    @inject
    def __init__(
        self,
        layout,
        renderer,
        font,
        small_font,
        get_score_callback: Callable[[], int],
        reset_game_callback: Optional[Callable[[], None]] = None,
    ):
        self.layout = layout
        self.renderer = renderer
        self.font = font
        self.small_font = small_font
        self.get_score = get_score_callback
        self.reset_game: Optional[Callable[[], None]] = reset_game_callback
        self.active = False
        self.logger = logging.getLogger("xboing.GameOverView")

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def handle_event(self, event):
        self.logger.debug(f"handle_event called with event: {event}")
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.logger.info("Spacebar pressed in GameOverView.")
            if self.reset_game:
                self.logger.info("Calling reset_game from GameOverView.")
                self.reset_game()

    def draw(self, surface):
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
