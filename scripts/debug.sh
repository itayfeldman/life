#
# ./debug.sh

#!/bin/bash

# To debug first run debug.sh in the terminal and then run the Python: Attach to Debugpy configuration

# Activate the virtual environment. This assumes your virtual env is in .virtualenvs/deep
source ~/.virtualenvs/life/bin/activate
python -m debugpy --listen localhost:5678 --wait-for-client -m life "$@"

# Optionally, deactivate at the end of the script
deactivate