"""Graphics rendering abstraction over SDL2/pygame.

This module provides a clean interface for sprite rendering, animations,
and other graphical operations, abstracting the underlying pygame implementation.
"""

import logging
from typing import List, Optional, Tuple

import pygame


class Sprite:
    """Sprite class for rendering images with various transformations."""

    def __init__(
        self,
        surface: pygame.Surface,
        x: int = 0,
        y: int = 0,
        scale: float = 1.0,
        angle: float = 0.0,
    ) -> None:
        """Initialize a sprite.

        Args:
        ----
            surface (pygame.Surface): The image surface.
            x (int): X position.
            y (int): Y position.
            scale (float): Scale factor.
            angle (float): Rotation angle in degrees.

        """
        self.original_surface: pygame.Surface = surface
        self.surface: pygame.Surface = surface
        self.rect: pygame.Rect = surface.get_rect()
        self.x: float = x
        self.y: float = y
        self.scale: float = scale
        self.angle: float = angle
        self.visible: bool = True

        # Update rect position
        self.rect.x = int(x)
        self.rect.y = int(y)

    def set_position(self, x: float, y: float) -> None:
        """Set the sprite position."""
        self.x = x
        self.y = y
        self.rect.x = int(x)
        self.rect.y = int(y)

    def set_scale(self, scale: float) -> None:
        """Set the sprite scale."""
        self.scale = scale
        self._update_surface()

    def set_angle(self, angle: float) -> None:
        """Set the sprite rotation angle."""
        self.angle = angle
        self._update_surface()

    def _update_surface(self) -> None:
        """Update the surface based on scale and rotation."""
        if self.scale != 1.0:
            width: int = int(self.original_surface.get_width() * self.scale)
            height: int = int(self.original_surface.get_height() * self.scale)
            scaled: pygame.Surface = pygame.transform.scale(
                self.original_surface, (width, height)
            )
        else:
            scaled = self.original_surface

        if self.angle != 0:
            self.surface = pygame.transform.rotate(scaled, self.angle)
        else:
            self.surface = scaled

        # Update rect
        self.rect = self.surface.get_rect()
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the sprite to the target surface."""
        if self.visible:
            surface.blit(self.surface, self.rect)

    def get_rect(self) -> pygame.Rect:
        """Get the sprite's collision rectangle."""
        return self.rect


class AnimatedSprite(Sprite):
    """Sprite with frame-based animation capabilities."""

    def __init__(
        self,
        frames: List[pygame.Surface],
        frame_duration: int,
        x: int = 0,
        y: int = 0,
        scale: float = 1.0,
        angle: float = 0.0,
    ) -> None:
        """Initialize an animated sprite.

        Args:
        ----
            frames (List[pygame.Surface]): List of pygame.Surface objects for animation frames.
            frame_duration (int): Duration of each frame in milliseconds.
            x (int): X position.
            y (int): Y position.
            scale (float): Scale factor.
            angle (float): Rotation angle in degrees.

        """
        if not frames:
            raise ValueError("Frames list cannot be empty")

        # Initialize with the first frame
        super().__init__(frames[0], x, y, scale, angle)

        # Animation properties
        self.frames: List[pygame.Surface] = frames
        self.frame_duration: int = frame_duration
        self.current_frame: int = 0
        self.elapsed_time: int = 0
        self.playing: bool = False
        self.loop: bool = True

    def update(self, delta_ms: int) -> None:
        """Update the animation.

        Args:
        ----
            delta_ms (int): Time passed since last update in milliseconds.

        """
        if not self.playing:
            return

        self.elapsed_time += delta_ms

        if self.elapsed_time >= self.frame_duration:
            # Advance to the next frame
            self.elapsed_time = 0
            self.current_frame += 1

            # Handle loop or animation end
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.playing = False

            # Update the current surface
            self.original_surface = self.frames[self.current_frame]
            self._update_surface()

    def play(self, loop: bool = True) -> None:
        """Start the animation."""
        self.playing = True
        self.loop = loop

    def stop(self) -> None:
        """Stop the animation."""
        self.playing = False

    def reset(self) -> None:
        """Reset the animation to the first frame."""
        self.current_frame = 0
        self.elapsed_time = 0
        self.original_surface = self.frames[self.current_frame]
        self._update_surface()


class Renderer:
    """Main renderer class for managing drawing operations."""

    def __init__(self, window_surface: pygame.Surface) -> None:
        """Initialize the renderer.

        Args:
        ----
            window_surface (pygame.Surface): The main window surface.

        """
        self.logger: logging.Logger = logging.getLogger("xboing.Renderer")
        if window_surface is None:
            self.logger.error("Renderer initialized with None window_surface!")
        self.surface: pygame.Surface = window_surface
        self.width: int = window_surface.get_width()
        self.height: int = window_surface.get_height()
        self.background_color: Tuple[int, int, int] = (0, 0, 0)
        self.logger.info(f"Renderer initialized: {self.width}x{self.height}")

    def clear(self, color: Optional[Tuple[int, int, int]] = None) -> None:
        """Clear the renderer with the specified color."""
        self.surface.fill(color if color is not None else self.background_color)

    def draw_sprite(self, sprite: Sprite) -> None:
        """Draw a sprite to the renderer."""
        sprite.draw(self.surface)

    def draw_rect(
        self,
        rect: pygame.Rect,
        color: Tuple[int, int, int],
        filled: bool = True,
        width: int = 1,
    ) -> None:
        """Draw a rectangle."""
        if filled:
            pygame.draw.rect(self.surface, color, rect)
        else:
            pygame.draw.rect(self.surface, color, rect, width)

    def draw_line(
        self,
        start_pos: Tuple[int, int],
        end_pos: Tuple[int, int],
        color: Tuple[int, int, int],
        width: int = 1,
    ) -> None:
        """Draw a line."""
        pygame.draw.line(self.surface, color, start_pos, end_pos, width)

    def draw_text(
        self,
        text: str,
        font: pygame.font.Font,
        color: Tuple[int, int, int],
        x: int,
        y: int,
        centered: bool = False,
    ) -> pygame.Rect:
        """Draw text to the renderer.

        Args:
        ----
            text (str): The text to render.
            font (pygame.font.Font): The font to use.
            color (Tuple[int, int, int]): The color of the text.
            x (int): The x position.
            y (int): The y position.
            centered (bool, optional): Whether to center the text. Defaults to False.

        Returns:
        -------
            pygame.Rect: The rectangle of the rendered text.

        """
        text_surface: pygame.Surface = font.render(text, True, color)
        text_rect: pygame.Rect = text_surface.get_rect()

        if centered:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)

        self.surface.blit(text_surface, text_rect)
        return text_rect
