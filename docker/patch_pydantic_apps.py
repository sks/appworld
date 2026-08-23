#!/usr/bin/env python3
"""Patch unpacked AppWorld apps for pydantic v2 serve/mcp startup."""
from __future__ import annotations

import os
import re
from pathlib import Path

import appworld


def patch_file(path: Path) -> bool:
    text = path.read_text()
    original = text
    text = re.sub(
        r"@root_validator(\s*\n)",
        r"@root_validator(skip_on_failure=True)\1",
        text,
    )
    text = re.sub(
        r"@root_validator\((?!skip_on_failure)",
        r"@root_validator(skip_on_failure=True, ",
        text,
    )
    text = text.replace("constr(regex=", "constr(pattern=")
    if text != original:
        path.write_text(text)
        return True
    return False


def main() -> int:
    apps_dir = Path(os.path.dirname(appworld.__file__)) / "apps"
    changed = sum(1 for path in apps_dir.rglob("*.py") if patch_file(path))
    print(f"Patched {changed} app files under {apps_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
