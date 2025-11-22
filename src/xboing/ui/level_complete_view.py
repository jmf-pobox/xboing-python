"""UI view for displaying the level complete screen in XBoing."""

from enum import Enum, auto
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

# Frame-based timing constants (assuming 60 FPS)
REVEAL_DELAY_FRAMES = 180  # Default delay (3000ms / 16.67ms ≈ 180 frames)
BULLET_ANIM_DELAY_FRAMES = 18  # Frames per bullet (300ms / 16.67ms ≈ 18 frames)


class BonusState(Enum):
    """Enum representing the states of the bonus screen animation."""

    BONUS_TEXT = auto()  # Display level title and congratulations
    BONUS_SCORE = auto()  # Display score (currently not used, but reserved for future)
    BONUS_DELAY = auto()  # Delay between elements
    BONUS_COINS = auto()  # Display bonus coins (skip if zero)
    BONUS_LEVEL = auto()  # Display level bonus
    BONUS_BULLETS = auto()  # Display bullet bonus (skip if zero)
    BONUS_TIME = auto()  # Display time bonus (skip if zero)
    BONUS_RANK = auto()  # Display player ranking
    BONUS_PREPARE = auto()  # Display prepare for next level
    BONUS_FINISH = auto()  # Completion state


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

        # State machine variables
        self.current_state: BonusState = BonusState.BONUS_TEXT
        self.state_frame_counter: int = 0

        # Legacy reveal system (kept for now for compatibility)
        self.reveal_step: int = 0
        self.frame_counter: int = 0
        self.reveal_frame_threshold: int = REVEAL_DELAY_FRAMES

        # Bullet animation variables
        self.bullet_bonus_animating: bool = False
        self.bullet_bonus_total: int = 0
        self.bullet_bonus_shown: int = 0
        self.bullet_bonus_frame_counter: int = 0

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
            560,  # Press space for the next level
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
        self._row_delays.append(30)  # 500ms -> 30 frames
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
        self._row_delays.append(90)  # 1500ms -> 90 frames
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
            self._row_delays.append(90)  # 1500ms -> 90 frames
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
            self._row_delays.append(90)  # 1500ms -> 90 frames
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
        self._row_delays.append(54)  # 900ms -> 54 frames
        idx += 1
        # Bullet row (special y adjustment)
        bullet_img = pygame.transform.smoothscale(self._bullet_img, (7, 15))
        bullet_y = y_coords[idx] + 22 - bullet_img.get_height()
        self.row_renderers_with_y.append((BulletRowRenderer(bullet_img), bullet_y))
        self._row_events.append(None)  # Sound handled in update
        self._row_delays.append(42)  # 700ms -> 42 frames
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
        self._row_delays.append(72)  # 1200ms -> 72 frames
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
        self._row_delays.append(60)  # 1000ms -> 60 frames
        idx += 1
        # Prepare for the next level row
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
        self._row_delays.append(48)  # 800ms -> 48 frames
        idx += 1
        # Press the spacebar row
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
        self._row_delays.append(48)  # 800ms -> 48 frames
        self.composite_renderer = CompositeRenderer(self.row_renderers_with_y)

    def activate(self) -> None:
        """Activate the view and recompute bonuses."""
        self.active = True
        self._compute_bonuses()

        # Initialize state machine
        self.current_state = BonusState.BONUS_TEXT
        self.state_frame_counter = 0

        # Initialize legacy reveal system
        self.reveal_step = 0
        self.frame_counter = 0
        self._prepare_renderers()
        self.reveal_frame_threshold = (
            self._row_delays[0] if self._row_delays else REVEAL_DELAY_FRAMES
        )

        # Initialize bullet animation
        self.bullet_bonus_animating = False
        self.bullet_bonus_total = self.game_state.get_ammo()
        self.bullet_bonus_shown = 0
        self.bullet_bonus_frame_counter = 0

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

    def _get_next_state(self, current: BonusState) -> BonusState:
        """Get the next state in the bonus screen state machine with conditional skipping.

        Args:
        ----
            current (BonusState): The current state.

        Returns:
        -------
            BonusState: The next state, potentially skipping states with zero bonuses.

        """
        # State transition map
        if current == BonusState.BONUS_TEXT:
            return BonusState.BONUS_SCORE
        elif current == BonusState.BONUS_SCORE:
            return BonusState.BONUS_DELAY
        elif current == BonusState.BONUS_DELAY:
            # Skip to BONUS_COINS, or skip if no coins
            if self.coin_bonus > 0:
                return BonusState.BONUS_COINS
            else:
                # Skip coins, go directly to level
                return BonusState.BONUS_LEVEL
        elif current == BonusState.BONUS_COINS:
            return BonusState.BONUS_LEVEL
        elif current == BonusState.BONUS_LEVEL:
            # Skip to BONUS_BULLETS, or skip if no bullets
            if self.bullet_bonus_total > 0:
                return BonusState.BONUS_BULLETS
            # Skip bullets, check time
            elif self.time_bonus > 0:
                return BonusState.BONUS_TIME
            else:
                # Skip time too, go to rank
                return BonusState.BONUS_RANK
        elif current == BonusState.BONUS_BULLETS:
            # Check if we should skip time bonus
            if self.time_bonus > 0:
                return BonusState.BONUS_TIME
            else:
                # Skip time, go to rank
                return BonusState.BONUS_RANK
        elif current == BonusState.BONUS_TIME:
            return BonusState.BONUS_RANK
        elif current == BonusState.BONUS_RANK:
            return BonusState.BONUS_PREPARE
        elif current == BonusState.BONUS_PREPARE:
            return BonusState.BONUS_FINISH
        else:  # BONUS_FINISH or unknown
            return BonusState.BONUS_FINISH

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
                # Animate bullets one at a time (frame-based)
                if not self.bullet_bonus_animating:
                    self.bullet_bonus_animating = True
                    self.bullet_bonus_total = self.game_state.get_ammo()
                    self.bullet_bonus_shown = 0
                    self.bullet_bonus_frame_counter = 0
                if self.bullet_bonus_shown < self.bullet_bonus_total:
                    self.bullet_bonus_frame_counter += 1
                    if self.bullet_bonus_frame_counter >= BULLET_ANIM_DELAY_FRAMES:
                        self.bullet_bonus_shown += 1
                        self.bullet_bonus_frame_counter = 0
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
                    self.frame_counter = 0
                    # Set delay for the next row if available
                    if self.reveal_step < len(self._row_delays):
                        self.reveal_frame_threshold = self._row_delays[self.reveal_step]
                    else:
                        self.reveal_frame_threshold = REVEAL_DELAY_FRAMES
            else:
                # Normal reveal logic for other rows (frame-based)
                self.frame_counter += 1
                if self.frame_counter >= self.reveal_frame_threshold:
                    self.reveal_step += 1
                    self.frame_counter = 0
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
                        # Set delay for the next row if available
                        if self.reveal_step < len(self._row_delays):
                            self.reveal_frame_threshold = self._row_delays[
                                self.reveal_step
                            ]
                        else:
                            self.reveal_frame_threshold = REVEAL_DELAY_FRAMES

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
