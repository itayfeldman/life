#!/bin/bash

#
# Usage: ./scripts/debug.sh
#
# This script activates the Python virtual environment and starts the Python debugger (debugpy),
# allowing a remote debugger (e.g., from VS Code) to attach.

# To debug:
# 1. Make this script executable: chmod +x scripts/debug.sh
# 2. Run this script in your terminal: ./scripts/debug.sh
# 3. In your IDE, run a Python debug configuration to attach to localhost:5678.

# Activate the virtual environment. This assumes your virtual env is in ~/.virtualenvs/life
source ~/.virtualenvs/life/bin/activate
python -Xfrozen_modules=off -m debugpy --listen localhost:5678 --wait-for-client -m life "$@"

# Optionally, deactivate at the end of the script
deactivate