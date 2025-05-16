"""
Stateless renderer for displaying LED-style numbers using digit sprites.
Used by UI components for visual output.
"""

import logging
import os

import pygame

from utils.asset_paths import get_asset_path


def get_digits_dir():
    """Get the path to the digit images directory."""
    return get_asset_path("images/digits", create_dirs=True)


class DigitRenderer:
    """
    Stateless renderer for displaying LED-style numbers using digit sprites.
    Used by UI components for visual output.
    """

    logger = logging.getLogger("xboing.DigitRenderer")

    def __init__(self) -> None:
        """Initialize the DigitRenderer with loaded digit sprites."""
        self.digits = {}
        self._load_digits()
        self._surface_cache = {}
        if self.digits:
            self.digit_width = self.digits[0].get_width()
            self.digit_height = self.digits[0].get_height()
        else:
            self.digit_width = 30
            self.digit_height = 40

    def _load_digits(self):
        digits_dir = get_digits_dir()
        for i in range(10):
            digit_path = os.path.join(digits_dir, f"digit{i}.png")
            if os.path.exists(digit_path):
                self.digits[i] = pygame.image.load(digit_path).convert_alpha()
            else:
                self.logger.warning(f"Could not load digit image: {digit_path}")

    def render_number(
        self,
        number: int,
        spacing: int = 2,
        scale: float = 1.0,
        color: tuple[int, int, int] | None = None,
        width: int | None = None,
        right_justified: bool = False,
    ) -> pygame.Surface:
        """
        Render a number as a surface using digit sprites.

        Args:
            number (int): The number to render.
            spacing (int, optional): Spacing between digits. Defaults to 2.
            scale (float, optional): Scale factor for digit size. Defaults to 1.0.
            color (tuple[int, int, int] | None, optional): Color to tint digits. Defaults to None.
            width (int | None, optional): Minimum width (pads with spaces). Defaults to None.
            right_justified (bool, optional): Right-justify the number. Defaults to False.

        Returns:
            pygame.Surface: The rendered number as a surface.
        """
        number_str = str(number)
        if width is not None and len(number_str) < width:
            number_str = " " * (width - len(number_str)) + number_str
        cache_key = (number_str, spacing, scale, color, width, right_justified)
        if cache_key in self._surface_cache:
            return self._surface_cache[cache_key]
        scaled_width = int(self.digit_width * scale)
        total_width = (scaled_width * len(number_str)) + (
            spacing * (len(number_str) - 1)
        )
        scaled_height = int(self.digit_height * scale)
        surface = pygame.Surface((total_width, scaled_height), pygame.SRCALPHA)
        if right_justified and width is not None and len(number_str) < width:
            extra_width = (width - len(number_str)) * (scaled_width + spacing)
            x = extra_width
        else:
            x = 0
        for digit_char in number_str:
            if digit_char == " ":
                x += scaled_width + spacing
                continue
            try:
                digit = int(digit_char)
                if digit in self.digits:
                    digit_surface = self.digits[digit]
                    if scale != 1.0:
                        digit_surface = pygame.transform.smoothscale(
                            digit_surface, (scaled_width, scaled_height)
                        )
                    if color:
                        colored_surface = digit_surface.copy()
                        colored_surface.fill(
                            color, special_flags=pygame.BLEND_RGBA_MULT
                        )
                        digit_surface = colored_surface
                    surface.blit(digit_surface, (x, 0))
                    x += scaled_width + spacing
            except ValueError:
                x += scaled_width + spacing
        self._surface_cache[cache_key] = surface
        return surface

    def render_time(self, seconds, spacing=2, scale=1.0, colon_width=8, color=None):
        minutes = seconds // 60
        secs = seconds % 60
        time_str = f"{minutes:02d}:{secs:02d}"
        cache_key = (f"time_{time_str}", spacing, scale, colon_width, color)
        if cache_key in self._surface_cache:
            return self._surface_cache[cache_key]
        scaled_width = int(self.digit_width * scale)
        scaled_height = int(self.digit_height * scale)
        total_width = (scaled_width * 4) + (spacing * 3) + colon_width
        surface = pygame.Surface((total_width, scaled_height), pygame.SRCALPHA)
        colon_color = color if color else (255, 255, 0)
        x = 0
        for digit_char in f"{minutes:02d}":
            digit = int(digit_char)
            if digit in self.digits:
                digit_surface = self.digits[digit]
                if scale != 1.0:
                    digit_surface = pygame.transform.smoothscale(
                        digit_surface, (scaled_width, scaled_height)
                    )
                if color:
                    colored_surface = digit_surface.copy()
                    colored_surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
                    digit_surface = colored_surface
                surface.blit(digit_surface, (x, 0))
                x += scaled_width + spacing
        colon_y1 = scaled_height // 3
        colon_y2 = (scaled_height * 2) // 3
        colon_x = x
        pygame.draw.circle(
            surface, colon_color, (colon_x + colon_width // 2, colon_y1), 3
        )
        pygame.draw.circle(
            surface, colon_color, (colon_x + colon_width // 2, colon_y2), 3
        )
        x += colon_width + spacing
        for digit_char in f"{secs:02d}":
            digit = int(digit_char)
            if digit in self.digits:
                digit_surface = self.digits[digit]
                if scale != 1.0:
                    digit_surface = pygame.transform.smoothscale(
                        digit_surface, (scaled_width, scaled_height)
                    )
                if color:
                    colored_surface = digit_surface.copy()
                    colored_surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
                    digit_surface = colored_surface
                surface.blit(digit_surface, (x, 0))
                x += scaled_width + spacing
        self._surface_cache[cache_key] = surface
        return surface
