"""UI view for displaying game instructions in XBoing."""

import os
from typing import List, Tuple

from injector import inject
import pygame

from xboing.engine.graphics import Renderer
from xboing.layout.game_layout import GameLayout
from xboing.utils.asset_loader import load_image
from xboing.utils.asset_paths import get_backgrounds_dir, get_images_dir

from .view import View


class InstructionsView(View):
    """View for displaying game instructions in the XBoing UI."""

    @inject
    def __init__(
        self,
        layout: GameLayout,
        renderer: Renderer,
        font: pygame.font.Font,
        headline_font: pygame.font.Font,
        text_font: pygame.font.Font,
        amber_color: Tuple[int, int, int] = (255, 191, 63),
    ) -> None:
        """Initialize the InstructionsView.

        Args:
        ----
            layout (GameLayout): The GameLayout instance.
            renderer (Renderer): The renderer instance.
            font (pygame.font.Font): The main font.
            headline_font (pygame.font.Font): The font for headlines.
            text_font (pygame.font.Font): The font for instructions text.
            amber_color (Tuple[int, int, int], optional): Amber color for the bottom line. Defaults to (255, 191, 63).

        """
        self.layout: GameLayout = layout
        self.renderer: Renderer = renderer
        self.font: pygame.font.Font = font
        self.headline_font: pygame.font.Font = headline_font
        self.text_font: pygame.font.Font = text_font
        self.amber_color: Tuple[int, int, int] = amber_color
        # Manually broken lines to match the original game's style
        self.lines: List[str] = [
            # Paragraph 1 (3 lines)
            "XBoing is a blockout game where you use a paddle to bounce",
            "a proton ball around an arena full of nasties while keeping",
            "the ball from leaving the arena via the bottom rebound wall.",
            # Paragraph 2 (4 lines)
            "Each block has a point value associated with it. Some blocks",
            "may award you more points for hitting them a number of times.",
            "Some blocks may toggle extra time/points or even special effects",
            "such as no walls, machine gun, sticky paddle, reverse controls, etc.",
            # Paragraph 3 (2 lines)
            "Your paddle is equipped with special bullets that can disintegrate",
            "a block. You only have a limited supply of bullets so use them wisely.",
            # Paragraph 4 (4 lines)
            "The multiple ball block will give you an extra ball to play with in",
            "the arena. This ball will act like any other ball except that when",
            "it dies it will not force a new ball to start. You can shoot your",
            "own ball so watch out. The death symbol is not too healthy either.",
            # Paragraph 5 (2 lines)
            "Sometimes a special block may appear or be added to another block",
            "that will affect the gameplay if hit. They also disappear randomly.",
            # Paragraph 6 (1 line)
            "Please read the manual for more information on how to play.",
        ]
        # Use asset loader utility and asset_paths to load mnbgrnd.png
        backgrounds_dir = get_backgrounds_dir()
        bg_path = os.path.join(backgrounds_dir, "mnbgrnd.png")
        self.bg_image = load_image(bg_path, alpha=False)

        # Load xboing.png logo from the main images directory
        images_dir = get_images_dir()
        logo_path = os.path.join(images_dir, "xboing.png")
        self.logo_image = load_image(logo_path, alpha=True)

    def _draw_background(self, play_surf: pygame.Surface) -> None:
        if self.bg_image:
            img_w, img_h = self.bg_image.get_width(), self.bg_image.get_height()
            for y in range(0, play_surf.get_height(), img_h):
                for x in range(0, play_surf.get_width(), img_w):
                    play_surf.blit(self.bg_image, (x, y))
        else:
            play_surf.fill((40, 40, 50))

    def _draw_logo(self, play_surf: pygame.Surface, centerx: int, y: int) -> int:
        if self.logo_image:
            max_logo_width = min(320, play_surf.get_width() - 40)
            max_logo_height = 100
            logo_w, logo_h = self.logo_image.get_width(), self.logo_image.get_height()
            scale = min(max_logo_width / logo_w, max_logo_height / logo_h, 1.0)
            scaled_w, scaled_h = int(logo_w * scale), int(logo_h * scale)
            logo_surf = pygame.transform.smoothscale(
                self.logo_image, (scaled_w, scaled_h)
            )
            logo_rect = logo_surf.get_rect(center=(centerx, y + scaled_h // 2))
            play_surf.blit(logo_surf, logo_rect)
            return logo_rect.bottom + 10

        logo_font = self.headline_font
        logo_text = "XBoing"
        logo_surf = logo_font.render(logo_text, True, (255, 255, 255))
        logo_rect = logo_surf.get_rect(center=(centerx, 40))
        play_surf.blit(logo_surf, logo_rect)
        return logo_rect.bottom + 10

    def _draw_headline(self, play_surf: pygame.Surface, centerx: int, y: int) -> int:
        headline = " - Instructions - "
        headline_surf = self.headline_font.render(headline, True, (255, 0, 0))
        headline_rect = headline_surf.get_rect(center=(centerx, y))
        play_surf.blit(headline_surf, headline_rect)
        return headline_rect.bottom + 20

    def _draw_text_block(
        self, play_surf: pygame.Surface, centerx: int, start_y: int
    ) -> int:
        line_height = self.text_font.get_height()
        total_lines = len(self.lines)
        total_text_height = total_lines * line_height + (total_lines - 1) * 6
        text_start_y = (play_surf.get_height() - total_text_height) // 2
        text_start_y = max(text_start_y, start_y)
        green1 = (0, 255, 0)
        green2 = (0, 200, 0)
        paragraph_ends = [2, 6, 8, 12, 14]
        y_offset = 0
        for i, line in enumerate(self.lines):
            color = green1 if (i // 3) % 2 == 0 else green2
            line_surf = self.text_font.render(line, True, color)
            line_rect = line_surf.get_rect(center=(centerx, text_start_y + y_offset))
            play_surf.blit(line_surf, line_rect)
            y_offset += line_height + 6
            if i in paragraph_ends:
                y_offset += 18
        return text_start_y + y_offset

    def _draw_amber_line(self, play_surf: pygame.Surface, centerx: int) -> None:
        amber = self.amber_color
        amber_text = "Insert coin to start the game"
        amber_surf = self.text_font.render(amber_text, True, amber)
        amber_rect = amber_surf.get_rect(center=(centerx, play_surf.get_height() - 40))
        play_surf.blit(amber_surf, amber_rect)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the instructions view onto the given surface.

        Args:
        ----
            surface (pygame.Surface): The Pygame surface to draw on.

        """
        play_rect = self.layout.get_play_rect()
        play_surf = pygame.Surface((play_rect.width, play_rect.height))
        self._draw_background(play_surf)
        centerx = play_rect.width // 2
        y = 20
        y = self._draw_logo(play_surf, centerx, y)
        y = self._draw_headline(play_surf, centerx, y)
        self._draw_text_block(play_surf, centerx, y)
        self._draw_amber_line(play_surf, centerx)
        surface.blit(play_surf, play_rect.topleft)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a single Pygame event (currently a stub).

        Args:
        ----
            event (pygame.event.Event): The Pygame event to handle.

        """
        # No-op for now

    def activate(self) -> None:
        """Activate the view (currently a stub)."""
        # No-op for now

    def deactivate(self) -> None:
        """Deactivate the view (currently a stub)."""
        # No-op for now
