#!/bin/env bash

# Get the directory containing this script
DIR="$( cd "$( dirname "$(readlink -f "${BASH_SOURCE[0]}")" )" >/dev/null 2>&1 && pwd )"

# Activate the virtual environment
source ${DIR}/../venv/bin/activate

# Run the app passing along all of the args
python3 -m rf_classifier.main "$@"

# Put the environment back the way it was.  Probably unnecessary, but just in case the source does something unexpected.
deactivate
