venv\Scripts\activate

echo "#"
echo "# Running application tests"
echo "#"
python -m unittest discover tests -v

echo ""
echo ""
echo "#"
echo "# Running model tests"
echo "#"
python -m unittest discover \Users\adamc\code\config\rfClassifier\v1 -v


deactivate