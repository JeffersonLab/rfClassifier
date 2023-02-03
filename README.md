# rf_classifier
A program for classifying CEBAF C100 RF faults based on waveform data.

Version 1.0 supported pluggable models, while version 2.0 only supports a single embedded model.  The pluggable model
feature was rarely, if ever, used and required unnecessary maintenance effort.

## Installation

### Certified Install

The developer will generate a certified tarball that removes and development related folders such .git, .idea, .vscode,
etc..  SQAM will use the ``setup-certified.bash`` script to run tests, build documentation, install, and compact the
project back to original state.  Running ``setup-certified.bash -h`` will produce more information on how to install.

### Other Installation

You can do a standard python install process with this.  For both development and deployment, this basic process works
well.  Newer version of pip and setuptools may also work.

Initial installation steps.
```bash
git clone https://github.com/JeffersonLab/rf_classifier
cd rf_classifier
python3.7 -m venv venv
pip install pip==23.0 setuptools=67.1.0
```

You the requirements file to lock the versions for deployment.  If you want to try your luck with the latest packages,
only install the app as it will pull in fresh dependencies.
```bash
pip install -r requirements.txt
pip install -e .
```

## Developer Notes

This package should be developed with it installed in editable mode in a local virtual environment.

First, download code and set up the environment.  New versions of pip and setuptools make work fine.  Older ones caused
errors.
```bash
git clone https://github.com/JeffersonLab/rf_classifier
cd rf_classifier
python3.7 -m venv venv
source venv/bin/activate
pip3 install pip==23.0 setuptools==67.1.0
```

If you want to lock dependencies to the last deployed set, install them from the requirements.txt file.  Otherwise, skip
this step.
```bash
pip install -r requirements
```

If you haven't already installed from requirements.txt, this step will pick up the latest set of dependencies.
```bash
pip install -e .
```

You can run tests the local unit tests.  They require that you are on a JLab network as it downloads the test data as it
is needed.
```bash
python -m unittest
```

When you are done developing, record the current set of dependencies in a requirements.txt and setup.cfg.  You will need
to manually remove rf_classifier from the requirements.txt file afterwards.  Make sure to commit, tag, and push the new
version.
```bash
vi setup.cfg
rm requirements.txt
pip freeze > requirements.txt
```

To generate a certified tarball for a new version of RF classifier, first make a copy of the development code in a
temporary location.  Then remove any extraneous files and directories.  Here we use version 0.1 as an example.
```bash
cd ..
cp -r rf_classifier rf_classifier0.1
cd rf_classifier0.1
rm -rf .git .idea .vscode
find src/ -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
find tests/ -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
cd ..
tar -czf rf_classifier0.1.tgz rf_classifier0.1/
```

## Documentation

Online documentation is available at https://jeffersonlab.github.io/rf_classifier

##Pluggable Models

These are only supported in version 1.0.  Future model updates will be embedded in directly in rf_classifier.

 * Random Forest [https://github.com/JeffersonLab/rf_classifier_random_forest]
 * CNN/LSTM Deep Learning Model [https://github.com/JeffersonLab/rf_classifier_cnn_lstm]