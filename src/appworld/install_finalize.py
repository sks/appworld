"""Post-install fixes for unpacked AppWorld app packages.

Older encrypted app bundles ship pydantic v1-style validators and may omit
per-app info.toml metadata. finalize_installed_apps applies compatibility
updates after bundle unpack so serve apis/mcp can start on pydantic v2.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

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


def _patch_pydantic_compat(path: Path) -> bool:
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
    if text == original:
        return False
    path.write_text(text)
    return True


def _ensure_info_toml_files(apps_dir: Path) -> int:
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


def finalize_installed_apps(apps_directory: str) -> None:
    """Apply pydantic v2 and metadata fixes to unpacked apps under apps_directory."""
    apps_dir = Path(apps_directory) / "apps"
    if not apps_dir.is_dir():
        return
    info_created = _ensure_info_toml_files(apps_dir)
    patched = sum(1 for path in apps_dir.rglob("*.py") if _patch_pydantic_compat(path))
    print(
        f"Finalized installed apps under {apps_dir} "
        f"(info.toml created: {info_created}, pydantic files patched: {patched})"
    )


def finalize_package_install(installation_path: str) -> None:
    """finalize_installed_apps wrapper for package installs."""
    finalize_installed_apps(installation_path)


def finalize_repo_install() -> None:
    """finalize_installed_apps wrapper for repository installs."""
    finalize_installed_apps(os.path.join("src", "appworld"))
