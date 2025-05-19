"""UI view for displaying the level complete screen in XBoing."""

from typing import Callable, Optional

import pygame

from xboing.engine.graphics import Renderer
from xboing.game.game_state import GameState
from xboing.game.level_manager import LevelManager
from xboing.layout.game_layout import GameLayout

from .view import View


class LevelCompleteView(View):
    """View for displaying the level complete overlay, including bonus breakdown and final score.

    Draws only within the play window region.
    """

    def __init__(
        self,
        layout: GameLayout,
        renderer: Renderer,
        font: pygame.font.Font,
        small_font: pygame.font.Font,
        game_state: GameState,
        level_manager: LevelManager,
        on_advance_callback: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize the LevelCompleteView.

        Args:
        ----
            layout (GameLayout): The GameLayout instance.
            renderer (Renderer): The main Renderer instance.
            font (pygame.font.Font): The main font for headlines.
            small_font (pygame.font.Font): The font for bonus breakdown.
            game_state (GameState): The current game state.
            level_manager (LevelManager): The level manager instance.
            on_advance_callback (Optional[Callable[[], None]]): Callback for advancing to the next level.

        """
        self.layout: GameLayout = layout
        self.renderer: Renderer = renderer
        self.font: pygame.font.Font = font
        self.small_font: pygame.font.Font = small_font
        self.game_state: GameState = game_state
        self.level_manager: LevelManager = level_manager
        self.on_advance_callback: Optional[Callable[[], None]] = on_advance_callback
        self.active: bool = False
        self.level_num: int
        self.level_title: str
        self.coin_bonus: int
        self.super_bonus: bool
        self.level_bonus: int
        self.bullet_bonus: int
        self.time_bonus: int
        self.total_bonus: int
        self.final_score: int
        self._compute_bonuses()

    def _compute_bonuses(self) -> None:
        """Gather stats and compute bonuses for the level complete screen."""
        self.level_num = self.game_state.level
        self.level_title = str(
            self.level_manager.get_level_info().get("title", f"Level {self.level_num}")
        )
        self.coin_bonus = 0  # TODO: integrate real coin bonus logic
        self.super_bonus = False
        self.level_bonus = self.level_num * 100  # Example
        self.bullet_bonus = 0  # TODO: integrate real bullet bonus logic
        self.time_bonus = self.level_manager.get_time_remaining() * 10  # Example
        self.total_bonus = (
            self.coin_bonus
            + (50000 if self.super_bonus else 0)
            + self.level_bonus
            + self.bullet_bonus
            + self.time_bonus
        )
        self.final_score = self.game_state.score + self.total_bonus

    def activate(self) -> None:
        """Activate the view and recompute bonuses."""
        self.active = True
        self._compute_bonuses()

    def deactivate(self) -> None:
        """Deactivate the view."""
        self.active = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a single Pygame event (advance on SPACE).

        Args:
        ----
            event (pygame.event.Event): The Pygame event to handle.

        """
        if (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_SPACE
            and self.on_advance_callback
        ):
            self.on_advance_callback()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the level complete overlay, bonus breakdown, and final score.

        Args:
        ----
            surface (pygame.Surface): The Pygame surface to draw on.

        """
        play_rect = self.layout.get_play_rect()
        overlay = pygame.Surface((play_rect.width, play_rect.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))  # Semi-transparent black
        surface.blit(overlay, play_rect.topleft)
        centerx = play_rect.width // 2
        y = 60
        # Headline
        headline = "LEVEL COMPLETE!"
        headline_surf = self.font.render(headline, True, (50, 255, 50))
        headline_rect = headline_surf.get_rect(center=(centerx, y))
        surface.blit(
            headline_surf,
            (play_rect.x + headline_rect.x, play_rect.y + headline_rect.y),
        )
        y = headline_rect.bottom + 20
        # Level title
        title_surf = self.small_font.render(self.level_title, True, (200, 200, 255))
        title_rect = title_surf.get_rect(center=(centerx, y))
        surface.blit(
            title_surf, (play_rect.x + title_rect.x, play_rect.y + title_rect.y)
        )
        y = title_rect.bottom + 30
        # Bonus breakdown
        lines = [
            f"Coin Bonus: {self.coin_bonus}",
            f"Super Bonus: {'50000' if self.super_bonus else '0'}",
            f"Level Bonus: {self.level_bonus}",
            f"Bullet Bonus: {self.bullet_bonus}",
            f"Time Bonus: {self.time_bonus}",
            f"Total Bonus: {self.total_bonus}",
            f"Final Score: {self.final_score}",
        ]
        for line in lines:
            line_surf = self.small_font.render(line, True, (255, 255, 200))
            line_rect = line_surf.get_rect(center=(centerx, y))
            surface.blit(
                line_surf, (play_rect.x + line_rect.x, play_rect.y + line_rect.y)
            )
            y = line_rect.bottom + 10
        # Prompt
        prompt = "Press SPACE for next level"
        prompt_surf = self.small_font.render(prompt, True, (200, 200, 200))
        prompt_rect = prompt_surf.get_rect(center=(centerx, play_rect.height - 40))
        surface.blit(
            prompt_surf, (play_rect.x + prompt_rect.x, play_rect.y + prompt_rect.y)
        )
