+++++++++++++++++++++
Admin Guide
+++++++++++++++++++++
.. toctree::
    :caption: Contents
    :maxdepth: 1

    Certified Install Guide <certified_install>

=====================
Overview
=====================
.. highlight:: none

This guide is intended to document common steps needed to test and reconfigure the rf_classifier application.


=====================
Generic Installation
=====================
Note: See :ref:`certified-install` for details on installing into CEBAF's certified software repository.

This software is maintained on github at https://github.com/JeffersonLab/rf_classifier.  It was developed against
Python 3.6 using a virtual environment, and it provides a requirements.txt file that can be used to "pip install"
it's package dependencies.  Additionally this documentation is produced using Sphinx.  Once the application is
installed, it's virtual environment created, it's packages installed, and documentation is created, the admin user
should install any available models.  To install this software from github.com to an Accelerator Linux system:

First download the software from github.com to the desired location.  All versions are kept as tags and can be viewed
using git tag -l.  Checkout the desired version after download the git repository.::

    cd /path/to/installation
    git clone https://github.com/JeffersonLab/rf_classifier
    cd rf_classifier
    git tag -l
    git checkout <version-tag>

This application was developed against Python 3.6.9.  A requirements.txt file is included to help with development or initial installation.
The setup-certified script is supplied to make installation along certified guidelines more streamlined, but can be ignored for a generic install.
To create the virtual environment and install dependencies in a Linux/bash environment.:::

    python3.6 -m venv ./venv
    source venv/bin/activate
    pip3 install -r requirements.txt

If desired, build the Spinx-based HTML documentation.  Additionally, launch Firefox to view them.::

    cd docsrc/
    make github
    firefox ../docs/index.html
    cd ..

Run the application's test suite.  No models have been installed so this will be a quick test of the base code.::

    cd tests
    ./tester.bash

Finally, install any models following the guidance below.  Then rerun the test script.


=====================
Software Testing
=====================
A script has been provided for automated testing of rf_classifier and it's associated models.  On Windows this is
tester.ps1, and on Linux this is tester.bash.  These unit tests should all be implemented using the unittest module.
The testing script looks in the module's test directory to discover available tests usings unittest's autodiscovery
feature.  Files named test_*.py are run as unittests, and directories that are valid packages are descended into during
the search.

To run all unit tests associated with the application and it's models, simply execute the test script.::

    cd /cs/certified/apps/rf_classifier/PRO/test
    ./tester.bash

Alternatively, the setup-certified.bash script can be used to run the tester.bash script as well.::

    ./setup-certified.bash test

=====================
Installing A Model
=====================
First note that all models should be added to github under the name rf_classifier_<model_name>, where <model_name> is
the model's unique ID without any version info.  E.g., for my_model_v2_7, <model_name> would be my_model.  This project
should also be linked from the rf_classifier project.

Adding a model amounts to placing a copy of the model's application in the rf_classifier's models directory, creating a
model-local python virtual environment (if needed), installing any of the model's dependencies, and running the model's test files
via the rf_classifier tester script.

Here's an example for deploying a model from github.com using a Linux terminal.  The model's documentation may also
include notes on any non-standard steps.  One specific difference that may occur is in creating documentation.  This
example assumes that the model uses Sphinx documentation which must be built after deployment.

First deploy the model into the model directory of the desired version of the application.  The random_forest model
is available on github and uses Sphinx documentation.  Also note that versions should be saved as git tags.  Checkout
the version that matches the version referenced in the directory name.::

    cd /cs/certified/apps/rf_classifier/PRO/models
    git clone https://github.com/JeffersonLab/rf_classifier_random_forest random_forest_v0_1
    cd random_forest_v0_1
    git checkout v0_1

If needed, create and activate a virtual environment for this model.  The base application works on Python 3.6, but you can use
any interpreter since this is a separate application.::

    /usr/csite/pubtools/python/3.6/bin/python3 -m venv ./venv
    source venv/bin/activate.csh

If needed, install the package dependencies, assuming the model has specified it's package requirements in requirements.txt.::

    pip3 install -r requirements.txt

If needed, build the model's documentation.  This models uses a markdown-based README.md, so nothing needs to be done.

Run the model's test code.  The easiest way is to run the application's tester.bash script and verify that the model's
tests appear and all are passed.  While the models shouldn't require anything more than this, it's always prudent to
check their documentation.::

    cd /cs/certified/apps/rf_classifier/PRO/tests
    ./tester.bash

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
environment and call main.py with an specified arguments.  See the User Guide for more details.

On Linux, use the following bash script:::

    rf_classifier/bin/rf_classifier.bash

On Windows, use the following PowerShell script:::

    rf_classifier\bin\rf_classifier.ps1
