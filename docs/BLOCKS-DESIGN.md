# XBoing Block Implementation

This document describes the implementation of blocks in the Python port of XBoing, based on the original X11 version.

## Original XBoing Block Specifications

In the original XBoing game:

- Blocks are defined with dimensions of 40x20 pixels (BLOCK_WIDTH=40, BLOCK_HEIGHT=20)
- Spacing between blocks is 7 pixels (SPACE=7)
- Blocks have rounded edges and 3D-style appearance with different colors
- Multiple special block types with animations and effects

## Implementation Details

### Block Dimensions and Spacing

The blocks in this implementation follow the original specifications:
- Width: 40 pixels
- Height: 20 pixels
- Spacing between blocks: 7 pixels

### Sprite-Based Rendering

Rather than drawing shapes with pygame's drawing primitives, this implementation uses the actual sprites from the original XBoing game:

1. Original XPM files are converted to PNG format using the provided `xpm_to_png.py` tool
2. The sprites are loaded and cached to improve performance
3. Animated blocks have multiple frames that cycle during gameplay

### Block Positioning

Blocks are positioned following the original XBoing's algorithm:
- Horizontal spacing: Each block is positioned with a 7-pixel margin between blocks
- Vertical spacing: Blocks have 7 pixels between rows
- The entire grid is offset to be centered in the play area

### Block Types

The implementation includes all block types from the original game:
- Regular colored blocks (red, blue, green, yellow, purple, tan)
- Special blocks (bomb, extraball, multiball, etc.)
- Animated blocks (counter blocks, death blocks)
- Powerup blocks (sticky, paddle expand/shrink, etc.)

## Collision Detection

Collision detection with blocks:
1. Uses rectangle-based collision detection with additional precision for angles
2. Calculates proper bounce angles based on where the ball hits the block
3. Triggers block animations and breakage when appropriate

## Usage

The sprite-based blocks are implemented in the `SpriteBlock` and `SpriteBlockManager` classes, which replace the simpler drawn blocks that were previously used. 

To create a new level with blocks:

```python
# Create a block manager with proper positioning
block_manager = SpriteBlockManager(play_area_x, play_area_y)

# Create a level with the specified parameters
block_manager.create_level(level_number, play_area_width, top_margin)
```

Each block is positioned precisely within the grid, and the spacing between blocks matches the original XBoing game for authentic reproduction.