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
These pluggable models are essentially independent Python packages each containing all of the logic required for an
analysis of the data associated with an RF fault event.  Each package must have it's own documentation, test suite, and
supply it's own package dependencies.  In addition, each model package must implement a class named **Model** that
inherits from an abstract base class, BaseModel, implement in this base_model module.  This defines the generic
interface that rf_classifer uses to interact with the models and allows for a separation of the application's other
concerns (command line interface, external software integration, etc.).  Importantly, this allows for separate development
efforts on both the model and application components to occur simultaneously with little interference or coordination.

=================================
Structure
=================================
The purpose of this documentation is to define the model interface to rf_classifier.  The interface itself is simple.
Inherit from a specific class and define two methods, describe() and analyze().

:class:`base_model.BaseModel`
    Abstract base class defining the model interface
:meth:`base_model.BaseModel.describe`
    Returns information about the model
:meth:`base_model.BaseModel.analyze`
    Performs the analysis and returns its results

More detailed information is given in the base_model module documentation.

In addition to defining an interface through the base_model module, this application also provides a number of concrete
methods which should aid in parsing and validating RF fault event waveform data.  These additional functions are spread
across the base_model, mya, and utils modules.

base_model
  Contains the BaseModel class definition and all model related methods such as parsing or validating waveform data

mya
  Contains all functions necessary for interacting with JLab's MySQL Archiver (MYA)

utils
  Contains any utility functions not implicitly tied to a specific purpose