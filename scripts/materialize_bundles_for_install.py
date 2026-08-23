"""Pack or fetch bundle files and copy them into the installed package.

CI and Docker builds use this when Git LFS bandwidth is unavailable. The git
checkout only has LFS pointer stubs for bundle files; when plaintext app
directories are not unpacked, bundles are copied from the PyPI wheel instead.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import appworld

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPI_APPWORLD_SPEC = os.environ.get("APPWORLD_PYPI_SPEC", "appworld[mcp]")


def pack_source_bundles(bundle_names: list[str] | None = None) -> None:
    module_path = REPO_ROOT / "scripts" / "pack_source_bundles.py"
    spec = importlib.util.spec_from_file_location("pack_source_bundles", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(REPO_ROOT))
    spec.loader.exec_module(module)
    module.pack_source_bundles(bundle_names=bundle_names)


def copy_bundles_from_pypi(bundle_names: list[str]) -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        subprocess.run(
            ["uv", "pip", "install", f"--target={temporary_directory}", PYPI_APPWORLD_SPEC],
            check=True,
        )
        for bundle_name in bundle_names:
            source = Path(temporary_directory) / "appworld" / ".source" / f"{bundle_name}.bundle"
            if not source.exists():
                raise FileNotFoundError(f"PyPI package missing bundle: {source}")
            if bundle_name in ("apps", "tests"):
                destination = REPO_ROOT / "src" / "appworld" / ".source" / f"{bundle_name}.bundle"
            else:
                destination = REPO_ROOT / "generate" / ".source" / f"{bundle_name}.bundle"
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            print(f"Copied PyPI bundle {source} -> {destination}")


def materialize_bundles(bundle_names: list[str] | None = None) -> None:
    if bundle_names is None:
        bundle_names = ["apps", "tests"]
    previous_cwd = Path.cwd()
    os.chdir(REPO_ROOT)
    try:
        try:
            pack_source_bundles(bundle_names=bundle_names)
        except (FileNotFoundError, OSError) as error:
            print(f"pack_source_bundles failed ({error}); falling back to PyPI bundles")
            copy_bundles_from_pypi(bundle_names=bundle_names)
    finally:
        os.chdir(previous_cwd)

    package_root = os.path.dirname(appworld.__file__)
    package_source = os.path.join(package_root, ".source")
    os.makedirs(package_source, exist_ok=True)
    for bundle_name in bundle_names:
        if bundle_name in ("apps", "tests"):
            repo_bundle = REPO_ROOT / "src" / "appworld" / ".source" / f"{bundle_name}.bundle"
        else:
            repo_bundle = REPO_ROOT / "generate" / ".source" / f"{bundle_name}.bundle"
        if not repo_bundle.exists():
            raise FileNotFoundError(f"packed bundle not found: {repo_bundle}")
        destination = os.path.join(package_source, f"{bundle_name}.bundle")
        if os.path.abspath(repo_bundle) == os.path.abspath(destination):
            print(f"Bundle already in package path: {destination}")
            continue
        shutil.copy2(repo_bundle, destination)
        print(f"Copied {repo_bundle} -> {destination}")


def main() -> None:
    names = sys.argv[1:] or ["apps", "tests"]
    materialize_bundles(bundle_names=names)


if __name__ == "__main__":
    main()
