+++++++++++++++++++++
Admin Guide
+++++++++++++++++++++

=====================
Overview
=====================

This guide is intended to document common steps needed to test and reconfigure the rf_classifier application.

=====================
Installation
=====================
This software is maintained on github at https://github.com/JeffersonLab/rf_classifier.  It was developed against
Python 3.6 using a virtual environment, and it provides a requirements.txt file that can be used to "pip install"
it's package dependencies.  Additionally this documentation is produced using Sphinx.  Once the application is
installed, it's virtual environment created, it's packages installed, and documentation is created, the admin user
should install any available models.  To install this software from github.com to an Accelerator Linux system:

First download the software from github.com to the desired location.::

    cd /path/to/installation
    git clone https://github.com/JeffersonLab/rf_classifier

Then create the python virtual environment based on the pubtools python 3.6 version.::

    cd rf_classifier
    /usr/csite/pubtools/python/3.6/bin/python -m venv ./venv

Activate the virtual environment and install required packages.::

    source venv/bin/activate
    pip install < requirements.txt

If desired, build the Spinx-based HTML documentation.  You may need to update the sys.path values in doc/config.py.::




=====================
Software Testing
=====================
A two scripts have been provided for automated testing of rf_classifier and it's associated models.  On Windows this is
tester.ps1, and on Linux this is tester.bash.  These unit tests should all be implemented using the unittest module as the testing script relies on unittests's
autodiscovery feature.  Autodiscovery requires each module must be structured as a valid Python package, i.e., contained
 within a directory having an __init__.py file, and it requires that each test file be named following the test_*.py pattern.


To run all unit tests associated with the application and it's models, simply execute the test script.  For example, on
Linux::

    # cd \cs\certified\apps\rf_classifier\PRO
    # .\tester.bash

=====================
Adding A Model
=====================
First note that all models should be added to github under the name rf_classifier_<model_name>, where <model_name> is
the model's unique ID without any version info.  E.g., for my_model_v2_7, <model_name> would be my_model.  This project
should also be linked from the rf_classifier project.

Adding a model amounts to placing a copy of model python package in the rf_classifier's models directory, creating a
model-local python virtual environment, installing any of the model's dependencies, and running the model's test files
via the rf_classifier tester script.

Here's an example for deploying a model from github.com using a Linux terminal.  The model's documentation may also
include notes on any non-standard steps.  One specific difference that may occur is in creating documentation.  This
example assumes that the model uses Sphinx documentation which must be built after deployment.

First deploy the model into the model directory of the desired version of the application.::

    # cd /cs/certified/apps/rf_classifier/PRO/models
    # git clone https://github.com/JeffersonLab/rf_classifier_random_forest_v0_1 random_forest_v0_1

Then create and activate a virtual environment for this package.  The rf_classifier application is designed to look in
the venv directory for packages this model depends on.::

    # cd random_forest_v0_1
    # python3 -m venv venv
    # source venv/bin/activate

Install the package dependencies, assuming the model has specified it's package requirements in requirements.txt.::

    # pip install -r requirements.txt

If needed, build the model's documentation.  This model uses Sphinx which provides a Makefile and can compile it's reST
files into a number of formats, including html.  Check the documentation via firefox before moving on.::

    # cd docs/source
    # make html
    # firefox ../build/html/index.html

Run the model's test code.  The easiest way is to run the application's tester.bash script and verify that the model's
tests appear and all are passed.::

    # cd /cs/certified/apps/rf_classifier/PRO/
    # tester.bash

===========================
Application Configuration
===========================
rf_classifier reads configuration settings from a YAML formatted configuration file.  The location of this file is
configurable, but the application attempts to read config.yaml from the application directory by default.  The below
tables gives accepted configuration options and their information.

============  ================= ==============
Option        Default Value     Description
============  ================= ==============
models_dir    <app_dir>/models  Directory containing model packages
default_model None              Name of the model to use in analyzing an event

