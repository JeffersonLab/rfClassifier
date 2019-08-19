+++++++++++++++++++++++++++++++++
Pluggable Model API Introduction
+++++++++++++++++++++++++++++++++

=================================
Overview
=================================
The C100 RF Waveform Fault Classifier application, or rf_classifier, was developed to identify the offending cavity and
fault type for RF faults occuring within a C100 cryomodule by analyzing the harvested RF waveforms.  The methods and
models used to analyze these faults are areas of activity development and are given to change over time.  To more easily
accommodate this reality, rf_classifier is designed around "pluggable" models.

=================================
Purpose
=================================
Pluggable models are independent Python application each containing all of the logic required for the parsing and
analysis of the data associated with an RF fault event.  Each package must have it's own documentation, test suite, and
supply it's own package dependencies.  Each model must return output to STDOUT in JSON format as mentioned in the developer
guide.  Since every model will need to perform a number of similar steps (e.g., data parsing or validation), the rf_classifier
application contains python modules that can be linked to or copied and modified within a model application.

=================================
Structure
=================================
The purpose of this documentation is to provide reference documentation for the extra modules provided by rf_classifier.
The base_model module contains the various helper functions, and has two major components of which to be aware.

:class:`base_model.BaseModel`
    Abstract base class defining the model interface
:meth:`base_model.BaseModel.analyze`
    Performs the analysis and returns its results

More detailed information is given in the base_model, mya, and utils module documentation.

base_model
  Contains the BaseModel class definition and all model related methods such as parsing or validating waveform data

mya
  Contains all functions necessary for interacting with JLab's MySQL Archiver (MYA)

utils
  Contains any utility functions not implicitly tied to a specific purpose