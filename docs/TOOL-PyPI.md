# PyPI Publishing Checklist for XBoing

This checklist covers all steps for building, testing, and publishing the XBoing package to PyPI, including local development installs and TestPyPI dry runs.

---

## 1. Bump the Version
- Update the version in `src/xboing/__version__.py` (or wherever your version is set).

---

## 2. Build the Distribution
```sh
hatch build
```
- This creates `.whl` and `.tar.gz` files in the `dist/` directory.

---

## 3. Check the Distribution (Recommended)
```sh
hatch run publish:check
```
- Runs `twine check dist/*` to ensure your distributions are valid.

---

## 4. Test Install Locally (Editable/Dev Mode)
```sh
pip install -e .
```
- Installs your package in editable mode for local development.
- Uninstall with: `pip uninstall xboing`

---

## 5. Test the Build in a Clean Environment
```sh
python -m venv /tmp/xboing-test
source /tmp/xboing-test/bin/activate
pip install dist/xboing-*.whl
python -m xboing
```
- Ensures the built wheel works as expected after install.

---

## 6. Test Upload to TestPyPI (Dry Run)
```sh
hatch run publish:test-publish
```
- This will upload to [TestPyPI](https://test.pypi.org/).
- You can install from TestPyPI with:
  ```sh
  pip install --index-url https://test.pypi.org/simple/ xboing
  ```

---

## 7. Upload to PyPI
```sh
hatch run publish:upload
```
- This runs `twine upload dist/*` and will prompt for your PyPI credentials or API token.

---

## 8. Verify on PyPI
- Check your package at: https://pypi.org/project/xboing/
- Try installing in a fresh environment:
  ```sh
  pip install xboing
  python -m xboing
  ```

---

## 9. Troubleshooting
- If you get a version error, bump the version and rebuild.
- If dependencies are missing, add them to `[project] dependencies` in `pyproject.toml`.
- If assets are missing, ensure they are included in the package and referenced with package-relative paths.

---

## 10. Tag and Release
```sh
git tag vX.Y.Z
git push origin vX.Y.Z
```
- Tag your release in git for traceability.

---

**Happy publishing!** 