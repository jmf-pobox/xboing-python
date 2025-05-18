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

## Block Types and Attributes (from block_types.json)

The following table summarizes all block types, their key attributes, and special behaviors, as extracted from the canonical block_types.json:

| Block Type        | Main Sprite      | Explosion Frames         | Points | Special Behavior                  | Notes                        |
|-------------------|------------------|--------------------------|--------|-----------------------------------|------------------------------|
| RED_BLK           | redblk.xpm       | exred[1-3].xpm           | 100    | None                              | Standard block               |
| BLUE_BLK          | blueblk.xpm      | exblue[1-3].xpm          | 110    | None                              | Standard block               |
| GREEN_BLK         | grnblk.xpm       | exgren[1-3].xpm          | 120    | None                              | Standard block               |
| TAN_BLK           | tanblk.xpm       | extan[1-3].xpm           | 130    | None                              | Standard block               |
| YELLOW_BLK        | yellblk.xpm      | exyell[1-3].xpm          | 140    | None                              | Standard block               |
| PURPLE_BLK        | purpblk.xpm      | expurp[1-3].xpm          | 150    | None                              | Standard block               |
| BOMB_BLK          | bombblk.xpm      | exbomb[1-3].xpm          | 50     | Explodes neighbors                | Triggers chain explosion     |
| COUNTER_BLK       | cntblk.xpm       | excnt[1-3].xpm           | 200    | Requires multiple hits            | Animated counter             |
| BLACK_BLK         | blakblk.xpm      |                          | 0      | Indestructible wall               | Not breakable                |
| BULLET_BLK        | yellblk.xpm      | exyell[1-3].xpm          | 50     | Grants ammo                       | Yellow block, bullet overlay |
| MAXAMMO_BLK       | lotsammo.xpm     |                          | 50     | Grants unlimited ammo             | Special ammo block           |
| DEATH_BLK         | death1.xpm       | exdeath[1-4].xpm         | 0      | Kills player                      | Animated pirate block        |
| EXTRABALL_BLK     | xtrabal.xpm      |                          | 100    | Grants extra ball                 | Animated                     |
| MULTIBALL_BLK     | multibal.xpm     | exred[1-3].xpm           | 100    | Spawns multiple balls             | Uses red explosion           |
| ROAMER_BLK        | roamer.xpm       |                          | 400    | Moves around playfield            | Animated, moves              |
| BONUS_BLK         | bonus1.xpm       | exx2bs[1-3].xpm          | 0      | Grants bonus                      | Animated bonus coin          |
| BONUSX2_BLK       | x2bonus1.xpm     | exx2bs[1-3].xpm          | 0      | x2 bonus                          | Animated                     |
| BONUSX4_BLK       | x4bonus1.xpm     | exx2bs[1-3].xpm          | 0      | x4 bonus                          | Animated                     |
| TIMER_BLK         | clock.xpm        | exx2bs[1-3].xpm          | 100    | Adds time                         | Uses bonus explosion         |
| DYNAMITE_BLK      | dynamite.xpm     |                          | 0      | Explode all of one type           | Overlays other blocks        |
| PAD_SHRINK_BLK    | padshrk.xpm      |                          | 100    | Shrinks paddle                    |                              |
| PAD_EXPAND_BLK    | padexpn.xpm      |                          | 100    | Expands paddle                    |                              |
| STICKY_BLK        | stkyblk.xpm      |                          | 100    | Sticky paddle                     |                              |
| REVERSE_BLK       | reverse.xpm      |                          | 100    | Reverses paddle controls          |                              |
| HYPERSPACE_BLK    | hypspc.xpm       |                          | 100    | Special effect                    |                              |
| MGUN_BLK          | machgun.xpm      |                          | 100    | Machine gun powerup               |                              |
| WALLOFF_BLK       | walloff.xpm      |                          | 100    | Turns off wall                    |                              |
| DROP_BLK          | grnblk.xpm       | exgren[1-3].xpm          | (var)  | Drops down the playfield          | Uses green explosion         |
| RANDOM_BLK        | redblk.xpm       | exred[1-3].xpm           | 0      | Changes type randomly             | Draws '- R -' overlay        |
| BLACKHIT_BLK      | blakblkH.xpm     |                          | 0      | Indestructible wall (hit state)   | Wall block in hit state      |


## Mapping: Block Attribute/Behavior to src/ Class

| Attribute/Behavior         | Responsible Class/Module         | Status/Notes                                  |
|---------------------------|-----------------------------------|-----------------------------------------------|
| Block data/attributes      | `block_types.json` (data),        | Canonical, used for reference and tests       |
|                           | `SpriteBlock`, `SpriteBlockManager` | Main logic for block state, rendering         |
| Block rendering           | `SpriteBlock`, `SpriteBlockManager`, `renderers/` | Implemented (sprite-based)         |
| Block positioning/layout  | `SpriteBlockManager`, `GameLayout`| Implemented                                   |
| Block collision detection | `SpriteBlockManager`, `Ball`      | Implemented                                   |
| Block explosion animation | `SpriteBlock`, `renderers/`       | **Partially implemented** (not all per-type)  |
| Block special effects     | `SpriteBlock`, `GameController`   | **Partially implemented** (see TODOs)         |
| Block powerup logic       | `GameController`, `GameState`     | Implemented for most, some in progress        |
| Block state transitions   | `SpriteBlock`, `SpriteBlockManager` | Implemented                                 |
| Block asset loading       | `utils/asset_loader.py`           | Implemented                                   |
| Block test data           | `block_types.json`, `tests/`      | Implemented                                   |
| Block type registry       | `block_types.json`                | Implemented                                   |
| Block hit/score logic     | `GameController`, `GameState`     | Implemented                                   |
| Block animation (bonus, death, roamer, counter) | `SpriteBlock`, `renderers/` | **Partially implemented** (see TODOs) |
| Indestructible logic      | `SpriteBlock`, `GameController`   | Implemented                                   |
| Chain explosions          | `GameController`, `SpriteBlock`   | **Not fully implemented** (see TODOs)         |
| Block overlays (e.g., dynamite) | `SpriteBlock`, `renderers/` | **Not fully implemented**                     |

**Legend:**
- **Implemented**: Feature is present and working in the Python port.
- **Partially implemented**: Some block types/behaviors are present, but not all (see TODOs).
- **Not fully implemented**: Feature is missing or incomplete; see TODOs for future work.

## TODOs and Gaps
- Per-block-type explosion animations: Only some blocks use unique explosion frames; others use generic or missing animations.
- Chain explosions (e.g., bomb block): Logic for triggering neighbor explosions is not fully implemented.
- Block overlays (dynamite, random block text): Some overlays are not yet rendered.
- Full parity with C version: Some special block behaviors and animations are not yet ported.
- Ensure all block types in block_types.json are covered in tests and code.

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