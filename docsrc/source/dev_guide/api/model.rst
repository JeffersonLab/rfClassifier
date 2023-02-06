################################
base_model Module Documentation
################################

================================
Overview
================================
This module defines the model interface expected by the rfClassifier application.  Specifically, the model module should
provide an update_example method that selects the fault to analyze and an analyze method that does all work related to
classifying the fault, including data validation.

The embedded model needs to also provide a description.yaml file that provides a description of the model which can be
parsed and presented by the main rf_classifier method.

Additional methods are provided that ease the process of parsing and validating RF fault event directories.


================================
model Class
================================
.. automodule:: rf_classifier.model.model
    :members: