"""UI view for displaying the level complete screen in XBoing."""

import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

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
from xboing.utils.asset_loader import load_image
from xboing.utils.asset_paths import get_asset_path

from .view import View

REVEAL_DELAY_MS = 3000  # Default delay, but now per-element
BULLET_ANIM_DELAY_MS = 300  # ms per bullet in the animation

BulletRowMarker = Tuple[str, str]
ElementType = Tuple[Union[pygame.Surface, BulletRowMarker], Optional[Any], int]


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
        self.bonus_elements: List[
            Tuple[Union[pygame.Surface, BulletRowMarker], object, int]
        ] = []
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

    def activate(self) -> None:
        """Activate the view and recompute bonuses."""
        self.active = True
        self._compute_bonuses()
        self.reveal_step = 0
        self.reveal_timer = 0.0
        self.bonus_elements = self._prepare_elements()
        self.reveal_delay_ms = (
            self.bonus_elements[0][2] if self.bonus_elements else REVEAL_DELAY_MS
        )
        self.bullet_bonus_animating = False
        self.bullet_bonus_total = self.game_state.get_ammo()
        self.bullet_bonus_shown = 0
        self.bullet_bonus_timer = 0.0
        self.logger.debug(
            f"[activate] Called. bonus_elements length: {len(self.bonus_elements)}"
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

    def _prepare_elements(
        self,
    ) -> List[Tuple[Union[pygame.Surface, BulletRowMarker], object, int]]:
        """Prepare all elements to be displayed on the level complete screen, with optional event and per-row delay."""
        elements: List[Tuple[Union[pygame.Surface, BulletRowMarker], object, int]] = [
            (
                self._fonts["title"].render(
                    f"- Level {self.level_num} -", True, (255, 0, 0)
                ),
                None,
                500,
            ),
            (
                self._fonts["message"].render(
                    "Congratulations on finishing this level.", True, (255, 255, 255)
                ),
                ApplauseEvent(),
                1500,
            ),
        ]

        # Bonus coin logic
        coins = self.game_state.level_state.get_bonus_coins_collected()
        if coins == 0:
            # Show message and fire sound event
            elements.append(
                (
                    self._fonts["message"].render(
                        "Sorry, no bonus coins collected.", True, (0, 0, 255)
                    ),
                    DohSoundEvent(),
                    1500,
                )
            )
        else:
            # No-op for now; bonus coins are not yet implemented as non-block elements
            pass

        elements += [
            (
                self._fonts["bonus"].render(
                    f"Level bonus - level {self.level_num} x 100 ="
                    f" {self.level_bonus} "
                    f"points",
                    True,
                    (255, 255, 0),
                ),
                BonusCollectedEvent(),
                900,
            ),
            (("bullets", ""), None, 700),  # Bullet row marker
            (
                self._fonts["bonus"].render(
                    f"Time bonus - {self.time_remaining} x 100 = "
                    f"{self.time_bonus} "
                    f"points",
                    True,
                    (255, 255, 0),
                ),
                TimerUpdatedEvent(self.time_remaining),
                1200,
            ),
            (
                self._fonts["rank"].render(
                    f"You are currently ranked {0}.", True, (255, 0, 0)
                ),
                None,
                1000,
            ),
            (
                self._fonts["message"].render(
                    f"Prepare for level {self.level_num + 1}", True, (255, 255, 255)
                ),
                None,
                800,
            ),
            (
                self._fonts["prompt"].render(
                    "Press space for next level", True, (255, 255, 255)
                ),
                None,
                800,
            ),
        ]
        return elements

    @staticmethod
    def _calculate_total_height(
        elements: List[Tuple[Union[pygame.Surface, BulletRowMarker], object]],
        bullet_height: int,
        spacing: int,
        icon_spacing: int,
    ) -> int:
        """Calculate the total height required for all elements.

        Args:
        ----
            elements (List[Tuple[Union[pygame.Surface, BulletRowMarker], object]]): The elements to display.
            bullet_height (int): The height of bullet images.
            spacing (int): Standard spacing between elements.
            icon_spacing (int): Extra spacing for icons.

        Returns:
        -------
            int: The total height needed.

        """
        total_height = 0
        for e, _ in elements:
            if isinstance(e, pygame.Surface):
                total_height += e.get_height()
            elif isinstance(e, tuple) and e[0] == "bullets":
                total_height += bullet_height

        # Add spacing between elements
        total_height += spacing * (len(elements) - 1)

        # Add extra spacing for icons
        total_height += icon_spacing

        return total_height

    @staticmethod
    def _draw_centered_element(
        surface: pygame.Surface, element: pygame.Surface, center_x: int, y: int
    ) -> int:
        """Draw an element centered horizontally and return the new y position.

        Args:
        ----
            surface (pygame.Surface): The surface to draw on.
            element (pygame.Surface): The element to draw.
            center_x (int): The x-coordinate of the center.
            y (int): The current y position.

        Returns:
        -------
            int: The new y position after drawing the element.

        """
        element_rect = element.get_rect(
            center=(center_x, y + element.get_height() // 2)
        )
        surface.blit(element, element_rect)
        return y + element.get_height()

    @staticmethod
    def _draw_bullets_row(
        surface: pygame.Surface,
        center_x: int,
        y: int,
        bullet_img: pygame.Surface,
        total_bullets: int,
    ) -> int:
        """Draw the bullet row and return the new y position."""
        bullet_w, bullet_h = bullet_img.get_size()
        spacing = 2  # 1px between bullets
        bullets_width = total_bullets * bullet_w + (total_bullets - 1) * spacing
        start_x = center_x - bullets_width // 2

        for i in range(total_bullets):
            bx = start_x + i * (bullet_w + spacing)
            surface.blit(bullet_img, (bx, y))

        return y + bullet_h

    def update(self, delta_ms: float) -> None:
        """Update the gradual reveal of bonus/info messages, bullet animation, and fire sound events."""
        self.logger.debug(
            f"[update] Called. reveal_step: {self.reveal_step}, bonus_elements length: {len(self.bonus_elements)}"
        )
        if self.active and self.reveal_step < len(self.bonus_elements):
            # Check if we're at the bullet row step
            bullet_row_idx = None
            for idx, (element, _, _) in enumerate(self.bonus_elements):
                if isinstance(element, tuple) and element[0] == "bullets":
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
                    if self.reveal_step < len(self.bonus_elements):
                        self.reveal_delay_ms = self.bonus_elements[self.reveal_step][2]
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
                    if self.reveal_step <= len(self.bonus_elements):
                        _, event, _ = self.bonus_elements[self.reveal_step - 1]
                        if event is not None:
                            pygame.event.post(
                                pygame.event.Event(pygame.USEREVENT, {"event": event})
                            )
                        # Set delay for next row if available
                        if self.reveal_step < len(self.bonus_elements):
                            self.reveal_delay_ms = self.bonus_elements[
                                self.reveal_step
                            ][2]
                        else:
                            self.reveal_delay_ms = REVEAL_DELAY_MS

    def _prepare_elements_with_y(self) -> List[ElementType]:
        """Prepare all elements to be displayed on the level complete screen, with hardcoded y coordinates for pixel-perfect placement."""
        # Y coordinates from the C version ruler overlay (in px from window top)
        y_coords = [
            (210 - 34),  # - Level 1 - (bottom)
            (260 - 31),  # Congratulations on finishing this level.
            (300 - 5),  # Sorry, no bonus coins collected.
            (350 + 19),  # Level bonus - level 1 x 100 = 100 points
            (400 + 17),  # [Bullets row] (bottom)
            (450 + 16),  # Time bonus - ...
            (500 - 5),  # You are currently ranked ...
            (540 - 10),  # Prepare for level ...
            560,  # Press space for next level
        ]
        elements: List[ElementType] = []
        idx = 0
        # Title
        elements.append(
            (
                self._fonts["title"].render(
                    f"- Level {self.level_num} -", True, (255, 0, 0)
                ),
                None,
                y_coords[idx],
            )
        )
        idx += 1
        # Congratulations
        elements.append(
            (
                self._fonts["message"].render(
                    "Congratulations on finishing this level.", True, (255, 255, 255)
                ),
                ApplauseEvent(),
                y_coords[idx],
            )
        )
        idx += 1
        # Bonus coin logic
        coins = self.game_state.level_state.get_bonus_coins_collected()
        if coins == 0:
            elements.append(
                (
                    self._fonts["message"].render(
                        "Sorry, no bonus coins collected.", True, (0, 0, 255)
                    ),
                    DohSoundEvent(),
                    y_coords[idx],
                )
            )
        else:
            elements.append(
                (
                    self._fonts["message"].render(
                        "Bonus coins collected!", True, (0, 128, 255)
                    ),
                    BonusCollectedEvent(),
                    y_coords[idx],
                )
            )
        idx += 1
        # Level bonus
        elements.append(
            (
                self._fonts["bonus"].render(
                    f"Level bonus - level {self.level_num} x 100 = {self.level_bonus} points",
                    True,
                    (255, 255, 0),
                ),
                BonusCollectedEvent(),
                y_coords[idx],
            )
        )
        idx += 1
        # Bullets row marker
        elements.append((("bullets", ""), None, y_coords[idx]))
        idx += 1
        # Time bonus
        elements.append(
            (
                self._fonts["bonus"].render(
                    f"Time bonus - {self.time_remaining} seconds x 100 = {self.time_bonus} points",
                    True,
                    (255, 255, 0),
                ),
                TimerUpdatedEvent(self.time_remaining),
                y_coords[idx],
            )
        )
        idx += 1
        # Rank
        elements.append(
            (
                self._fonts["rank"].render(
                    f"You are currently ranked {0}.", True, (255, 0, 0)
                ),
                None,
                y_coords[idx],
            )
        )
        idx += 1
        # Prepare for next level
        elements.append(
            (
                self._fonts["message"].render(
                    f"Prepare for level {self.level_num + 1}", True, (255, 255, 0)
                ),
                None,
                y_coords[idx],
            )
        )
        idx += 1
        # Press space
        elements.append(
            (
                self._fonts["prompt"].render(
                    "Press space for next level", True, (214, 183, 144)
                ),
                None,
                y_coords[idx],
            )
        )
        return elements

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the level-complete overlay content using hardcoded y coordinates for pixel-perfect placement."""
        self.logger.debug(
            f"[draw] Called. reveal_step: {self.reveal_step}, bonus_elements length: {len(self.bonus_elements)}"
        )
        play_rect = self.layout.get_play_rect()
        center_x = play_rect.x + play_rect.width // 2

        # Use the new elements structure with y coordinates
        elements = self._prepare_elements_with_y()
        # Reduce bullet size to match the C version
        bullet_img = pygame.transform.smoothscale(self._bullet_img, (7, 15))

        for idx, (element, _, y) in enumerate(elements):
            if idx < self.reveal_step:
                if isinstance(element, pygame.Surface):
                    self._draw_centered_element(surface, element, center_x, y)
                elif isinstance(element, tuple) and element[0] == "bullets":
                    # For bullets row, y is the bottom of the row, so adjust upward by bullet height and add 22px adjustment
                    self._draw_bullets_row(
                        surface,
                        center_x,
                        y + 22 - bullet_img.get_height(),
                        bullet_img,
                        self.game_state.get_ammo(),
                    )
            elif idx == self.reveal_step:
                if (
                    isinstance(element, tuple)
                    and element[0] == "bullets"
                    and self.bullet_bonus_animating
                ):
                    self._draw_bullets_row(
                        surface,
                        center_x,
                        y + 22 - bullet_img.get_height(),
                        bullet_img,
                        self.bullet_bonus_shown,
                    )
                break
            else:
                break
