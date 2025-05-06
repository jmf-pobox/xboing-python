# Plan: Update Asset Conversion Scripts to Use Configurable Paths

This document outlines the steps required to update all asset conversion and migration scripts in the XBoing Python project to avoid hardcoded asset paths. The goal is to make all scripts accept source and destination paths as command-line arguments, improving flexibility and maintainability, and to enable the safe removal of the unused `src/assets/` directory.

---

## 1. Identify Affected Scripts

- List all scripts in the `scripts/` directory that reference `src/assets/` or `assets/` directly (e.g., as hardcoded input/output paths).
- Typical scripts include:
  - `convert_audio.py`
  - `convert_paddle_sound.py`
  - `fix_balllost.py`
  - `simple_au_convert.py`
  - `sync_assets.py`
- Search for any other scripts with hardcoded asset paths.

## 2. Refactor Scripts to Use Command-Line Arguments

- For each affected script:
  - Replace hardcoded source and destination asset paths with command-line arguments (using `argparse`).
  - Provide sensible defaults (e.g., `assets/sounds/` for output, or prompt for input if not provided).
  - Update help messages to clearly describe the arguments.
  - Ensure scripts work when run from the project root or any subdirectory.

## 3. Update Documentation and Usage Examples

- Update script docstrings and comments to reflect the new argument-based usage.
- Add or update usage examples in the README or a dedicated section in the docs (e.g., `HATCH_USAGE.md` or a new `SCRIPT-USAGE.md`).
- Ensure all developers know to use the new argument-based invocation.

## 4. Test All Updated Scripts

- For each script, test the following scenarios:
  - Running with no arguments (should use defaults or prompt as appropriate)
  - Running with explicit source and destination paths
  - Running from different working directories
  - Handling of missing or invalid paths
- Fix any issues found during testing.

## 5. Remove `src/assets/` Directory

- Once all scripts have been updated and tested, and all asset migration is complete:
  - Delete the `src/assets/` directory and its contents.
  - Remove any references to `src/assets/` from documentation and codebase.
  - Confirm that all asset loading and conversion uses the root-level `assets/` directory.

## 6. Track Progress

- Use this document or TODO.md to check off each script as it is updated and tested.
- Optionally, add a checklist here:

```
- [ ] convert_audio.py updated
- [ ] convert_paddle_sound.py updated
- [ ] fix_balllost.py updated
- [ ] simple_au_convert.py updated
- [ ] sync_assets.py updated
- [ ] All scripts tested
- [ ] src/assets/ removed
- [ ] Documentation updated
```

---

Following this plan will ensure all asset conversion and migration scripts are robust, flexible, and maintainable, and will eliminate confusion caused by duplicate asset directories. 