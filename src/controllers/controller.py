from typing import List

import pygame
from typing_extensions import Protocol


class Controller(Protocol):
    """Protocol for controllers used in the main loop."""

    def handle_events(self, events: List[pygame.event.Event]) -> None: ...

    def update(self, delta_time: float) -> None: ...
