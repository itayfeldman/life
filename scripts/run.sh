#
# ./run.sh

#!/bin/bash

# Activate the virtual environment. This assumes your virtual env is in .virtualenvs/deep
source ~/.virtualenvs/life/bin/activate
python -m life "$@"

# Optionally, deactivate at the end of the script
deactivate
