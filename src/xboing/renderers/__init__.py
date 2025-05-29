"""Renderers package for XBoing, containing rendering logic for UI and game elements.

This module provides a collection of stateless renderers for various game elements:

- AmmoRenderer: Displays the current ammo (bullets) as bullet images
- BlockRenderer: Displays blocks using block sprites and animation frames
- BulletRenderer: Displays all bullets on screen
- BulletRowRenderer: Displays a row of bullets (animated)
- CompositeRenderer: Orchestrates a sequence of row renderers, handling reveal/animation state
- DigitRenderer: Displays LED-style numbers using digit sprites
- LivesRenderer: Displays the number of lives as ball images
- LogoRenderer: Displays a logo image centered at a given y-coordinate
- RowRenderer: Protocol defining the interface for all row renderers
- TextRowRenderer: Displays a single row of text, optionally with an icon

Renderers are designed to be stateless, meaning they don't maintain game state
but rather render the current state provided to them. This separation of concerns
allows for easier testing and maintenance.
"""
