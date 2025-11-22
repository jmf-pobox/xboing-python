"""Stateless renderer for a row of bullets (animated)."""

import typing

import pygame


class BulletRowRenderer:
    """Stateless renderer for a row of bullets (animated)."""

    def __init__(self, bullet_img: pygame.Surface, spacing: int = 2) -> None:
        """
        Initialize the BulletRowRenderer.

        Args:
            bullet_img (pygame.Surface): The bullet image to render.
            spacing (int): The spacing between bullets in pixels.

        """
        self.bullet_img = bullet_img
        self.spacing = spacing

    def render(
        self,
        surface: pygame.Surface,
        center_x: int,
        y: int,
        **kwargs: object,
    ) -> int:
        """
        Draws bullet_count bullets centered at (center_x, y).
        Returns the new y after drawing.

        Args:
            surface (pygame.Surface): The surface to draw on.
            center_x (int): The x-coordinate of row's center
            y (int): The y-coordinate to start drawing.
            **kwargs: (bullet_count) The number of bullets to render.

        Returns:
            int: The new y position after drawing the row.

        """
        bullet_count = typing.cast("int", kwargs.get("bullet_count", 0))
        bullet_w, bullet_h = self.bullet_img.get_size()
        total_width = (
            bullet_count * bullet_w + (bullet_count - 1) * self.spacing
            if bullet_count > 0
            else 0
        )
        start_x = center_x - total_width // 2
        for i in range(bullet_count):
            bx = start_x + i * (bullet_w + self.spacing)
            surface.blit(self.bullet_img, (bx, y))
        return y + bullet_h
