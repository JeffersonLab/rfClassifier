source ../venv/bin/activate
export PYTHONPATH="../lib:../models:../venv/lib/site-packages"

echo "#"
echo "# Running application tests"
echo "#"
python3 -m unittest discover . -v

echo ""
echo ""
# Add the model directory to the environment's PYTHONPATH.  This allows for all of the needed imports.
if [ "$(ls ../models | wc -w)" != '0' ] ; then
    echo "#"
    echo "# Running model tests"
    echo "#"

    python3 -m unittest discover ../models -vl
else
    echo "# No models found to test"
fi

deactivate
