#
# ./run.sh --strategy spx_delta

#!/bin/bash

# Activate the virtual environment. This assumes your virtual env is in .virtualenvs/deep
source ~/.virtualenvs/pydev/bin/activate

# Now run your Python script.  Replace with the actual path
python ~/Code/Projects/life/src/life/__main__.py "$@"

# Optionally, deactivate at the end of the script
deactivate
