# Full AppWorld stack: environment + APIs + MCP HTTP (for Genie appworld-routing).
# Published as ghcr.io/sks/appworld:stack by CI on push to main.
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /run

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev build-essential curl git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Seed real bundles from PyPI, then overlay fork source (git checkout has LFS pointers).
RUN uv pip install "appworld[mcp]" --system && \
    python - <<'PY'
import os, shutil, appworld
bundle_dir = os.path.join(os.path.dirname(appworld.__file__), ".source")
shutil.copytree(bundle_dir, "/tmp/appworld-bundles", dirs_exist_ok=True)
print(f"Saved PyPI bundles from {bundle_dir}")
PY

RUN --mount=type=bind,source=.,target=/project-root \
    cd /project-root && uv pip install ".[mcp]" --system && \
    cp -a /tmp/appworld-bundles/. "$(python -c 'import appworld, os; print(os.path.join(os.path.dirname(appworld.__file__), ".source"))')/"

COPY docker/patch_pydantic_apps.py /tmp/patch_pydantic_apps.py

RUN appworld install && \
    python /tmp/patch_pydantic_apps.py && \
    if appworld download data --help 2>/dev/null | grep -q -- "--mode"; then \
        appworld download data --mode minimal; \
    else \
        appworld download data; \
    fi

COPY docker/stack-entrypoint.sh /usr/local/bin/stack-entrypoint.sh
COPY docker/patch_pydantic_apps.py /usr/local/bin/patch_pydantic_apps.py
RUN chmod +x /usr/local/bin/stack-entrypoint.sh

ENV APPWORLD_ROOT=/run
ENV APPWORLD_ENV_PORT=8000
ENV APPWORLD_APIS_PORT=9000
ENV APPWORLD_MCP_PORT=10000

EXPOSE 8000 9000 10000

ENTRYPOINT ["/usr/local/bin/stack-entrypoint.sh"]

LABEL org.opencontainers.image.source=https://github.com/sks/appworld
LABEL org.opencontainers.image.description="AppWorld env+apis+MCP stack for Genie routing eval."
