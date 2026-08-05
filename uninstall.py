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
    return (
        run(
            [
                "sudo",
                "pacman",
                "-R",
                "--noconfirm",
                "ai-git-committer",
            ]
        )
        == 0
    )


def purge_config() -> None:
    if CONFIG_DIR.exists():
        shutil.rmtree(CONFIG_DIR)

        print(
            f"[OK] Removed configuration: {CONFIG_DIR}"
        )
    else:
        print(
            "[INFO] Configuration directory does not exist"
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove ai-git-committer"
    )

    parser.add_argument(
        "--purge",
        action="store_true",
        help="Remove ~/.config/ai-git-committer",
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

    if args.purge:
        purge_config()

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