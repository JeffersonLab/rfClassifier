#/bin/bash
export PATH="/usr/csite/pubtools/python/3.6.9/bin:$PATH"
export PYTHONPATH="../lib:"

echo "#"
echo "# Running application tests"
echo "#"
python3 -m unittest discover . -v

# Put the python environment back to stock
export PYTHONPATH=""

# Move on to test all of the models
echo ""
echo ""
echo "#"
echo "# Running model tests"
echo "#"

for mod in $(ls ../models)
do
    mod_dir="../models/$mod"
    echo "# $mod"
    if [ -d "$mod_dir/venv" ] ; then
        source $mod_dir/venv/bin/activate
    fi
    python3 -m unittest discover ../models/$mod/test -v
    if [ -d "$mod_dir/venv" ] ; then
        deactivate
    fi
done
