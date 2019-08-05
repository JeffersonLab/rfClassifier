source venv/Scripts/activate

echo "#"
echo "# Running application tests"
echo "#"
python3 -m unittest discover tests -v

echo ""
echo ""
echo "#"
echo "# Running model tests"
echo "#"

# Add the model directory to the environment's PYTHONPATH.  This allows for all of the needed imports.
export PYTHONPATH="./models:./venv/Lib/site-packages"
python3 -m unittest discover ./models -v


deactivate
