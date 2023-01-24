================================
rf_classifier User Guide
================================

.. toctree::

.. highlight:: none

The rf_classifier appilcation is a command line tool for analyzing C100 waveforms captured at the time of a fault.  The
application leverages a "pluggable" module architecture that allows for the user to access different models to determine
which cavity faulted and which type of fault occurred.

To get application name and version::

  rf_classifier

Example::

  > rf_classifier
  rf_classifier v0.1

To get help messages::

  rf_classifier -h [list_models|analyze]

Example::

  > rf_classifier -h
  usage: main.py [-h] [-c CONFIG_FILE] [-M MODELS_DIR] {list_models,analyze} ...

  rf_classifier v0.1 A program that determines the fault type and offending
  cavity based on a waveform data from a C100 fault event

  positional arguments:
    {list_models,analyze}
                          commands
      list_models         List out available models
      analyze             Analyze a fault event

  optional arguments:
    -h, --help            show this help message and exit
    -c CONFIG_FILE, --config CONFIG_FILE
                          Specify config file (default: cfg/config.yaml)
    -M MODELS_DIR, --models_dir MODELS_DIR
                          Specify the directory contain the models package


To list out available models::

  rf_classifier list_models

Example::

  > rf_classifier list_models
  random_forest_v0_1 (default)

To get detailed information about a single model::

  rf_classifier list_models -v <model_name>

Example::

  > rf_classifier list_models -v random_forest_v0_1
  random_forest_v0_1 (default)
  Release Date:  July 30, 2019
  Cavity Labels: ['multiple', '1', '2', '3', '4', '5', '6', '7', '8']
  Fault Labels:  ['E_Quench', 'Microphonics', 'Quench', 'Single Cav Turn off', 'Multi Cav Turn off']
  Brief:         Uses random forests ensemble method for analysis
  Details:
    This model uses random forest models to identify the faulted cavity and fault type of a C100 event.

    This model is based on work done by Chris Tennant, Tom Powers, etc. and represents the initial model used to
    identify which cavity and fault type is associated with a C100 fault event.  Any individual cavity can be
    identified as the offending cavity.  Any collection of multiple cavities faulting at the same time are given the
    generic label of 'multiple'.  The following fault types may be identified by the model: E_Quench, Microphonics,
    Quench, 'Single Cav Turn off, and Multi-cav Turn Off.

    Additional documentation is available in the package docs folder.


To analyze a fault event using the default model.  Note, the path should include the date and time componenets.::

  rf_classifier analyze /path/to/event/date/time/

Example::

  > rf_classifier analyze /usr/opsdata/waveforms/data/rf/1L26/2018_04_29/193409.3
  Cavity     Fault               Zone     Timestamp              Model                Cav-Conf Fault-Conf
  8          Single Cav Turn off 1L26     2018-04-29 19:34:09.3  random_forest_v0_1   0.99     0.79

To analyze a fault event using a non-default model with JSON output.::

  rf_classifier analyze -m <model_name> -o json /path/to/event/date/time

Example::

  > rf_classifier analyze -m random_forest_v0_1 -o json /data/waveforms/data/rf/1L26/2018_04_29/193409.3
  [
    {
      "location": "1L26",
      "timestamp": "2018-04-29 19:34:09.3",
      "cavity-label": "8",
      "cavity-confidence": 0.988,
      "fault-label": "Single Cav Turn off",
      "fault-confidence": 0.788
    }
  ]

