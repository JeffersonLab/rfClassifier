################################
rf_classifier Developer Guide
################################

.. toctree::
    :caption: Contents

    Introduction <self>
    Generating Documentation <docs>

================================
Overview
================================
This guide is intended to help new developers quickly get up to speed.  The rf_classifier application is made up of essentially two types software components, the main rf_classifier python application and the pluggable models.  The main application is designed to be as minimal as possible while still capable of processing user input, stored configuration, and loading pluggable models.  The pluggable models are responsible for the majority of the application's workload - namely classifying C100 RF faults based on waveform data captured at the time of the fault.  The classification models used in this process will likely be under development for some time as better models are created and additional classes of faults are identified.

These pluggable models will be developed by different parties using different techniques and relying on different Python software stacks.  The current machine learning software stacks are notoriously fragile to version conflicts, and maintaining a single Python package source would almost certainly run into difficult to resolve package version conflicts.  Given this, supporting pluggable models can be achieved in one of two ways.  A simple, but less efficient approach, would to have these models each be their own application that could be called by a single front end script.  However, rf_classifier uses a different approach where each model is developed separately with it's own virtual environment based on a version of python matching the rf_classifier's main application (currently version 3.6.9).  Since a single application will only import one package of a given name, it is important that the main application component be as simple as possible and only load a minimal set of modules.  Just prior to importing a pluggable model, the main application will update it's sys.path to include the model's venv's site-package directory and base directory.  Once the model has been loaded, only a small set of methods from the model will be called.

See the API Documentation for more details.

================================
Pluggable Model Requirements
================================
Pluggable models must meet the following requirements.

 - models must be valid Python packages (i.e., directories containing a __init__.py file)
 - models must define a class Model that must inherit from base_model.BaseModel, in a module named model.py

    + BaseModel defines two abstract methods:

        - analyze() which returns the results of the classification analysis
        - describe() which returns descriptive information about the model itself

    + BaseModel defines a single constructor which takes the path to a fault event data directory as a string
    + BaseModel also defines a number of helpful methods for validating and parsing waveform capture files

 - models must include at least one test script

    + scripts must be named test_*.py so that they will be autodiscoverable
    + based on Python package unittest
    + tests the predictions made on a variety of fault waveforms

 - models must include a docs directory containing

    + documentation about the model and how it functions
    + installation instructions for the model
    + a description of the data on which the model was trained

Developers should see https://github.com/JeffersonLab/rf_classifier_random_forest for an example of a pluggable model.
