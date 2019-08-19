# Load the applications virtual environment
& ..\venv\Scripts\Activate.ps1

# Add the lib directory that contains all of the python code to the search path
$env:PYTHONPATH = "..\lib"

echo "#"
echo "# Running application tests"
echo "#"

# Run any unit tests that match unittests autodiscovery criteria (any test_*.py in a valid package, etc.)
python -m unittest discover . -v

# Unload the applicaiton virtual environment
deactivate

# Move on to test all of the models
echo ""
echo ""
echo "#"
echo "# Running model tests"
echo "#"

# Clear the search path from above
$env:PYTHONPATH = ""

# List out each file/directory in the models dir.  Exclude dot files like .gitignore, etc.
Get-ChildItem "..\models" -Exclude '.*' | ForEach-Object {

    $model = $_.BaseName
    echo "## $model ##"

    # Load the models virtual environment
    & ..\models\$model\venv\Scripts\Activate.ps1

    # Run any unittests they have
    python -m unittest discover "..\models\$model\test\" -v

    # Unload the virtual environment of the current model
    deactivate
    echo ""
}
