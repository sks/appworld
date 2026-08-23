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


APP_DESCRIPTIONS: dict[str, str] = {
    "admin": "Administrative APIs for AppWorld.",
    "api_docs": "OpenAPI documentation for AppWorld apps.",
    "supervisor": "Supervisor persona and task context.",
    "amazon": "Amazon shopping app.",
    "phone": "Phone SMS and contacts app.",
    "file_system": "File system app.",
    "spotify": "Spotify music app.",
    "venmo": "Venmo payments app.",
    "gmail": "Gmail email app.",
    "splitwise": "Splitwise expense sharing app.",
    "simple_note": "Simple Note notes app.",
    "todoist": "Todoist tasks app.",
}


def ensure_info_toml_files(apps_dir: Path) -> int:
    created = 0
    for app_dir in apps_dir.iterdir():
        if not app_dir.is_dir() or app_dir.name.startswith("_"):
            continue
        info_path = app_dir / "info.toml"
        if info_path.exists():
            continue
        app_name = app_dir.name
        description = APP_DESCRIPTIONS.get(app_name, f"The {app_name} app.")
        info_path.write_text(f'name = "{app_name}"\ndescription = "{description}"\n')
        created += 1
    return created


def main() -> int:
    apps_dir = Path(os.path.dirname(appworld.__file__)) / "apps"
    info_created = ensure_info_toml_files(apps_dir)
    changed = sum(1 for path in apps_dir.rglob("*.py") if patch_file(path))
    print(f"Created {info_created} info.toml files under {apps_dir}")
    print(f"Patched {changed} app files under {apps_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
