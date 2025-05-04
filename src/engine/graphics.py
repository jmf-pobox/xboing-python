"""
Graphics rendering abstraction over SDL2/pygame.

This module provides a clean interface for sprite rendering, animations,
and other graphical operations, abstracting the underlying pygame implementation.
"""

import pygame


class Sprite:
    """Sprite class for rendering images with various transformations."""

    def __init__(self, surface, x=0, y=0, scale=1.0, angle=0):
        """
        Initialize a sprite.

        Args:
            surface (pygame.Surface): The image surface
            x (int): X position
            y (int): Y position
            scale (float): Scale factor
            angle (float): Rotation angle in degrees
        """
        self.original_surface = surface
        self.surface = surface
        self.rect = surface.get_rect()
        self.x = x
        self.y = y
        self.scale = scale
        self.angle = angle
        self.visible = True

        # Update rect position
        self.rect.x = int(x)
        self.rect.y = int(y)

    def set_position(self, x, y):
        """Set the sprite position."""
        self.x = x
        self.y = y
        self.rect.x = int(x)
        self.rect.y = int(y)

    def set_scale(self, scale):
        """Set the sprite scale."""
        self.scale = scale
        self._update_surface()

    def set_angle(self, angle):
        """Set the sprite rotation angle."""
        self.angle = angle
        self._update_surface()

    def _update_surface(self):
        """Update the surface based on scale and rotation."""
        if self.scale != 1.0:
            width = int(self.original_surface.get_width() * self.scale)
            height = int(self.original_surface.get_height() * self.scale)
            scaled = pygame.transform.scale(self.original_surface, (width, height))
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

    def draw(self, surface):
        """Draw the sprite to the target surface."""
        if self.visible:
            surface.blit(self.surface, self.rect)

    def get_rect(self):
        """Get the sprite's collision rectangle."""
        return self.rect


class AnimatedSprite(Sprite):
    """Sprite with frame-based animation capabilities."""

    def __init__(self, frames, frame_duration, x=0, y=0, scale=1.0, angle=0):
        """
        Initialize an animated sprite.

        Args:
            frames (list): List of pygame.Surface objects for animation frames
            frame_duration (int): Duration of each frame in milliseconds
            x (int): X position
            y (int): Y position
            scale (float): Scale factor
            angle (float): Rotation angle in degrees
        """
        if not frames:
            raise ValueError("Frames list cannot be empty")

        # Initialize with the first frame
        super().__init__(frames[0], x, y, scale, angle)

        # Animation properties
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.elapsed_time = 0
        self.playing = False
        self.loop = True

    def update(self, delta_ms):
        """
        Update the animation.

        Args:
            delta_ms (int): Time passed since last update in milliseconds
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

    def play(self, loop=True):
        """Start the animation."""
        self.playing = True
        self.loop = loop

    def stop(self):
        """Stop the animation."""
        self.playing = False

    def reset(self):
        """Reset the animation to the first frame."""
        self.current_frame = 0
        self.elapsed_time = 0
        self.original_surface = self.frames[self.current_frame]
        self._update_surface()


class Renderer:
    """Main renderer class for managing drawing operations."""

    def __init__(self, window_surface):
        """
        Initialize the renderer.

        Args:
            window_surface (pygame.Surface): The main window surface
        """
        self.surface = window_surface
        self.width = window_surface.get_width()
        self.height = window_surface.get_height()
        self.background_color = (0, 0, 0)

    def clear(self, color=None):
        """Clear the renderer with the specified color."""
        self.surface.fill(color if color is not None else self.background_color)

    def draw_sprite(self, sprite):
        """Draw a sprite to the renderer."""
        sprite.draw(self.surface)

    def draw_rect(self, rect, color, filled=True, width=1):
        """Draw a rectangle."""
        if filled:
            pygame.draw.rect(self.surface, color, rect)
        else:
            pygame.draw.rect(self.surface, color, rect, width)

    def draw_line(self, start_pos, end_pos, color, width=1):
        """Draw a line."""
        pygame.draw.line(self.surface, color, start_pos, end_pos, width)

    def draw_text(self, text, font, color, x, y, centered=False):
        """Draw text to the renderer."""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()

        if centered:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)

        self.surface.blit(text_surface, text_rect)
        return text_rect
