"""Provides a base class for views that render the play area background in the play window."""

import pygame

from xboing.layout.game_layout import GameLayout

from .view import View


class ViewWithBackground(View):
    """Base class for views that render the play area background in the play window."""

    def __init__(self, layout: GameLayout) -> None:
        self.layout = layout
        self._bg_index: int = 0  # Default background index

    def set_background(self, bg_index: int) -> None:
        """Set the background index for this view."""
        self._bg_index = bg_index

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the play area background (tiled image or color) in the play window using the current background index."""
        # Ensure the play area background is set to the correct background for this view
        self.layout.set_play_background(self._bg_index)
        play_rect = self.layout.get_play_rect()
        play_window = self.layout.play_window
        bg_surface = getattr(play_window, "bg_surface", None)
        bg_color = getattr(play_window, "bg_color", None)
        if bg_surface is not None:
            surface.blit(bg_surface, (play_rect.x, play_rect.y))
        elif bg_color is not None:
            pygame.draw.rect(surface, bg_color, play_rect)

    def activate(self) -> None:
        """Activate the view. The correct background index must be set via set_background() before activation."""
        # No background logic here; background is set via set_background()

    def deactivate(self) -> None:
        """Deactivate the view and restore the default space background."""
        self.layout.set_play_background_to_space()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle a single Pygame event (currently a stub)."""
