#!/bin/env bash

# Get the directory containing this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Make sure our package search path is right
export PATH="/usr/csite/pubtools/python/3.6.9/bin:$PATH"
export PYTHONPATH="${DIR}/lib/:${DIR}/..:${PYTHONPATH}"

# Run the app passing along all of the args
python3 ${DIR}/../lib/main.py "$@"
