"""AmmoDisplayComponent: UI component for displaying the player's current ammo (bullets) as bullet images, right-aligned with the lives display."""

import logging
from typing import List

import pygame

from xboing.engine.events import AmmoCollectedEvent, AmmoFiredEvent
from xboing.game.game_state import GameState
from xboing.layout.game_layout import GameLayout
from xboing.renderers.ammo_renderer import MAX_AMMO, AmmoRenderer


class AmmoDisplayComponent:
    """UI component for displaying the player's current ammo (bullets) as bullet images, right-aligned with the lives display."""

    def __init__(
        self,
        layout: GameLayout,
        ammo_display_util: AmmoRenderer,
        game_state: GameState,
        max_ammo: int = MAX_AMMO,
        lives_x: int = 365,
        lives_width: int = 96,  # e.g., 3 lives * 32px each
        lives_y: int = 12,
        lives_height: int = 32,
    ) -> None:
        """Initialize the AmmoDisplayComponent.

        Args:
        ----
            layout (GameLayout): The GameLayout instance.
            ammo_display_util (AmmoRenderer): The AmmoRenderer instance.
            game_state (GameState): The GameState instance (source of truth for ammo).
            max_ammo (int, optional): The maximum number of bullets to display. Defaults to 20.
            lives_x (int, optional): The x position of the lives display. Defaults to 365.
            lives_width (int, optional): The width of the lives display. Defaults to 96.
            lives_y (int, optional): The y position of the lives display. Defaults to 12.
            lives_height (int, optional): The height of the lives display. Defaults to 32.

        """
        self.layout = layout
        self.ammo_display_util = ammo_display_util
        self.game_state = game_state
        self.ammo: int = game_state.get_ammo()
        self.max_ammo: int = max_ammo
        self.lives_x: int = lives_x
        self.lives_width: int = lives_width
        self.lives_y: int = lives_y
        self.lives_height: int = lives_height
        self.logger = logging.getLogger("xboing.AmmoDisplayComponent")

    def handle_events(self, events: List[pygame.event.Event]) -> None:
        """Handle events and update ammo display when AmmoFiredEvent is received."""
        for event in events:
            if event.type == pygame.USEREVENT and (
                isinstance(event.event, (AmmoFiredEvent, AmmoCollectedEvent))
            ):
                self.ammo = self.game_state.get_ammo()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the ammo (bullets) display on the given surface."""
        ammo_surf = self.ammo_display_util.render(
            self.ammo, spacing=1, max_ammo=self.max_ammo
        )
        # Right-align ammo with lives display
        x = self.lives_x + self.lives_width - ammo_surf.get_width()
        y = self.lives_y + self.lives_height + 2  # 2px gap below lives
        self.logger.debug(f"Ammo display: x={x}, width={ammo_surf.get_width()}, y={y}")
        surface.blit(ammo_surf, (x, y))
