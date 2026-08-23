import argparse
import os
import subprocess


def default_image_name() -> str:
    if env_image := os.environ.get("APPWORLD_IMAGE"):
        return env_image
    repository = os.environ.get("GITHUB_REPOSITORY", "stonybrooknlp/appworld")
    return f"ghcr.io/{repository}"


def main():
    parser = argparse.ArgumentParser(
        description="Build and optionally push Docker multi-arch image(s) to GHCR."
    )
    parser.add_argument("--username", help="GitHub username", default="harshtrivedi")
    parser.add_argument("--password", help="GitHub personal access token", default="")
    parser.add_argument(
        "--tag",
        default="latest",
        help="Tag for the Docker image. It can be latest, source, stack or vX.Y.Z (e.g., v0.1.0)",
    )
    parser.add_argument(
        "--image",
        default=default_image_name(),
        help="Image repository (default: ghcr.io/$GITHUB_REPOSITORY or ghcr.io/stonybrooknlp/appworld)",
    )
    parser.add_argument(
        "--dockerfile",
        default="dockerfile",
        help="Dockerfile path relative to repo root (default: dockerfile)",
    )
    parser.add_argument("--push", action="store_true", help="Flag to push the image after building")
    parser.add_argument("--no-cache", action="store_true", help="Flag to build without cache")
    parser.add_argument(
        "--platforms",
        default="linux/amd64,linux/arm64",
        help="Comma-separated platforms for buildx when --push is set",
    )
    args = parser.parse_args()
    username = args.username
    password = (
        args.password
        or os.environ.get("GH_PACKAGES_TOKEN", "")
        or os.environ.get("GITHUB_TOKEN", "")
    )
    if not password:
        raise ValueError("GitHub personal access token not provided.")
    image_name = args.image
    tag = args.tag
    if tag not in ["latest", "source", "stack"] and not tag.startswith("v"):
        raise ValueError("Tag should be latest, source, stack or start with v.")
    is_upstream = image_name == "ghcr.io/stonybrooknlp/appworld"
    if tag == "source" and args.push and is_upstream:
        raise ValueError("The source tag is for local testing only and is not meant to be pushed.")
    # Login (avoid exposing token via args)
    command = ["docker", "login", "--username", username, "--password", password, "ghcr.io"]
    print(" ".join(command))
    subprocess.run(command, check=True)
    appworld_version = tag.lstrip("v")
    if tag == "stack":
        appworld_version = "source"
    if args.push:
        # With --push, build a multi-arch manifest using buildx
        build_cmd = [
            "docker",
            "buildx",
            "build",
            ".",
            "--file",
            args.dockerfile,
            "--platform",
            args.platforms,
            "--build-arg",
            f"APPWORLD_VERSION={appworld_version}",
            "-t",
            f"{image_name}:{tag}",
            "--push",
        ]
    else:
        # Without --push, Docker cannot store a multi-arch manifest locally.
        # So we build for the host architecture only.
        build_cmd = [
            "docker",
            "build",
            ".",
            "--file",
            args.dockerfile,
            "--build-arg",
            f"APPWORLD_VERSION={appworld_version}",
            "-t",
            f"{image_name}:{tag}",
        ]
    if args.no_cache:
        build_cmd.append("--no-cache")
    print(" ".join(build_cmd))
    subprocess.run(build_cmd, check=True)


if __name__ == "__main__":
    main()
