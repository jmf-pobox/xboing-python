"""BlockManager: Manages block objects and their interactions in XBoing."""

import logging
from typing import Any, List


class BlockManager:
    """Manages block objects and their interactions in XBoing."""

    def __init__(self) -> None:
        """Initialize the block manager."""
        self.blocks: List[Any] = []
        self.logger = logging.getLogger("xboing.BlockManager")

    def remaining_blocks(self) -> int:
        """Return the number of blocks that are not destroyed."""
        count: int = len([b for b in self.blocks if not b.destroyed])
        return count

    def destroy_block(self, block: Any) -> None:
        """Mark a block as destroyed and log the event."""
        block.destroyed = True
        self.logger.info(f"Block destroyed: {block}")
