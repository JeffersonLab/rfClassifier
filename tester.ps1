venv\Scripts\Activate.ps1

echo "#"
echo "# Running application tests"
echo "#"
python -m unittest discover tests -v

echo ""
echo ""
echo "#"
echo "# Running model tests"
echo "#"

# Add the model directory to the environment's PYTHONPATH.  This allows for all of the needed imports.
$env:PYTHONPATH = "C:\Users\adamc\code\config\rf_classifier\v1\models"
python -m unittest discover \Users\adamc\code\config\rf_classifier\v1 -v


deactivate