"""Defines row rendering interfaces and implementations.

This module provides the RowRenderer protocol that defines the interface for all row renderers,
as well as the TextRowRenderer implementation for rendering text rows with optional icons.
"""

from typing import Optional, Protocol, Tuple

import pygame


# pylint: disable=missing-function-docstring
class RowRenderer(Protocol):
    """Protocol for all row renderers."""

    def render(
        self, surface: pygame.Surface, center_x: int, y: int, **kwargs: object
    ) -> int:
        """
        Render the row at the given position. Implemented by subclasses.

        Args:
            surface (pygame.Surface): The surface to draw on.
            center_x (int): The x-coordinate of the row's center.
            y (int): The y-coordinate to start drawing.
            **kwargs: Additional arguments for renderer customization.

        Returns:
            int: The new y position after drawing the row.

        """
        ...


class TextRowRenderer:
    """Stateless renderer for a single text row, optionally with an icon."""

    def __init__(
        self,
        text: str,
        font: pygame.font.Font,
        color: Tuple[int, int, int],
        icon: Optional[pygame.Surface] = None,
        icon_offset: int = 0,
    ) -> None:
        """
        Initialize the TextRowRenderer.

        Args:
            text (str): The text to render.
            font (pygame.font.Font): The font to use.
            color (Tuple[int, int, int]): The color of the text.
            icon (Optional[pygame.Surface]): Optional icon to render left of the text.
            icon_offset (int): Space between icon and text.

        """
        self.text = text
        self.font = font
        self.color = color
        self.icon = icon
        self.icon_offset = icon_offset

    # pylint: disable=missing-function-docstring
    def render(
        self, surface: pygame.Surface, center_x: int, y: int, **kwargs: object
    ) -> int:
        """
        Render the row at the given position. Implemented by subclasses.

        Args:
            surface (pygame.Surface): The surface to draw on.
            center_x (int): The x-coordinate to of the row's center.
            y (int): The y-coordinate to start drawing.
            **kwargs: Additional arguments for renderer customization.

        Returns:
            int: The new y position after drawing the row.

        """
        # kwargs is unused but required for interface compatibility
        _ = kwargs

        # Render main text
        text_surf = self.font.render(self.text, True, self.color)
        text_rect = text_surf.get_rect(
            center=(center_x, y + text_surf.get_height() // 2)
        )

        # Render shadow text first (offset by 2,2 in black)
        shadow_surf = self.font.render(self.text, True, (0, 0, 0))
        shadow_rect = shadow_surf.get_rect(
            center=(center_x + 2, y + shadow_surf.get_height() // 2 + 2)
        )
        surface.blit(shadow_surf, shadow_rect)

        # Render icon if present
        if self.icon:
            icon_rect = self.icon.get_rect()
            icon_rect.right = text_rect.left - self.icon_offset
            icon_rect.centery = text_rect.centery
            surface.blit(self.icon, icon_rect)

        # Render main text on top of shadow
        surface.blit(text_surf, text_rect)
        return y + text_surf.get_height()
