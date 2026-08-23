# Full AppWorld stack: environment + APIs + MCP HTTP (for Genie appworld-routing).
# Published as ghcr.io/sks/appworld:stack by CI on push to main.
FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /run

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev build-essential curl git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN --mount=type=bind,source=.,target=/project-root \
    cd /project-root && \
    uv pip install ".[mcp]" --system && \
    python scripts/materialize_bundles_for_install.py apps tests

RUN appworld install && \
    if appworld download data --help 2>/dev/null | grep -q -- "--mode"; then \
        appworld download data --mode minimal; \
    else \
        appworld download data; \
    fi

COPY docker/stack-entrypoint.sh /usr/local/bin/stack-entrypoint.sh
RUN chmod +x /usr/local/bin/stack-entrypoint.sh

ENV APPWORLD_ROOT=/run
ENV APPWORLD_ENV_PORT=8000
ENV APPWORLD_APIS_PORT=9000
ENV APPWORLD_MCP_PORT=10000

EXPOSE 8000 9000 10000

ENTRYPOINT ["/usr/local/bin/stack-entrypoint.sh"]

LABEL org.opencontainers.image.source=https://github.com/sks/appworld
LABEL org.opencontainers.image.description="AppWorld env+apis+MCP stack for Genie routing eval."
