"""
Digit Display utilities for rendering LED-style numbers.

This module provides a DigitDisplay class that renders numbers using the classic
LED-style digit sprites from the original XBoing game.
"""

import os
import pygame
from src.utils.asset_paths import get_asset_path


def get_digits_dir():
    """Get the path to the digit images directory."""
    return get_asset_path("images/digits", create_dirs=True)


class DigitDisplay:
    """
    A class for rendering LED-style numbers using digit sprites.
    
    This maintains the classic XBoing aesthetic with the original LED-style
    digit images for rendering scores, levels, etc.
    """

    def __init__(self):
        """Initialize the DigitDisplay with loaded digit sprites."""
        self.digits = {}
        self._load_digits()
        
        # Cache for previously rendered numbers
        self._surface_cache = {}
        
        # Digit dimensions (all digits have the same size)
        if self.digits:
            self.digit_width = self.digits[0].get_width()
            self.digit_height = self.digits[0].get_height()
        else:
            # Default values in case loading fails
            self.digit_width = 30
            self.digit_height = 40

    def _load_digits(self):
        """Load all digit sprites from the assets directory."""
        digits_dir = get_digits_dir()
        for i in range(10):
            digit_path = os.path.join(digits_dir, f"digit{i}.png")
            if os.path.exists(digit_path):
                self.digits[i] = pygame.image.load(digit_path).convert_alpha()
            else:
                print(f"Warning: Could not load digit image: {digit_path}")

    def render_number(self, number, spacing=2, scale=1.0, color=None, width=None, right_justified=False):
        """
        Render a number using the LED-style digit sprites.
        
        Args:
            number (int): The number to render
            spacing (int): Pixels between digits
            scale (float): Scale factor for the rendered digits
            color (tuple): Optional (R, G, B) color to tint the digits. If None, original color is used.
            width (int): If specified, forces a fixed width (in digits) for right-justified numbers
            right_justified (bool): If True, right-justifies the number in its display area
            
        Returns:
            pygame.Surface: A surface containing the rendered number
        """
        # Convert number to string
        number_str = str(number)
        
        # If width is specified, pad the number string with spaces on the left
        if width is not None and len(number_str) < width:
            number_str = ' ' * (width - len(number_str)) + number_str
        
        # Check cache first - include all parameters in cache key
        cache_key = (number_str, spacing, scale, color, width, right_justified)
        if cache_key in self._surface_cache:
            return self._surface_cache[cache_key]
        
        # Calculate the width of the rendered number
        scaled_width = int(self.digit_width * scale)
        total_width = (scaled_width * len(number_str)) + (spacing * (len(number_str) - 1))
        scaled_height = int(self.digit_height * scale)
        
        # Create a surface for the rendered number
        surface = pygame.Surface((total_width, scaled_height), pygame.SRCALPHA)
        
        # Adjust starting position for right-justified numbers
        if right_justified and width is not None and len(number_str) < width:
            # Calculate additional width needed for right justification
            extra_width = (width - len(number_str)) * (scaled_width + spacing)
            x = extra_width
        else:
            x = 0
        
        # Render each digit
        for digit_char in number_str:
            if digit_char == ' ':
                # Skip spaces in the number string
                x += scaled_width + spacing
                continue
                
            try:
                digit = int(digit_char)
                if digit in self.digits:
                    # Get the base digit surface
                    digit_surface = self.digits[digit]
                    
                    # Scale if needed
                    if scale != 1.0:
                        digit_surface = pygame.transform.smoothscale(
                            digit_surface, 
                            (scaled_width, scaled_height)
                        )
                    
                    # Apply color tint if specified
                    if color:
                        # Create a copy of the digit surface
                        colored_surface = digit_surface.copy()
                        
                        # Fill with the specified color, preserving alpha
                        colored_surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
                        
                        # Use the colored surface
                        digit_surface = colored_surface
                    
                    # Blit the digit onto the surface
                    surface.blit(digit_surface, (x, 0))
                    
                    # Move to the next digit position
                    x += scaled_width + spacing
            except ValueError:
                # Skip non-digit characters
                x += scaled_width + spacing
        
        # Cache the rendered surface
        self._surface_cache[cache_key] = surface
        
        return surface
        
    def render_time(self, seconds, spacing=2, scale=1.0, colon_width=8, color=None):
        """
        Render a time value in MM:SS format using the LED-style digit sprites.
        
        Args:
            seconds (int): The time in seconds to render
            spacing (int): Pixels between digits
            scale (float): Scale factor for the rendered digits
            colon_width (int): Width of the colon separator in pixels
            color (tuple): Optional (R, G, B) color to tint the digits. If None, original color is used.
            
        Returns:
            pygame.Surface: A surface containing the rendered time
        """
        # Format time as MM:SS
        minutes = seconds // 60
        secs = seconds % 60
        time_str = f"{minutes:02d}:{secs:02d}"
        
        # Check cache first - include color in cache key
        cache_key = (f"time_{time_str}", spacing, scale, colon_width, color)
        if cache_key in self._surface_cache:
            return self._surface_cache[cache_key]
        
        # Calculate dimensions
        scaled_width = int(self.digit_width * scale)
        scaled_height = int(self.digit_height * scale)
        
        # Calculate total width including colon
        total_width = (scaled_width * 4) + (spacing * 3) + colon_width
        
        # Create a surface
        surface = pygame.Surface((total_width, scaled_height), pygame.SRCALPHA)
        
        # Determine colon color - use the provided color or default to yellow
        colon_color = color if color else (255, 255, 0)  # Default to yellow
        
        # Render minutes (2 digits)
        x = 0
        for digit_char in f"{minutes:02d}":
            digit = int(digit_char)
            if digit in self.digits:
                # Get base digit surface
                digit_surface = self.digits[digit]
                
                # Scale if needed
                if scale != 1.0:
                    digit_surface = pygame.transform.smoothscale(
                        digit_surface,
                        (scaled_width, scaled_height)
                    )
                
                # Apply color tint if specified
                if color:
                    # Create a copy of the digit surface
                    colored_surface = digit_surface.copy()
                    
                    # Fill with the specified color, preserving alpha
                    colored_surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
                    
                    # Use the colored surface
                    digit_surface = colored_surface
                
                # Blit the digit onto the surface
                surface.blit(digit_surface, (x, 0))
                x += scaled_width + spacing
        
        # Add colon - draw two small dots using the specified color
        colon_y1 = scaled_height // 3
        colon_y2 = (scaled_height * 2) // 3
        colon_x = x
        pygame.draw.circle(surface, colon_color, (colon_x + colon_width//2, colon_y1), 3)
        pygame.draw.circle(surface, colon_color, (colon_x + colon_width//2, colon_y2), 3)
        x += colon_width + spacing
        
        # Render seconds (2 digits)
        for digit_char in f"{secs:02d}":
            digit = int(digit_char)
            if digit in self.digits:
                # Get base digit surface
                digit_surface = self.digits[digit]
                
                # Scale if needed
                if scale != 1.0:
                    digit_surface = pygame.transform.smoothscale(
                        digit_surface,
                        (scaled_width, scaled_height)
                    )
                
                # Apply color tint if specified
                if color:
                    # Create a copy of the digit surface
                    colored_surface = digit_surface.copy()
                    
                    # Fill with the specified color, preserving alpha
                    colored_surface.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
                    
                    # Use the colored surface
                    digit_surface = colored_surface
                
                # Blit the digit onto the surface
                surface.blit(digit_surface, (x, 0))
                x += scaled_width + spacing
        
        # Cache the rendered surface
        self._surface_cache[cache_key] = surface
        
        return surface