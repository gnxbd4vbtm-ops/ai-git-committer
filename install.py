#!/usr/bin/env python3
"""
Developer installer for ai-git-committer.

Builds the Arch Linux package and installs it through pacman.
No pip usage. No PATH modification.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent


def run(
    command: list[str],
    *,
    cwd: Path | None = None,
) -> int:
    print(f"\n$ {' '.join(command)}")

    result = subprocess.run(
        command,
        cwd=cwd,
        check=False,
    )

    return result.returncode


def require_command(name: str) -> bool:
    if shutil.which(name):
        return True

    print(f"[ERROR] Missing required command: {name}")
    return False


def check_arch() -> bool:
    arch_files = [
        Path("/etc/arch-release"),
        Path("/etc/cachyos-release"),
    ]

    if any(path.exists() for path in arch_files):
        print("[OK] Arch-based system detected")
        return True

    print(
        "[WARNING] This does not look like Arch Linux.\n"
        "Continue only if you know what you are doing."
    )

    return True


def check_dependencies() -> bool:
    required = [
        "makepkg",
        "pacman",
        "python",
    ]

    return all(require_command(cmd) for cmd in required)


def build_package() -> Path | None:
    print("\n== Building Arch package ==")

    result = run(
        [
            "makepkg",
            "-f",
            "--clean",
        ],
        cwd=PROJECT_ROOT,
    )

    if result != 0:
        print("[ERROR] Package build failed")
        return None

    packages = sorted(
        PROJECT_ROOT.glob("*.pkg.tar.zst"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not packages:
        print("[ERROR] No package found")
        return None

    return packages[0]


def install_package(package: Path) -> bool:
    print("\n== Installing package ==")

    result = run(
        [
            "sudo",
            "pacman",
            "-U",
            "--needed",
            str(package),
        ]
    )

    return result == 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build and install ai-git-committer Arch package"
    )

    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip confirmation",
    )

    args = parser.parse_args()

    print(
        """
====================================
 ai-git-committer Arch Installer
====================================
"""
    )

    if not args.yes:
        answer = input(
            "Build and install ai-git-committer? [y/N]: "
        ).lower()

        if answer not in ("y", "yes"):
            print("Cancelled.")
            return 1

    check_arch()

    if not check_dependencies():
        return 1

    package = build_package()

    if package is None:
        return 1

    if not install_package(package):
        return 1

    print(
        """
====================================
 Installation complete!

 Run:
   aic

 or:

   ai-git-committer

====================================
"""
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())