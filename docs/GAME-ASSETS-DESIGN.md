# SCRIPTS-DESIGN.md

## Overview

This document describes the final state and design of all asset migration and conversion scripts in the `scripts/` directory for the XBoing Python project. The migration from the legacy `xboing2.4-clang` project to the new `assets/` directory structure is now complete, with all redundant scripts removed and only essential, modernized scripts retained.

---

## 1. Script Inventory & Purpose (Current)

| Script Name             | Purpose                                                         | Notes |
|------------------------|------------------------------------------------------------------|-------|
| convert_xpm_to_png.py  | Converts all XPM images to PNG for all asset subdirectories      | CLI, cross-platform, covers all images |
| convert_au_to_wav.py   | Batch converts all .au audio files to .wav using ffmpeg          | CLI, cross-platform, covers all standard audio |
| fix_balllost.py        | Special-case: Converts corrupted balllost.au to balllost.wav     | Only for balllost.au; custom μ-law decode |
| fix_background.py      | Special-case: Converts bgrnd.xpm to bgrnd.png with custom logic  | Only for bgrnd.xpm; custom palette |

All other scripts have been removed as redundant or obsolete.

---

## 2. Cross-Platform & Path Handling

- All scripts use `pathlib` for robust, cross-platform path handling.
- Input and output paths are resolved from the current working directory.
- External dependencies (Pillow, ffmpeg) are checked at runtime and documented.

---

## 3. Recommended Workflow

1. **Convert all images:**
   - `python scripts/convert_xpm_to_png.py` (with optional --input/--output)
2. **Convert all standard audio:**
   - `python scripts/convert_au_to_wav.py` (with optional --input/--output)
3. **Special-case conversions:**
   - `python scripts/fix_balllost.py` (for balllost.au)
   - `python scripts/fix_background.py` (for bgrnd.xpm)

---

## 4. External Dependencies
- **Pillow**: Required for image conversion scripts.
- **ffmpeg**: Required for audio conversion (convert_au_to_wav.py).

---

## 5. References
- See `docs/PROJECT-PATHS.md` for directory structure and asset path conventions.
- See `TODO.md` for any remaining migration or script update tasks.

---

## 6. Special-Case Scripts

Some legacy assets require special handling that is not covered by the general-purpose migration/conversion scripts. The following scripts are maintained separately for these cases:

### fix_balllost.py
- **Purpose:** Converts the `balllost.au` sound file (with a corrupted/non-standard header) to `balllost.wav`.
- **Why special?** Uses a fixed header offset and custom μ-law to PCM conversion. Standard audio conversion scripts may not work for this file.
- **Scope:** Only for `balllost.au` → `balllost.wav`.

### fix_background.py
- **Purpose:** Converts the `bgrnd.xpm` background pattern to `bgrnd.png` using a hardcoded color mapping.
- **Why special?** Tailored to the unique format and palette of `bgrnd.xpm`, which may not be handled by general XPM-to-PNG converters.
- **Scope:** Only for `bgrnd.xpm` → `bgrnd.png`.

---

## 7. Deprecated/Removed Scripts

The following scripts have been removed as their functionality is now fully covered by the updated and modernized scripts:
- `xpm_to_png.py`, `simple_au_convert.py`, `sync_assets.py`, `convert_paddle_sound.py`, `better_xpm_converter.py`, `convert_audio.py` (see previous versions for details).

---

## 8. Action Items (Complete)
- [x] Update all scripts for cross-platform compatibility and current asset paths.
- [x] Migrate all missing images and sounds.
- [x] Remove/merge redundant scripts.
- [x] Document all changes in this file and in TODO.md.

**The asset migration and script modernization process is now complete.**

## Script Location

All utility scripts are now located in `src/xboing/scripts/`. These scripts are used for asset conversion, dependency analysis, and other development tasks. Run them as modules, e.g., `python -m xboing.scripts.convert_au_to_wav`.

## 9. External Dependencies
- **Pillow**: Required for image conversion scripts.
- **ffmpeg**: Required for audio conversion (convert_au_to_wav.py).

## 10. References
- See `docs/PROJECT-PATHS.md` for directory structure and asset path conventions.
- See `TODO.md` for any remaining migration or script update tasks.

## 11. Special-Case Scripts

Some legacy assets require special handling that is not covered by the general-purpose migration/conversion scripts. The following scripts are maintained separately for these cases:

### fix_balllost.py
- **Purpose:** Converts the `balllost.au` sound file (with a corrupted/non-standard header) to `balllost.wav`.
- **Why special?** Uses a fixed header offset and custom μ-law to PCM conversion. Standard audio conversion scripts may not work for this file.
- **Scope:** Only for `balllost.au` → `balllost.wav`.

### fix_background.py
- **Purpose:** Converts the `bgrnd.xpm` background pattern to `bgrnd.png` using a hardcoded color mapping.
- **Why special?** Tailored to the unique format and palette of `bgrnd.xpm`, which may not be handled by general XPM-to-PNG converters.
- **Scope:** Only for `bgrnd.xpm` → `bgrnd.png`.

## 12. Deprecated/Removed Scripts

The following scripts have been removed as their functionality is now fully covered by the updated and modernized scripts:
- `xpm_to_png.py`, `simple_au_convert.py`, `sync_assets.py`, `convert_paddle_sound.py`, `better_xpm_converter.py`, `convert_audio.py` (see previous versions for details).

## 13. Action Items (Complete)
- [x] Update all scripts for cross-platform compatibility and current asset paths.
- [x] Migrate all missing images and sounds.
- [x] Remove/merge redundant scripts.
- [x] Document all changes in this file and in TODO.md.

**The asset migration and script modernization process is now complete.** 