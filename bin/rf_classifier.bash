#!/bin/env bash

# Get the directory containing this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Activate the apps python environment.
source ${DIR}/../venv/bin/activate
if [ "$?" != "0" ] ; then
    echo "Error activating python virutal environment.  Exiting."
    exit 1
fi

# Make sure our package search path is right
export PYTHONPATH="${DIR}/lib/:${DIR}/..:${PYTHONPATH}"

# Run the app passing along all of the args
python3 ${DIR}/../lib/main.py "$@"
