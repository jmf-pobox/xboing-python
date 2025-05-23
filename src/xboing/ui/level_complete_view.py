"""UI view for displaying the level complete screen in XBoing."""

from typing import Callable, Dict, List, Optional, Tuple, Union

import pygame

from xboing.engine.graphics import Renderer
from xboing.game.game_state import GameState
from xboing.game.level_manager import LevelManager
from xboing.layout.game_layout import GameLayout
from xboing.utils.asset_loader import load_image
from xboing.utils.asset_paths import get_asset_path

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
        self.super_bonus: int
        self.level_bonus: int
        self.bullet_bonus: int
        self.time_bonus: int
        self.total_bonus: int
        self.final_score: int
        self.time_remaining: int

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
            "title": pygame.font.SysFont("Arial", 32, bold=True),
            "message": pygame.font.SysFont("Arial", 18),
            "bonus": pygame.font.SysFont("Arial", 20, bold=True),
            "rank": pygame.font.SysFont("Arial", 18, bold=True),
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

    def _prepare_elements(self) -> List[Union[pygame.Surface, Tuple[str, str]]]:
        """Prepare all elements to be displayed on the level complete screen.

        Returns
        -------
            List of rendered text/image surfaces or placeholders for special elements.

        """
        bonus_coin_img = pygame.transform.smoothscale(self._bonus_coin_img, (22, 22))

        elements: List[Union[pygame.Surface, Tuple[str, str]]] = [
            self._fonts["title"].render(
                f"- Level {self.level_num} -", True, (255, 0, 0)
            ),
            self._fonts["message"].render(
                "Congratulations on finishing this level.", True, (255, 255, 255)
            ),
            bonus_coin_img,
            self._fonts["bonus"].render(
                f"Level bonus - level {self.level_num} x 100 ="
                f" {self.level_bonus} "
                f"points",
                True,
                (255, 255, 0),
            ),
            ("bullets", ""),  # Placeholder for the bullet row
            self._fonts["bonus"].render(
                f"Time bonus - {self.time_remaining} x 100 = "
                f"{self.time_bonus} "
                f"points",
                True,
                (255, 255, 0),
            ),
            self._fonts["rank"].render(
                f"You are currently ranked {0}.", True, (255, 0, 0)
            ),
            self._fonts["message"].render(
                f"Prepare for level {self.level_num + 1}", True, (255, 255, 255)
            ),
            self._fonts["prompt"].render(
                "Press space for next level", True, (255, 255, 255)
            ),
        ]
        return elements

    @staticmethod
    def _calculate_total_height(
        elements: List[Union[pygame.Surface, Tuple[str, str]]],
        bullet_height: int,
        spacing: int,
        icon_spacing: int,
    ) -> int:
        """Calculate the total height required for all elements.

        Args:
        ----
            elements (List[Union[pygame.Surface, Tuple[str, str]]]): The elements to display.
            bullet_height (int): The height of bullet images.
            spacing (int): Standard spacing between elements.
            icon_spacing (int): Extra spacing for icons.

        Returns:
        -------
            int: The total height needed.

        """
        total_height = 0
        for e in elements:
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
        """Draw the bullet row and return the new y position.

        Args:
        ----
            surface (pygame.Surface): The surface to draw on.
            center_x (int): The x-coordinate of the center.
            y (int): The current y position.
            bullet_img (pygame.Surface): The bullet image to draw.
            total_bullets (int): The number of bullets to draw.

        Returns:
        -------
            int: The new y position after drawing the bullets.

        """
        bullet_w, bullet_h = bullet_img.get_size()
        bullets_width = total_bullets * bullet_w
        start_x = center_x - bullets_width // 2

        for i in range(total_bullets):
            bx = start_x + i * bullet_w
            surface.blit(bullet_img, (bx, y))

        return y + bullet_h

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the level-complete overlay content, with improved spacing/formatting and correct icon usage."""
        play_rect = self.layout.get_play_rect()
        center_x = play_rect.x + play_rect.width // 2

        # Prepare all elements to be drawn
        elements = self._prepare_elements()

        # Prepare bullet image for calculations and drawing
        bullet_img = pygame.transform.smoothscale(self._bullet_img, (12, 24))
        bullet_height = bullet_img.get_height()

        # Calculate total height and center block vertically
        total_height = self._calculate_total_height(
            elements, bullet_height, self.spacing, self.icon_spacing
        )
        y = play_rect.y + (play_rect.height - total_height) // 2

        # Draw each element
        for element in elements:
            if isinstance(element, pygame.Surface):
                # Draw regular text/image element
                y = self._draw_centered_element(surface, element, center_x, y)
                y += self.spacing
            elif isinstance(element, tuple) and element[0] == "bullets":
                # Draw bullets row (special case)
                total_bullets = self.game_state.get_ammo()
                y = self._draw_bullets_row(
                    surface, center_x, y, bullet_img, total_bullets
                )
                y += self.spacing
