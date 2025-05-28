"""Composite renderer for orchestrating a sequence of row renderers."""

from typing import List, Tuple

import pygame

from .row_renderer import RowRenderer


class CompositeRenderer:
    """Orchestrate a sequence of row renderers, handling reveal/animation state and per-row y-coordinates."""

    def __init__(
        self,
        row_renderers_with_y: List[Tuple[RowRenderer, int]],
    ) -> None:
        """
        Initialize the CompositeRenderer.

        Args:
            row_renderers_with_y (List[Tuple[RowRenderer, int]]):
                The list of (row renderer, y) pairs to orchestrate.

        """
        self.row_renderers_with_y = row_renderers_with_y

    def render(
        self,
        surface: pygame.Surface,
        center_x: int,
        reveal_step: int,
        **kwargs: object,
    ) -> None:
        """
        Render up to reveal_step rows. Passes **kwargs to each renderer.

        Args:
            surface (pygame.Surface): The surface to draw on.
            center_x (int): The x-coordinate to center rows.
            reveal_step (int): The number of rows to reveal.
            **kwargs: Extra arguments for row renderers (e.g., bullet_count).

        """
        for idx, (renderer, y) in enumerate(self.row_renderers_with_y):
            if idx < reveal_step:
                renderer.render(surface, center_x, y, **kwargs)
            elif idx == reveal_step:
                renderer.render(surface, center_x, y, **kwargs)
                break
            else:
                break
