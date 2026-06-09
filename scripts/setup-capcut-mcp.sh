#!/usr/bin/env bash
#
# Setup script for the CapCut MCP server (CapCutAPI by sun-guannan / ashreo).
#
# CapCut has no official public API and CapCutAPI is not published on PyPI,
# so the documented way to run it is to clone the repo and launch
# `python mcp_server.py`. This script automates the clone + install so the
# MCP config in .claude/settings.json can point at a known location.
#
# Usage:
#   ./scripts/setup-capcut-mcp.sh            # installs into $HOME/CapCutAPI
#   CAPCUT_DIR=/custom/path ./scripts/setup-capcut-mcp.sh
#
set -euo pipefail

CAPCUT_REPO="${CAPCUT_REPO:-https://github.com/sun-guannan/CapCutAPI.git}"
CAPCUT_DIR="${CAPCUT_DIR:-$HOME/CapCutAPI}"

echo "==> CapCut MCP server setup"
echo "    repo: $CAPCUT_REPO"
echo "    dir:  $CAPCUT_DIR"

if [ -d "$CAPCUT_DIR/.git" ]; then
  echo "==> Repo already present, pulling latest"
  git -C "$CAPCUT_DIR" pull --ff-only
else
  echo "==> Cloning CapCutAPI"
  git clone --depth 1 "$CAPCUT_REPO" "$CAPCUT_DIR"
fi

cd "$CAPCUT_DIR"

echo "==> Creating virtual environment (venv-capcut)"
python3 -m venv venv-capcut
# shellcheck disable=SC1091
source venv-capcut/bin/activate

echo "==> Installing MCP dependencies"
if [ -f requirements-mcp.txt ]; then
  pip install -r requirements-mcp.txt
else
  echo "!! requirements-mcp.txt not found; installing base requirements" >&2
  pip install -r requirements.txt
fi

if [ -f config.json.example ] && [ ! -f config.json ]; then
  echo "==> Creating config.json from example"
  cp config.json.example config.json
fi

echo
echo "==> Done."
echo "    Python interpreter: $CAPCUT_DIR/venv-capcut/bin/python"
echo "    MCP entrypoint:     $CAPCUT_DIR/mcp_server.py"
echo
echo "    The .claude/settings.json 'capcut' entry should reference these paths."
echo "    Edit config.json in $CAPCUT_DIR if you need to set CapCut/draft paths."
