"""UI view for displaying the level complete screen in XBoing."""

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame

from xboing.engine.events import (
    ApplauseEvent,
    BonusCollectedEvent,
    DohSoundEvent,
    KeySoundEvent,
    TimerUpdatedEvent,
    post_level_title_message,
)
from xboing.engine.graphics import Renderer
from xboing.game.game_state import GameState
from xboing.game.level_manager import LevelManager
from xboing.layout.game_layout import GameLayout
from xboing.renderers.bullet_row_renderer import BulletRowRenderer
from xboing.renderers.composite_renderer import CompositeRenderer
from xboing.renderers.row_renderer import RowRenderer, TextRowRenderer
from xboing.utils.asset_loader import load_image
from xboing.utils.asset_paths import get_asset_path

from .view import View

REVEAL_DELAY_MS = 3000  # Default delay, but now per-element
BULLET_ANIM_DELAY_MS = 300  # ms per bullet in the animation


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
        self.super_bonus: int
        self.level_bonus: int
        self.bullet_bonus: int
        self.time_bonus: int
        self.total_bonus: int
        self.final_score: int
        self.time_remaining: int
        self.message: str = "- Bonus Tally -"
        self.reveal_step: int = 0
        self.reveal_timer: float = 0.0
        self.reveal_delay_ms: int = REVEAL_DELAY_MS
        self.bullet_bonus_animating: bool = False
        self.bullet_bonus_total: int = 0
        self.bullet_bonus_shown: int = 0
        self.bullet_bonus_timer: float = 0.0
        self.logger = logging.getLogger("xboing.ui.LevelCompleteView")

        # Load and cache icons using asset loader and asset paths
        bonus_coin_path = get_asset_path("images/blocks/bonus1.png")
        bullet_path = get_asset_path("images/guns/bullet.png")
        self._bonus_coin_img = load_image(bonus_coin_path, alpha=True, scale=(27, 27))
        self._bullet_img = load_image(bullet_path, alpha=True, scale=(16, 32))

        # Font definitions for drawing
        self._fonts = self._initialize_fonts()

        # Spacing constants
        self.spacing = 12
        self.icon_spacing = 16

        # Renderer list and composite renderer
        self.row_renderers_with_y: List[Tuple[RowRenderer, int]] = []
        self.composite_renderer: Optional[CompositeRenderer] = None
        self._row_events: List[Optional[Any]] = []
        self._row_delays: List[int] = []

    @staticmethod
    def _initialize_fonts() -> Dict[str, pygame.font.Font]:
        """Initialize and return fonts used for rendering text."""
        return {
            "title": pygame.font.SysFont("Arial", 24),
            "message": pygame.font.SysFont("Arial", 16),
            "bonus": pygame.font.SysFont("Arial", 15),
            "rank": pygame.font.SysFont("Arial", 16),
            "prompt": pygame.font.SysFont("Arial", 16),
        }

    def _compute_bonuses(self) -> None:
        """Gather stats and compute bonuses for the level complete screen."""
        self.level_num = self.game_state.get_level_num()
        self.level_title = str(
            self.level_manager.get_level_info().get("title", f"Level {self.level_num}")
        )
        # Coin bonus
        # coins = self.game_state.level_state.get_bonus_coins_collected()
        self.coin_bonus = self.game_state.level_state.calculate_coin_bonus()

        # Super bonus
        self.super_bonus = self.game_state.level_state.calculate_super_bonus()

        # Level bonus
        self.level_bonus = self.game_state.level_state.calculate_level_bonus()

        # Bullet bonus
        bullets = self.game_state.get_ammo()
        self.bullet_bonus = self.game_state.level_state.calculate_bullet_bonus(bullets)

        # Time bonus
        self.time_remaining = self.game_state.level_state.get_bonus_time()
        self.time_bonus = self.game_state.level_state.calculate_time_bonus()

        # Total bonus
        self.total_bonus = self.game_state.level_state.calculate_all_bonuses(bullets)

        # Add total bonus to score
        self.final_score = self.game_state.score

    def _prepare_renderers(self) -> None:
        """Prepare the list of (renderer, y) pairs, events, and delays for the level complete screen, using pixel-perfect y-coordinates."""
        self.row_renderers_with_y = []
        self._row_events = []
        self._row_delays = []
        y_coords = [
            176,  # - Level 1 - (bottom)
            229,  # Congratulations on finishing this level.
            295,  # Sorry, no bonus coins collected.
            369,  # Level bonus - level 1 x 100 = 100 points
            417,  # [Bullets row] (bottom)
            466,  # Time bonus - ...
            495,  # You are currently ranked ...
            530,  # Prepare for level ...
            560,  # Press space for next level
        ]
        idx = 0
        # Title row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text=f"- Level {self.level_num} -",
                    font=self._fonts["title"],
                    color=(255, 0, 0),
                ),
                y_coords[idx],
            )
        )
        self._row_events.append(None)
        self._row_delays.append(500)
        idx += 1
        # Congratulations row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text="Congratulations on finishing this level.",
                    font=self._fonts["message"],
                    color=(255, 255, 255),
                ),
                y_coords[idx],
            )
        )
        self._row_events.append(ApplauseEvent())
        self._row_delays.append(1500)
        idx += 1
        # Bonus coin row
        coins = self.game_state.level_state.get_bonus_coins_collected()
        if coins == 0:
            self.row_renderers_with_y.append(
                (
                    TextRowRenderer(
                        text="Sorry, no bonus coins collected.",
                        font=self._fonts["message"],
                        color=(0, 0, 255),
                    ),
                    y_coords[idx],
                )
            )
            self._row_events.append(DohSoundEvent())
            self._row_delays.append(1500)
        else:
            self.row_renderers_with_y.append(
                (
                    TextRowRenderer(
                        text="Bonus coins collected!",
                        font=self._fonts["message"],
                        color=(0, 128, 255),
                        icon=self._bonus_coin_img,
                        icon_offset=8,
                    ),
                    y_coords[idx],
                )
            )
            self._row_events.append(BonusCollectedEvent())
            self._row_delays.append(1500)
        idx += 1
        # Level bonus row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text=f"Level bonus - level {self.level_num} x 100 = {self.level_bonus} points",
                    font=self._fonts["bonus"],
                    color=(255, 255, 0),
                ),
                y_coords[idx],
            )
        )
        self._row_events.append(BonusCollectedEvent())
        self._row_delays.append(900)
        idx += 1
        # Bullet row (special y adjustment)
        bullet_img = pygame.transform.smoothscale(self._bullet_img, (7, 15))
        bullet_y = y_coords[idx] + 22 - bullet_img.get_height()
        self.row_renderers_with_y.append((BulletRowRenderer(bullet_img), bullet_y))
        self._row_events.append(None)  # Sound handled in update
        self._row_delays.append(700)
        idx += 1
        # Time bonus row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text=f"Time bonus - {self.time_remaining} seconds x 100 = {self.time_bonus} points",
                    font=self._fonts["bonus"],
                    color=(255, 255, 0),
                ),
                y_coords[idx],
            )
        )
        self._row_events.append(TimerUpdatedEvent(self.time_remaining))
        self._row_delays.append(1200)
        idx += 1
        # Rank row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text=f"You are currently ranked {0}.",
                    font=self._fonts["rank"],
                    color=(255, 0, 0),
                ),
                y_coords[idx],
            )
        )
        self._row_events.append(None)
        self._row_delays.append(1000)
        idx += 1
        # Prepare for next level row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text=f"Prepare for level {self.level_num + 1}",
                    font=self._fonts["message"],
                    color=(255, 255, 0),
                ),
                y_coords[idx],
            )
        )
        self._row_events.append(None)
        self._row_delays.append(800)
        idx += 1
        # Press space row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text="Press space for next level",
                    font=self._fonts["prompt"],
                    color=(214, 183, 144),
                ),
                y_coords[idx],
            )
        )
        self._row_events.append(None)
        self._row_delays.append(800)
        self.composite_renderer = CompositeRenderer(self.row_renderers_with_y)

    def activate(self) -> None:
        """Activate the view and recompute bonuses."""
        self.active = True
        self._compute_bonuses()
        self.reveal_step = 0
        self.reveal_timer = 0.0
        self._prepare_renderers()
        self.reveal_delay_ms = (
            self._row_delays[0] if self._row_delays else REVEAL_DELAY_MS
        )
        self.bullet_bonus_animating = False
        self.bullet_bonus_total = self.game_state.get_ammo()
        self.bullet_bonus_shown = 0
        self.bullet_bonus_timer = 0.0
        self.logger.debug(
            f"[activate] Called. row_renderers_with_y length: {len(self.row_renderers_with_y)}"
        )
        post_level_title_message(self.message)

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

    def update(self, delta_ms: float) -> None:
        """Update the gradual reveal of bonus/info messages, bullet animation, and fire sound events."""
        self.logger.debug(
            f"[update] Called. reveal_step: {self.reveal_step}, row_renderers_with_y length: {len(self.row_renderers_with_y)}"
        )
        if self.active and self.reveal_step < len(self.row_renderers_with_y):
            # Check if we're at the bullet row step
            bullet_row_idx = None
            for idx, (renderer, _) in enumerate(self.row_renderers_with_y):
                if isinstance(renderer, BulletRowRenderer):
                    bullet_row_idx = idx
                    break
            if bullet_row_idx is not None and self.reveal_step == bullet_row_idx:
                # Animate bullets one at a time
                if not self.bullet_bonus_animating:
                    self.bullet_bonus_animating = True
                    self.bullet_bonus_total = self.game_state.get_ammo()
                    self.bullet_bonus_shown = 0
                    self.bullet_bonus_timer = 0.0
                if self.bullet_bonus_shown < self.bullet_bonus_total:
                    self.bullet_bonus_timer += delta_ms
                    if self.bullet_bonus_timer >= BULLET_ANIM_DELAY_MS:
                        self.bullet_bonus_shown += 1
                        self.bullet_bonus_timer = 0.0
                        # Fire AmmoFiredEvent for sound
                        pygame.event.post(
                            pygame.event.Event(
                                pygame.USEREVENT,
                                {"event": KeySoundEvent()},
                            )
                        )
                else:
                    self.bullet_bonus_animating = False
                    self.reveal_step += 1
                    # Set delay for next row if available
                    if self.reveal_step < len(self._row_delays):
                        self.reveal_delay_ms = self._row_delays[self.reveal_step]
                    else:
                        self.reveal_delay_ms = REVEAL_DELAY_MS
            else:
                # Normal reveal logic for other rows
                self.reveal_timer += delta_ms
                if self.reveal_timer >= self.reveal_delay_ms:
                    self.reveal_step += 1
                    self.reveal_timer = 0.0
                    self.logger.debug(
                        f"[update] reveal_step incremented: {self.reveal_step}"
                    )
                    # Fire event for this row if present
                    if self.reveal_step <= len(self._row_events):
                        event = self._row_events[self.reveal_step - 1]
                        if event is not None:
                            pygame.event.post(
                                pygame.event.Event(pygame.USEREVENT, {"event": event})
                            )
                        # Set delay for next row if available
                        if self.reveal_step < len(self._row_delays):
                            self.reveal_delay_ms = self._row_delays[self.reveal_step]
                        else:
                            self.reveal_delay_ms = REVEAL_DELAY_MS

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the level-complete overlay content using hardcoded y coordinates for pixel-perfect placement."""
        self.logger.debug(
            f"[draw] Called. reveal_step: {self.reveal_step}, row_renderers_with_y length: {len(self.row_renderers_with_y)}"
        )
        play_rect = self.layout.get_play_rect()
        center_x = play_rect.x + play_rect.width // 2
        if self.composite_renderer:
            self.composite_renderer.render(
                surface,
                center_x,
                self.reveal_step,
                bullet_count=self.bullet_bonus_shown,
            )
