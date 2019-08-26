export PATH="/usr/csite/pubtools/python/3.6.9/bin:$PATH"
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
else
    echo "# No models found to test"
fi
