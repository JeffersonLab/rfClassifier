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

First download the software from github.com to the desired location.  All versions are kept as tags.  Checkout the desired
version after download the git repository.::

    cd /path/to/installation
    git clone https://github.com/JeffersonLab/rf_classifier
    git tag -l
    git checkout <version-tag>

Then create the python virtual environment based on the pubtools python 3.6 version.::

    /usr/csite/pubtools/python/3.6/bin/python3 -m venv ./venv

Activate the virtual environment and install required packages.  Source venv/bin/activate for bash shells::

    source venv/bin/activate.csh
    pip3 install -r requirements.txt

If desired, build the Spinx-based HTML documentation.  Launch Firefox to view them.::

    cd docs/
    make html
    firefox build/html/index.html

Run the application's test suite.  No models have been installed so this will be a quick test of the base code.::

    cd ../tests
    bash ./tester.bash

Finally, install any models following the guidance below.  Then rerun the test script.


=====================
Software Testing
=====================
A two scripts have been provided for automated testing of rf_classifier and it's associated models.  On Windows this is
tester.ps1, and on Linux this is tester.bash.  These unit tests should all be implemented using the unittest module as the testing script relies on unittests's
autodiscovery feature.  Autodiscovery requires each module must be structured as a valid Python package, i.e., contained
within a directory having an __init__.py file, and it requires that each test file be named following the test_*.py pattern.


To run all unit tests associated with the application and it's models, simply execute the test script.  For example, on
Linux::

    cd /cs/certified/apps/rf_classifier/PRO/test
    bash ./tester.bash

=====================
Installing A Model
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

First deploy the model into the model directory of the desired version of the application.  The random_forest model
is available on github and uses Sphinx documentation.::

    cd /cs/certified/apps/rf_classifier/PRO/models
    git clone https://github.com/JeffersonLab/rf_classifier_random_forest random_forest_v0_1

Then create and activate a virtual environment for this package.  The rf_classifier application is designed to look in
the venv directory for packages this model depends on.  Use the pubtools python 3.6 version to be consistent with the
base application's interpreter.::

    cd random_forest_v0_1
    /usr/csite/pubtools/python/3.6/bin/python3 -m venv ./venv
    source venv/bin/activate.csh

Install the package dependencies, assuming the model has specified it's package requirements in requirements.txt.::

    pip3 install -r requirements.txt

If needed, build the model's documentation.  This model uses Sphinx which provides a Makefile and can compile it's reST
files into a number of formats, including html.  Check the documentation via firefox before moving on.::

    cd docs/source
    make html
    firefox ../build/html/index.html

Run the model's test code.  The easiest way is to run the application's tester.bash script and verify that the model's
tests appear and all are passed.::

    cd /cs/certified/apps/rf_classifier/PRO/tests
    bash ./tester.bash

===========================
Application Configuration
===========================
rf_classifier reads configuration settings from a YAML formatted configuration file.  The location of this file is
configurable, but the application attempts to read cfg/config.yaml from the application directory by default.  The
below tables gives accepted configuration options and their information.

=============  ================= ==============
Option         Default Value     Description
=============  ================= ==============
models_dir     <app_dir>/models  Directory containing model packages
default_model  None              Name of the model to use in analyzing an event
=============  ================= ==============

==========================
Running the Application
==========================
This project has launcher scripts for running the application from Linux and Windows.  These scripts setup the Python
environment and call main.py with an specified arguments.

On Linux, use the following bash script:::

    rf_classifier/bin/rf_classifier.bash

On Windows, use the following PowerShell script:::

    rf_classifier\bin\rf_classifier.ps1
