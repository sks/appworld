#!/usr/bin/env bash
# Start env + apis + MCP HTTP for Genie and other MCP clients.
set -euo pipefail

ROOT="${APPWORLD_ROOT:-/run}"
ENV_PORT="${APPWORLD_ENV_PORT:-8000}"
APIS_PORT="${APPWORLD_APIS_PORT:-9000}"
MCP_PORT="${APPWORLD_MCP_PORT:-10000}"

cd "${ROOT}"

python /usr/local/bin/patch_pydantic_apps.py

if appworld serve multiple --help 2>/dev/null | grep -q -- '--environment'; then
  exec appworld serve multiple \
    --environment '' \
    --apis '' \
    --mcp "http --port ${MCP_PORT}" \
    --root "${ROOT}"
fi

echo "appworld serve multiple unavailable; starting env+apis+mcp separately" >&2

appworld serve apis --no-show-usage --port "${APIS_PORT}" --root "${ROOT}" &
apis_pid=$!
sleep 3
appworld serve environment --no-show-usage --port "${ENV_PORT}" --root "${ROOT}" &
env_pid=$!
sleep 2

if appworld serve mcp --help 2>/dev/null | grep -q http; then
  appworld serve mcp http \
    --remote-apis-url "http://127.0.0.1:${APIS_PORT}" \
    --port "${MCP_PORT}" \
    --root "${ROOT}" &
  mcp_pid=$!
else
  echo "ERROR: appworld serve mcp not available in this image" >&2
  exit 1
fi

trap 'kill ${apis_pid} ${env_pid} ${mcp_pid} 2>/dev/null || true' EXIT INT TERM
wait -n
exit $?
