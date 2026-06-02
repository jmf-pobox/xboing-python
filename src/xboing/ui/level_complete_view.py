"""UI view for displaying the level complete screen in XBoing."""

from collections.abc import Callable
from enum import Enum, auto
import logging

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

BULLET_ANIM_DELAY_FRAMES = 18  # Frames per bullet (300ms / 16.67ms ≈ 18 frames)

# Layout constants (from original bonus.c)
GAP = 30  # Vertical spacing unit between elements
Y_START = 135  # Starting Y position for bonus screen content


class BonusState(Enum):
    """Enum representing the states of the bonus screen animation."""

    BONUS_TEXT = auto()  # Display level title
    BONUS_SCORE = auto()  # Display congratulations message
    BONUS_DELAY = auto()  # Delay before bonus breakdown
    BONUS_COINS = auto()  # Display bonus coins
    BONUS_LEVEL = auto()  # Display level bonus
    BONUS_BULLETS = auto()  # Display bullet bonus
    BONUS_TIME = auto()  # Display time bonus
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
        on_advance_callback: Callable[[], None] | None = None,
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
        self.on_advance_callback: Callable[[], None] | None = on_advance_callback
        self.active: bool = False
        self.level_num: int
        self.coin_bonus: int
        self.super_bonus: int
        self.level_bonus: int
        self.bullet_bonus: int
        self.time_bonus: int
        self.time_remaining: int
        self.message: str = "- Bonus Tally -"

        # State machine variables
        self.current_state: BonusState = BonusState.BONUS_TEXT
        self.state_frame_counter: int = 0

        self.reveal_step: int = 0

        # Bullet animation variables
        self.bullet_bonus_animating: bool = False
        self.bullet_bonus_total: int = 0
        self.bullet_bonus_shown: int = 0
        self.bullet_bonus_frame_counter: int = 0

        # Score animation variables
        self.score_animation_active: bool = False
        self.score_animation_target: int = 0
        self.score_animation_accumulated: float = 0.0
        self.score_animation_increment_per_frame: float = 0.0

        self.logger = logging.getLogger("xboing.ui.LevelCompleteView")

        # Load and cache icons using asset loader and asset paths
        bonus_coin_path = get_asset_path("images/blocks/bonus1.png")
        bullet_path = get_asset_path("images/guns/bullet.png")
        self._bonus_coin_img = load_image(bonus_coin_path, alpha=True, scale=(27, 27))
        self._bullet_img = load_image(bullet_path, alpha=True, scale=(16, 32))

        # Font definitions for drawing
        self._fonts = self._initialize_fonts()

        # Renderer list and composite renderer
        self.row_renderers_with_y: list[tuple[RowRenderer, int]] = []
        self.composite_renderer: CompositeRenderer | None = None

    @staticmethod
    def _initialize_fonts() -> dict[str, pygame.font.Font]:
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
        self.coin_bonus = self.game_state.level_state.calculate_coin_bonus()
        self.super_bonus = self.game_state.level_state.calculate_super_bonus()
        self.level_bonus = self.game_state.level_state.calculate_level_bonus()
        bullets = self.game_state.get_ammo()
        self.bullet_bonus = self.game_state.level_state.calculate_bullet_bonus(bullets)
        self.time_remaining = self.game_state.level_state.get_bonus_time()
        self.time_bonus = self.game_state.level_state.calculate_time_bonus()

    def _prepare_renderers(self) -> None:
        """Prepare the list of (renderer, y) pairs for the level complete screen."""
        self.row_renderers_with_y = []

        # Dynamic Y positioning using font metrics (from original bonus.c)
        ypos = Y_START

        # Title row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text=f"- Level {self.level_num} -",
                    font=self._fonts["title"],
                    color=(255, 0, 0),
                ),
                ypos,
            )
        )
        ypos += self._fonts["title"].get_ascent() + GAP
        # Congratulations row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text="Congratulations on finishing this level.",
                    font=self._fonts["message"],
                    color=(255, 255, 255),
                ),
                ypos,
            )
        )
        ypos += self._fonts["message"].get_ascent() + int(GAP * 1.5)  # 1.5x spacing

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
                    ypos,
                )
            )
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
                    ypos,
                )
            )
        ypos += self._fonts["message"].get_ascent() + int(GAP * 1.5)  # 1.5x spacing
        # Level bonus row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text=f"Level bonus - level {self.level_num} x 100 = {self.level_bonus} points",
                    font=self._fonts["bonus"],
                    color=(255, 255, 0),
                ),
                ypos,
            )
        )
        ypos += self._fonts["bonus"].get_ascent() + GAP

        # Bullet row
        bullet_img = pygame.transform.smoothscale(self._bullet_img, (7, 15))
        self.row_renderers_with_y.append((BulletRowRenderer(bullet_img), ypos))
        ypos += bullet_img.get_height() + GAP

        # Time bonus row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text=f"Time bonus - {self.time_remaining} seconds x 100 = {self.time_bonus} points",
                    font=self._fonts["bonus"],
                    color=(255, 255, 0),
                ),
                ypos,
            )
        )
        ypos += self._fonts["bonus"].get_ascent() + GAP

        # Rank row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text=f"You are currently ranked {0}.",
                    font=self._fonts["rank"],
                    color=(255, 0, 0),
                ),
                ypos,
            )
        )
        ypos += self._fonts["rank"].get_ascent() + GAP

        # Prepare for the next level row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text=f"Prepare for level {self.level_num + 1}",
                    font=self._fonts["message"],
                    color=(255, 255, 0),
                ),
                ypos,
            )
        )
        ypos += self._fonts["message"].get_ascent() + GAP

        # Press the spacebar row
        self.row_renderers_with_y.append(
            (
                TextRowRenderer(
                    text="Press space for next level",
                    font=self._fonts["prompt"],
                    color=(214, 183, 144),
                ),
                ypos,
            )
        )
        self.composite_renderer = CompositeRenderer(self.row_renderers_with_y)

    def activate(self) -> None:
        """Activate the view and recompute bonuses."""
        self.active = True
        self._compute_bonuses()

        # Initialize state machine
        self.current_state = BonusState.BONUS_TEXT
        self.state_frame_counter = 0

        self.reveal_step = 0
        self._prepare_renderers()

        # Initialize bullet animation
        self.bullet_bonus_animating = False
        self.bullet_bonus_total = self.game_state.get_ammo()
        self.bullet_bonus_shown = 0
        self.bullet_bonus_frame_counter = 0

        # Initialize score animation
        self.score_animation_active = False
        self.score_animation_target = 0
        self.score_animation_accumulated = 0.0
        self.score_animation_increment_per_frame = 0.0

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
        """Get the next state in the bonus screen state machine.

        Args:
        ----
            current (BonusState): The current state.

        Returns:
        -------
            BonusState: The next state in sequence.

        """
        transitions: dict[BonusState, BonusState] = {
            BonusState.BONUS_TEXT: BonusState.BONUS_SCORE,
            BonusState.BONUS_SCORE: BonusState.BONUS_DELAY,
            BonusState.BONUS_DELAY: BonusState.BONUS_COINS,
            BonusState.BONUS_COINS: BonusState.BONUS_LEVEL,
            BonusState.BONUS_LEVEL: BonusState.BONUS_BULLETS,
            BonusState.BONUS_BULLETS: BonusState.BONUS_TIME,
            BonusState.BONUS_TIME: BonusState.BONUS_RANK,
            BonusState.BONUS_RANK: BonusState.BONUS_PREPARE,
            BonusState.BONUS_PREPARE: BonusState.BONUS_FINISH,
        }
        return transitions.get(current, BonusState.BONUS_FINISH)

    def _get_state_duration_frames(self, state: BonusState) -> int:
        """Get the frame duration for a given bonus state.

        Args:
        ----
            state (BonusState): The state to get duration for.

        Returns:
        -------
            int: Number of frames this state should last.

        """
        # Map states to their durations (in frames at 60 FPS)
        if state == BonusState.BONUS_TEXT:
            return 30  # Title row
        elif state == BonusState.BONUS_SCORE:
            return 90  # Congratulations row
        elif state == BonusState.BONUS_DELAY:
            return 0  # No delay, transition immediately
        elif state == BonusState.BONUS_COINS:
            return 90  # Bonus coin row
        elif state == BonusState.BONUS_LEVEL:
            return 54  # Level bonus row
        elif state == BonusState.BONUS_BULLETS:
            # Dynamic based on bullet count * frames per bullet
            return self.bullet_bonus_total * BULLET_ANIM_DELAY_FRAMES
        elif state == BonusState.BONUS_TIME:
            return 72  # Time bonus row
        elif state == BonusState.BONUS_RANK:
            return 60  # Rank row
        elif state == BonusState.BONUS_PREPARE:
            return 48  # Prepare for next level row
        else:  # BONUS_FINISH
            return 0

    def _get_state_reveal_step(self, state: BonusState) -> int:
        """Map BonusState to reveal_step index for rendering compatibility.

        Args:
        ----
            state (BonusState): The current state.

        Returns:
        -------
            int: The reveal_step index (how many rows to show).

        """
        # Map states to reveal_step indices (0-based: reveal_step=N renders rows 0..N)
        if state == BonusState.BONUS_TEXT:
            return 0  # Show title row
        elif state == BonusState.BONUS_SCORE:
            return 1  # Show title + congratulations
        elif state == BonusState.BONUS_DELAY:
            return 1  # Keep showing title + congratulations
        elif state == BonusState.BONUS_COINS:
            return 2  # Show up to coin row
        elif state == BonusState.BONUS_LEVEL:
            return 3  # Show up to level bonus row
        elif state == BonusState.BONUS_BULLETS:
            return 4  # Show up to bullet row
        elif state == BonusState.BONUS_TIME:
            return 5  # Show up to time bonus row
        elif state == BonusState.BONUS_RANK:
            return 6  # Show up to rank row
        elif state == BonusState.BONUS_PREPARE:
            return 7  # Show up to prepare row
        else:  # BONUS_FINISH
            return 8  # Show all rows

    def _start_score_animation(self, bonus_amount: int, duration_frames: int) -> None:
        """Start animating score increase for a bonus.

        Args:
        ----
            bonus_amount (int): The total bonus points to add.
            duration_frames (int): Number of frames over which to animate.

        """
        if bonus_amount > 0 and duration_frames > 0:
            self.score_animation_active = True
            self.score_animation_target = self.game_state.score + bonus_amount
            self.score_animation_accumulated = 0.0
            self.score_animation_increment_per_frame = bonus_amount / duration_frames
            self.logger.debug(
                f"Starting score animation: {bonus_amount} points over {duration_frames} frames"
            )

    def _update_score_animation(self) -> None:
        """Update score animation by one frame, incrementing score gradually."""
        if not self.score_animation_active:
            return

        # Accumulate fractional score
        self.score_animation_accumulated += self.score_animation_increment_per_frame

        # Add integer portion to score
        score_to_add = int(self.score_animation_accumulated)
        if score_to_add > 0:
            self.score_animation_accumulated -= score_to_add

            # Don't exceed target
            new_score = self.game_state.score + score_to_add
            if new_score >= self.score_animation_target:
                score_to_add = self.score_animation_target - self.game_state.score
                new_score = self.score_animation_target
                self.score_animation_active = False

            # Update score and post event
            if score_to_add > 0:
                score_events = self.game_state.add_score(score_to_add)
                for event in score_events:
                    pygame.event.post(
                        pygame.event.Event(pygame.USEREVENT, {"event": event})
                    )

    def update(self, delta_ms: float) -> None:
        """Update state machine, score animation, and bonus screen progression."""
        if not self.active or self.current_state == BonusState.BONUS_FINISH:
            return

        self.logger.debug(
            f"[update] state={self.current_state}, frame={self.state_frame_counter}"
        )

        # Update score animation every frame
        self._update_score_animation()

        # Special handling for BONUS_BULLETS state (bullet animation)
        if self.current_state == BonusState.BONUS_BULLETS:
            if not self.bullet_bonus_animating:
                self.bullet_bonus_animating = True
                self.bullet_bonus_shown = 0
                self.bullet_bonus_frame_counter = 0

            if self.bullet_bonus_shown < self.bullet_bonus_total:
                self.bullet_bonus_frame_counter += 1
                if self.bullet_bonus_frame_counter >= BULLET_ANIM_DELAY_FRAMES:
                    self.bullet_bonus_shown += 1
                    self.bullet_bonus_frame_counter = 0
                    # Fire sound event for each bullet
                    pygame.event.post(
                        pygame.event.Event(
                            pygame.USEREVENT,
                            {"event": KeySoundEvent()},
                        )
                    )
            else:
                # Bullets animation complete, transition to next state
                self.bullet_bonus_animating = False
                self._transition_to_next_state()
                return

        # Check if current state duration has elapsed
        state_duration = self._get_state_duration_frames(self.current_state)
        if state_duration == 0 or self.state_frame_counter >= state_duration:
            self._transition_to_next_state()
        else:
            # Increment frame counter
            self.state_frame_counter += 1

    def _transition_to_next_state(self) -> None:
        """Transition to the next state, fire events, and start animations."""
        next_state = self._get_next_state(self.current_state)

        self.logger.debug(f"Transitioning from {self.current_state} to {next_state}")

        # Update state
        self.current_state = next_state
        self.state_frame_counter = 0

        # Update reveal_step for rendering
        self.reveal_step = self._get_state_reveal_step(next_state)

        # Fire events and start animations based on new state
        if next_state == BonusState.BONUS_TEXT:
            # Post title event (none currently)
            pass
        elif next_state == BonusState.BONUS_SCORE:
            # Post congratulations event
            pygame.event.post(
                pygame.event.Event(pygame.USEREVENT, {"event": ApplauseEvent()})
            )
        elif next_state == BonusState.BONUS_COINS:
            # Post coin event and start score animation
            coins = self.game_state.level_state.get_bonus_coins_collected()
            if coins > 0:
                pygame.event.post(
                    pygame.event.Event(
                        pygame.USEREVENT, {"event": BonusCollectedEvent()}
                    )
                )
                self._start_score_animation(
                    self.coin_bonus, self._get_state_duration_frames(next_state)
                )
            else:
                pygame.event.post(
                    pygame.event.Event(pygame.USEREVENT, {"event": DohSoundEvent()})
                )
        elif next_state == BonusState.BONUS_LEVEL:
            # Post level bonus event and start score animation
            pygame.event.post(
                pygame.event.Event(pygame.USEREVENT, {"event": BonusCollectedEvent()})
            )
            self._start_score_animation(
                self.level_bonus, self._get_state_duration_frames(next_state)
            )
        elif next_state == BonusState.BONUS_BULLETS:
            self._start_score_animation(
                self.bullet_bonus, self._get_state_duration_frames(next_state)
            )
        elif next_state == BonusState.BONUS_TIME:
            # Post time bonus event and start score animation
            pygame.event.post(
                pygame.event.Event(
                    pygame.USEREVENT, {"event": TimerUpdatedEvent(self.time_remaining)}
                )
            )
            self._start_score_animation(
                self.time_bonus, self._get_state_duration_frames(next_state)
            )
        elif next_state == BonusState.BONUS_FINISH:
            # All done
            self.logger.debug("Bonus screen animation complete")

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
