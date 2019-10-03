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
This guide is intended to help new developers quickly get up to speed.  The rf_classifier application is made up of essentially two types of software components, the main rf_classifier python application and the pluggable models.  The main application is designed to be as minimal as possible while still capable of processing user input, stored configuration, and loading pluggable models.  The pluggable models are responsible for the majority of the application's workload - namely classifying C100 RF faults based on waveform data captured at the time of the fault.  The classification models used in this process will likely be under development for some time as better models are created and additional classes of faults are identified.

These pluggable models will be developed by different parties using different techniques and relying on different Python software stacks.  Current machine learning software stacks are often very particular about dependency versions.  Maintaining a single Python package source would eventually run into difficult to resolve version conflicts.  Supporting pluggable models is achieved by making each model a separate application, capable of having a separate Python environment.  However, each model must still adhere to some standards that allow interoperability.

See the API Documentation for details on supporting modules.

================================
Pluggable Model Requirements
================================

Pluggable models must meet the following requirements.

 - models must be directories with the following structure:::

    <model_dir>/
        bin/model.bash
        docs/
        lib/
        test/
            test-data/
            test_*.py
        description.yaml
        requirements.txt

   where

   + <model_dir> is a string of the format <model_name>_<model_version>
   + bin/model.bash is the executable used to interact with the model.  It should accept the path to event directories as it's only arguments.  Optionally, a model.ps1 may be inlucded for Windows support/
   + docs/ contains the following:

     - documentation about the model and how it functions
     - installation instructions for the model
     - a description of the data on which the model was trained

   + lib/ will contain any python code or Pickle files associated with the model
   + test/ will contain all files associated with running unittest-based unit tests

     - all test scripts should be based on unittest and be named in such a way that they are discoverable by the unittest module start from the test directory (e.g., named with a leading "test_")
     - tests should include actual waveform data
     - models must include at least one test script

   + description.yaml is a YAML formatted file that contains information about the model.  Is should include at least
     the following fields.

     - id: The model identifier, i.e., <model_name>_<model_version>
     - releaseDate: The model's release date
     - cavLabels: An array containing all possible valid cavity string labels associated with the model's output
     - faultLabels: An array containing all possible valid string fault type labels associated with the model's output
     - brief: A one-line description of the model
     - details: A longer description detailing any important features of the model

   + requirements.txt: An optional file that is used by pip (usually in conjunction with virtualenv) to install the
     model's package dependencies.

 - models must return a JSON object with the following structure.::
    {
        "data": [
            {
                "cavity-label": <string>,
                "cavity-confidence": <float>,
                "fault-label": <string>,
                "fault-confidence: <float>,
                "location": <string>
                "timestamp": <string>
            }
        ]
    }

   where

   + cavity-label and fault-label are strings defined by the model for classifying faults
   + cavity-confidence and fault-confidence are numbers in [0,1] or None relaying the confidence of the model in it's classification
   + timestamp is a string of the format 'yyyy-mm-dd HH:MM:ss.S", e.g., '2019-12-25 22:45:13.5'
   + location is a string representing the zone where this event occurred

In order to make developing these models more straight forward, the application contains code that may be linked to or
copied into a model and modified.  This code is contained in three Python modules, mya.py, utils.py, and base_model.py.
base_model.py relies on utils.py and mya.py, and contains a number of convenient functions for validating and parsing
waveform data found in an event directory.  Additionally the base_model module defines a class BaseModel
with a single abstract method, analyze(), which is to be defined in child classes and should return the results of the
classification analysis.

Developers should see https://github.com/JeffersonLab/rf_classifier_random_forest for an example of a pluggable model
and reference the API Documentation for details of the base_model, mya, and utils modules.
