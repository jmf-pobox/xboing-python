#!/usr/bin/env python3
"""Scan XBoing Python packages and output their inter-package dependencies.

Scans each module in each src package and outputs which packages depend upon which other packages.

Usage:
  python scripts/dep_grep.py
"""
import re
from pathlib import Path
from typing import Dict, Set

SRC_DIR = Path(__file__).parent.parent / "src"
PACKAGES = [
    "controllers",
    "engine",
    "game",
    "layout",
    "renderers",
    "ui",
    "utils",
]


def find_package_dependencies() -> Dict[str, Set[str]]:
    """Scan each package for imports of other packages and return a dependency map.

    Returns
    -------
        Dict[str, Set[str]]: Mapping from package to set of dependent packages.

    """
    deps: Dict[str, Set[str]] = {pkg: set() for pkg in PACKAGES}
    for pkg in PACKAGES:
        pkg_dir = SRC_DIR / pkg
        if not pkg_dir.exists():
            continue
        for py_file in pkg_dir.glob("*.py"):
            with open(py_file, encoding="utf-8") as fh:
                for line in fh:
                    m = re.match(r"from (\w+)\.", line) or re.match(
                        r"import (\w+)\.", line
                    )
                    if m:
                        dep = m.group(1)
                        if dep in PACKAGES and dep != pkg:
                            deps[pkg].add(dep)
    return deps


def print_dependencies(deps: Dict[str, Set[str]]) -> None:
    """Print the package dependency summary.

    Args:
    ----
        deps: Dependency map from find_package_dependencies().

    """
    print("Package dependencies:")
    for pkg in PACKAGES:
        dep_list = sorted(deps[pkg])
        print(f"{pkg}: {dep_list}")


def main() -> None:
    """Find and print the package dependencies."""
    deps = find_package_dependencies()
    print_dependencies(deps)


if __name__ == "__main__":
    main()
