#!/usr/bin/env python3
"""
Developer uninstaller for ai-git-committer.

Uses pacman removal.
Does not use pip.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


CONFIG_DIR = Path.home() / ".config" / "ai-git-committer"


def run(command: list[str]) -> int:
    print(f"\n$ {' '.join(command)}")

    return subprocess.run(
        command,
        check=False,
    ).returncode


def uninstall_package() -> bool:
    if subprocess.run(
        ["pacman", "-Q", "ai-git-committer"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode != 0:
        print("[INFO] ai-git-committer is not installed")
        return True

    return (
        run(
            [
                "sudo",
                "pacman",
                "-Rns",
                "--noconfirm",
                "ai-git-committer",
            ]
        )
        == 0
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove ai-git-committer"
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
 ai-git-committer Uninstaller
====================================
"""
    )

    if not args.yes:
        answer = input(
            "Remove ai-git-committer? [y/N]: "
        ).lower()

        if answer not in ("y", "yes"):
            print("Cancelled.")
            return 1

    if not uninstall_package():
        print(
            "[ERROR] pacman removal failed"
        )
        return 1

    print(
        """
====================================
 Uninstallation complete
====================================
"""
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
