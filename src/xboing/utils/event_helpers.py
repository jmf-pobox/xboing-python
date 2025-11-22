"""Helper functions for working with events in the game.

This module provides utility functions for working with events,
such as posting common event types with standard parameters.
"""

from xboing.engine.events import post_level_title_message

# Re-export the function for backward compatibility
__all__ = ["post_level_title_message"]
