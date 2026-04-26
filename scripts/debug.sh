#!/bin/bash
#
# Starts the app under debugpy so a remote debugger can attach.
#
# Usage:
#   ./scripts/debug.sh [life args...]
#
# In your IDE, attach to localhost:5678 with a Python remote-attach config.

cd "$(dirname "$0")/.."
uv run python -Xfrozen_modules=off -m debugpy --listen localhost:5678 --wait-for-client -m life "$@"
