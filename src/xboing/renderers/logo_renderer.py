"""Stateless renderer for a logo image centered at a given y."""

from typing import Optional, Tuple

import pygame


class LogoRenderer:
    """Stateless renderer for a logo image centered at a given y."""

    def __init__(
        self,
        logo_image: Optional[pygame.Surface],
        max_width: int = 320,
        max_height: int = 100,
        fallback_text: str = "XBoing",
        font: Optional[pygame.font.Font] = None,
        color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        """
        Initialize the LogoRenderer.

        Args:
            logo_image (Optional[pygame.Surface]): The logo image to render.
            max_width (int): Maximum width for scaling the logo.
            max_height (int): Maximum height for scaling the logo.
            fallback_text (str): Text to render if logo_image is None.
            font (Optional[pygame.font.Font]): Font for fallback text.
            color (tuple[int, int, int]): Color for fallback text.

        """
        self.logo_image = logo_image
        self.max_width = max_width
        self.max_height = max_height
        self.fallback_text = fallback_text
        self.font = font
        self.color = color

    def render(
        self,
        surface: pygame.Surface,
        center_x: int,
        y: int,
        **kwargs: object,
    ) -> int:
        """
        Draw the logo (or fallback text) centered at (center_x, y). Returns the new y after drawing.

        Args:
            surface (pygame.Surface): The surface to draw on.
            center_x (int): The x-coordinate to center the logo.
            y (int): The y-coordinate to start drawing.

        Returns:
            int: The new y position after drawing the logo.

        """
        if self.logo_image:
            logo_w, logo_h = self.logo_image.get_width(), self.logo_image.get_height()
            scale = min(self.max_width / logo_w, self.max_height / logo_h, 1.0)
            scaled_w, scaled_h = int(logo_w * scale), int(logo_h * scale)
            logo_surf = pygame.transform.smoothscale(
                self.logo_image, (scaled_w, scaled_h)
            )
            logo_rect = logo_surf.get_rect(center=(center_x, y + scaled_h // 2))
            surface.blit(logo_surf, logo_rect)
            return logo_rect.bottom + 10
        if self.font:
            logo_surf = self.font.render(self.fallback_text, True, self.color)
            logo_rect = logo_surf.get_rect(
                center=(center_x, y + logo_surf.get_height() // 2)
            )
            surface.blit(logo_surf, logo_rect)
            return logo_rect.bottom + 10
        # kwargs is unused, but required for interface compatibility
        _ = kwargs  # noqa: W0613
        return y
