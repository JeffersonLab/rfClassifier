+++++++++++++++++++++++++++++++++
Embedded Model API Introduction
+++++++++++++++++++++++++++++++++

=================================
Overview
=================================
The C100 RF Waveform Fault Classifier application, or rf_classifier, was developed to identify the offending cavity and
fault type for RF faults occuring within a C100 cryomodule by analyzing the harvested RF waveforms.  Older versions of
this software supported multiple pluggable models.  In practice, only the most recent model was of use.  Newer versions
of the software now include a single embedded model, but the application code is structured so that updating that model
should be a relatively straightforward process.

=================================
Developer Notes
=================================
All of the model code and artifacts should be place under the rf_classifier.model package.  The tests directory has a
unit test for the model that uses the test_set.txt to validate proper model operations.  Data for the faults given in
this file are dynamically loaded and require a JLab network connection.  Additional fault data is kept in
tests/test-data.  These files are used to test the validation processes of the embedded model.  Bad data typically stays
bad for new models, so this data kept with the application, while the examples that new model chooses to validate
against may change over time and is dynamically loaded.

When a new model is prepared.  Generate a new test/test_set.txt that lists the faults the model will be run on, and the
expected results.  Care should be used to select data where the fault would raise an exception (i.e., invalid data),
and faults of a variety of types and confidences.

=================================
Structure
=================================
The purpose of this documentation is to provide reference documentation for the extra modules provided by rf_classifier.
The rf_classifier.model.model module contains the various helper functions, and has two major components of which to be aware.

:class:`rf_classifier.model.model.Model`
    Model class for defining the model interface
:meth:`rf_classifier.model.model.Model.analyze`
    Performs the analysis and returns its results
:meth:`rf_classifier.model.model.Model.update_example`
    Loads the data associated with the specified example

More detailed information is given in the model and utils module documentation.

rf_classifier.model.model
  Contains the Model class definition and all model related methods such as parsing or validating waveform data

rf_classifier.utils
  Contains any utility functions not implicitly tied to a specific purpose