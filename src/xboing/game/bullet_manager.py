"""Manages bullet objects and their state in XBoing."""

import logging
from typing import Iterator, List

from .bullet import Bullet

logger = logging.getLogger("xboing.BulletManager")


class BulletManager:
    """Manages the canonical list of Bullet objects in play."""

    def __init__(self) -> None:
        """Initialize the BulletManager with an empty list of bullets."""
        self._bullets: List[Bullet] = []

    @property
    def bullets(self) -> List[Bullet]:
        """Return the list of bullets (read/write for legacy compatibility)."""
        return self._bullets

    def __iter__(self) -> Iterator[Bullet]:
        """Return an iterator over the managed bullets."""
        return iter(self._bullets)

    def add_bullet(self, bullet: Bullet) -> None:
        """Add a bullet to the manager."""
        self._bullets.append(bullet)
        logger.info(f"Added bullet: {bullet}")

    def remove_bullet(self, bullet: Bullet) -> None:
        """Remove a bullet from the manager."""
        self._bullets.remove(bullet)

    def clear(self) -> None:
        """Remove all bullets from the manager."""
        self._bullets.clear()

    def update(self, delta_ms: float) -> None:
        """Update all bullets and remove inactive ones.

        Args:
            delta_ms: Time since last frame in milliseconds.

        """
        logger.debug(f"Updating bullets: {len(self._bullets)} bullets in play")
        for bullet in self._bullets[:]:
            bullet.update(delta_ms)
            if not bullet.is_active():
                self._bullets.remove(bullet)

    def __len__(self) -> int:
        """Return the number of bullets currently managed."""
        return len(self._bullets)
