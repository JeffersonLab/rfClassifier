source ../venv/bin/activate
export PYTHONPATH="../lib:"

echo "#"
echo "# Running application tests"
echo "#"
python3 -m unittest discover . -v

# Put the python environment back to stock
export PYTHONPATH=""
deactivate

# Move on to test all of the models
echo ""
echo ""
echo "#"
echo "# Running model tests"
echo "#"

# List out each file/directory in the models dir. Exclude dot files like .gitignore
for model in `ls ../models`
do
    echo "## $model ##"

    # Load the models virtual environment
    source ../models/$model/venv/bin/activate

    # Run any unittests they have
    python3 -m unittest discover "../models/$model/test" -v

    # Unload the virtual environment
    deactivate
    echo ""
done 
