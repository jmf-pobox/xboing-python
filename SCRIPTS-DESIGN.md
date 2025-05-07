# SCRIPTS-DESIGN.md

## Overview

This document describes the current state, design, and migration status of all asset migration and conversion scripts in the `scripts/` directory for the XBoing Python project. It also assesses the completeness of asset migration from the legacy `xboing2.4-clang` project to the new `assets/` directory structure, and outlines the changes needed to ensure 100% migration and cross-platform compatibility.

---

## 1. Script Inventory & Purpose

| Script Name              | Purpose                                                                 | Notes / Issues |
|-------------------------|-------------------------------------------------------------------------|---------------|
| sync_assets.py           | Synchronizes and copies assets from legacy to new structure; invokes XPM to PNG conversion | Needs update for new asset subdirs; only covers some asset types |
| better_xpm_converter.py  | Converts XPM images to PNG with improved color handling                  | CLI, cross-platform, but may need path updates |
| xpm_to_png.py            | Converts XPM images to PNG (older, less robust than better_xpm_converter.py) | Redundant with better_xpm_converter.py |
| fix_background.py        | Special-case converter for background XPM to PNG                         | Only for bgrnd.xpm; may be obsolete |
| fix_balllost.py          | Fixes and converts corrupted balllost.au to WAV                          | Hardcoded paths; needs path update |
| convert_audio.py         | Batch converts .au to .wav using ffmpeg/pydub                            | Requires ffmpeg; cross-platform but needs path update |
| simple_au_convert.py     | Batch converts .au to .wav (pure Python, no external deps)               | Only covers essential sounds; needs extension |
| convert_paddle_sound.py  | Converts paddle.au to WAV (special case)                                 | Hardcoded paths; needs path update |

---

## 2. Asset Migration Status

### 2.1 Bitmaps/Images

#### Migrated (assets/images/*):
- backgrounds: bgrnd.png, bgrnd2.png, bgrnd3.png, bgrnd4.png, bgrnd5.png, mnbgrnd.png, space.png
- blocks: (many, see directory listing)
- balls: ball1.png, ball2.png, ball3.png, ball4.png, bbirth1-8.png, killer.png, life.png
- paddle: padhuge.png, padmed.png, padsml.png
- digits: digit0-9.png

#### Not Yet Migrated (xboing2.4-clang/bitmaps/*):
- eyes: deveyes*.xpm, guy*.xpm
- guides: guide*.xpm
- guns: bullet.xpm, tink.xpm
- presents: earth.xpm, flag.xpm, justin.xpm, kibell.xpm, presents.xpm, title*.xpm
- stars: star*.xpm
- blockex: excnt*, exdeath*, exgren*, expurp*, exred*, extan*, exx2bs*, exyell*, exblue*, exbomb*
- Misc: floppy.xpm, highscr.xpm, icon.xpm, larrow.xpm, mouse.xpm, question.xpm, rarrow.xpm, text.xpm

### 2.2 Sounds

#### Migrated (assets/sounds/):
- applause.wav, balllost.wav, ballshot.wav, boing.wav, bomb.wav, bonus.wav, click.wav, game_over.wav, paddle.wav, powerup.wav, whoosh.wav

#### Not Yet Migrated (xboing2.4-clang/sounds/):
- Many .au files not present as .wav (e.g., Doh1-4.au, ammo.au, ball2ball.au, buzzer.au, ddloo.au, evillaugh.au, gate.au, hithere.au, hypspc.au, intro.au, key.au, looksbad.au, metal.au, mgun.au, ouch.au, ping.au, shark.au, shoot.au, shotgun.au, spring.au, stamp.au, sticky.au, supbons.au, toggle.au, tone.au, touch.au, wallsoff.au, warp.au, weeek.au, whizzo.au, wzzz.au, wzzz2.au, youagod.au)

### 2.3 Levels

#### Migrated (assets/levels/):
- All levelXX.data, demo.data, editor.data, new.data (appears complete)

#### Not Yet Migrated:
- None detected (all files present)

---

## 3. Cross-Platform & Path Issues

- Many scripts use hardcoded or relative paths that assume a Linux directory structure. Update all scripts to use `os.path` or `pathlib` for cross-platform compatibility.
- Some scripts assume the legacy asset directory is at a fixed relative path; this may break if the project is moved. Use configuration or environment variables if needed.
- Some scripts require external tools (e.g., ffmpeg for audio conversion). Document these requirements and check for tool presence at runtime.
- Some scripts (e.g., fix_balllost.py, convert_paddle_sound.py) are hardcoded for specific files and may not generalize to all assets.

---

## 4. Recommendations & Next Steps

1. **Update all scripts to use cross-platform path handling (os.path, pathlib).**
2. **Extend sync_assets.py and/or add new scripts to cover all asset subdirectories:**
   - Add support for eyes, guides, guns, presents, stars, blockex, and any other missing asset types.
   - Ensure all XPM files are converted to PNG and placed in the correct assets/images subdirectory.
   - Ensure all .au files are converted to .wav and placed in assets/sounds/.
3. **Add a verification step to check for missing assets after migration.**
4. **Document all scripts in this file and keep it up to date as scripts are modified.**
5. **Add/extend tests for asset migration scripts to ensure no regressions.**
6. **Remove or merge redundant scripts (e.g., xpm_to_png.py vs better_xpm_converter.py).**
7. **Document external dependencies (e.g., ffmpeg, Pillow) in README or here.**

---

## 5. Migration Checklist (Summary Table)

| Asset Type | Subdirectory | Migrated | Missing | Notes |
|------------|--------------|----------|---------|-------|
| Images     | backgrounds  | All      | None    | Complete |
| Images     | blocks       | All      | None    | Complete |
| Images     | balls        | All      | None    | Complete |
| Images     | paddle       | All      | None    | Complete |
| Images     | digits       | All      | None    | Complete |
| Images     | eyes         | No       | All     | Needs migration |
| Images     | guides       | No       | All     | Needs migration |
| Images     | guns         | No       | All     | Needs migration |
| Images     | presents     | No       | All     | Needs migration |
| Images     | stars        | No       | All     | Needs migration |
| Images     | blockex      | Partial? | Most    | Needs migration |
| Sounds     | .wav         | Partial  | Many    | Needs migration |
| Levels     | .data        | All      | None    | Complete |

---

## 6. External Dependencies
- **Pillow**: Required for image conversion scripts.
- **ffmpeg**: Required for audio conversion (convert_audio.py).
- **pydub**: Optional, used in convert_audio.py for audio handling.

---

## 7. References
- See `docs/PROJECT-PATHS.md` for directory structure and asset path conventions.
- See `TODO.md` for current migration and script update tasks.

---

## 8. Action Items
- [ ] Update all scripts for cross-platform compatibility and current asset paths.
- [ ] Migrate all missing images (eyes, guides, guns, presents, stars, blockex, etc.).
- [ ] Migrate all missing sounds (.au to .wav).
- [ ] Remove/merge redundant scripts.
- [ ] Add/extend tests for migration scripts.
- [ ] Document all changes in this file and in TODO.md.

---

## 9. Special-Case Scripts

Some legacy assets require special handling that is not covered by the general-purpose migration/conversion scripts. The following scripts are maintained separately for these cases:

### fix_balllost.py
- **Purpose:** Converts the `balllost.au` sound file (with a corrupted/non-standard header) to `balllost.wav`.
- **Why special?** Uses a fixed header offset and custom μ-law to PCM conversion. Standard audio conversion scripts may not work for this file.
- **Scope:** Only for `balllost.au` → `balllost.wav`.
- **Path handling:** Should be updated to resolve input/output paths from the current working directory (not script location), matching the style of other scripts.

### fix_background.py
- **Purpose:** Converts the `bgrnd.xpm` background pattern to `bgrnd.png` using a hardcoded color mapping.
- **Why special?** Tailored to the unique format and palette of `bgrnd.xpm`, which may not be handled by general XPM-to-PNG converters.
- **Scope:** Only for `bgrnd.xpm` → `bgrnd.png`.
- **Path handling:** Should be updated to resolve input/output paths from the current working directory (not script location), matching the style of other scripts.

**Recommendation:**
- Keep these scripts separate for clarity and safety.
- Document their usage and limitations in this file.

---

## Deprecated/Removed Scripts

The following scripts have been removed as their functionality is now fully covered by the updated and modernized scripts:

- `xpm_to_png.py`: Superseded by `better_xpm_converter.py`.
- `simple_au_convert.py`: Superseded by `convert_audio.py` and `fix_balllost.py`.
- `sync_assets.py`: Asset migration and synchronization is now handled by the updated conversion scripts and manual review.
- `convert_paddle_sound.py`: Superseded by `convert_audio.py` (no special handling required for paddle.au).

Refer to the sections above for the recommended scripts to use for each asset type. 