..\venv\Scripts\Activate.ps1

$env:PYTHONPATH = "..\lib;..\models;..\venv\Lib\site-packages"

echo "#"
echo "# Running application tests"
echo "#"
python -m unittest discover . -v

echo ""
echo ""
echo "#"
echo "# Running model tests"
echo "#"

# Add the model directory to the environment's PYTHONPATH.  This allows for all of the needed imports.
python -m unittest discover ..\models -v


deactivate
