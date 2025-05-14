import logging


class BlockManager:
    def __init__(self):
        self.blocks = []
        self.logger = logging.getLogger("xboing.BlockManager")

    def remaining_blocks(self):
        count = len([b for b in self.blocks if not b.destroyed])
        return count

    def destroy_block(self, block):
        block.destroyed = True
        self.logger.info(f"Block destroyed: {block}")
