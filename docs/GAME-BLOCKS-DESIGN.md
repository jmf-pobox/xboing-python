# XBoing Block System — Current Design

## Block Data and Configuration

- All block types, attributes, point values, and image mappings are defined in `src/xboing/assets/config/block_types.json`.
- The canonical string constants for block types are defined in `src/game/block_types.py` and are used throughout the codebase to prevent typos and ensure consistency.
- The mapping from level file characters to block types in `LevelManager` now uses these canonical constants.

## Block Implementation

- Block logic is handled by the `Block` class and its subclasses (e.g., `CounterBlock` for counter blocks).
- Block management (creation, removal, state updates) is handled by `BlockManager`.
- Block rendering is stateless and handled by `BlockRenderer`, which preloads all block images and animation frames.
- All block configuration (including special effects, point values, and image/animation data) is loaded from the JSON at startup.

## Rendering and Animation

- Blocks are rendered using preloaded PNG sprites, converted from the original XPMs, located in `src/xboing/assets/images/blocks/`.
- Animated blocks (e.g., counter, death, bonus) use multiple frames as specified in the JSON.
- Explosion/breaking animations are handled by the `Block` class, using per-type frames as specified in the JSON.
- Special overlays (e.g., for dynamite, random block text) are partially implemented.

## Block Types and Effects

- All block types from the original game are present, including standard, special, powerup, and animated blocks.
- Special effects (e.g., ammo, multiball, paddle shrink/expand, sticky, etc.) are triggered using canonical string constants, not hardcoded strings or ints.
- Unbreakable and special blocks are handled according to their type and configuration.
- Point values and behaviors are fully data-driven and match the canonical JSON.

## Testing and Compliance

- All tests use the canonical string constants and are updated to match the data-driven system.
- The codebase is fully PEP 8/257/484 compliant, type-checked, and formatted.
- Legacy integer constants, static mappings, and dead code have been removed.

## Outstanding Gaps (as of now)

- Chain explosions (e.g., bomb block): Logic for triggering neighbor explosions is not fully implemented.
- Block overlays (dynamite, random block text): Some overlays are not yet rendered.
- Full parity with C version: Some special block behaviors and animations are not yet ported.
- Ensure all block types in `block_types.json` are covered in tests and code.

## Counter Block Logic (Canonical Behavior)

- Counter blocks are created for any digit ('0'-'9') in the level data.
- The digit value N means the block requires N+1 hits to break:
    - '0' → 1 hit (shows blank, i.e., cntblk.png)
    - '1' → 2 hits (shows '1', then blank)
    - '2' → 3 hits (shows '2', then '1', then blank)
    - etc.
- Rendering:
    - If hits_remaining > 1: show the corresponding numbered image (cntblkN.png, where N = hits_remaining-1)
    - If hits_remaining == 1: show cntblk.png (no number)
    - When hits_remaining == 0: block is destroyed
- This matches the original C logic and ensures full parity with the intended gameplay.
- The mapping from level data to block creation and rendering is now systematic and data-driven.

---

The XBoing Python block system is now fully data-driven, using canonical constants and JSON configuration for all block types and behaviors. Rendering, animation, and special effects are handled by dedicated, stateless classes. The codebase is clean, modern, and maintainable, with only a few advanced features (like chain explosions and overlays) remaining for full parity with the original.