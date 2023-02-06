================================
rf_classifier User Guide
================================

.. toctree::

.. highlight:: none

The rf_classifier application is a command line tool for analyzing C100 waveforms captured at the time of a fault.  The
application leverages a "pluggable" module architecture that allows for the user to access different models to determine
which cavity faulted and which type of fault occurred.

To get application name and version::

  bin/rf_classifier.bash

Example::

  > bin/rf_classifier.bash
  rf_classifier v2.0.0


To get help messages::

  bin/rf_classifier.bash -h [describe|analyze]

Example::

  > bin/rf_classifier.bash -h
  usage: main.py [-h] {describe,analyze} ...

  rf_classifier v2.0.0: A program that determines the fault type and offending
  cavity based on a waveform data from a C100 fault event

  positional arguments:
    {describe,analyze}  commands
      describe          Describe the embedded model
      analyze           Analyze a fault event

  optional arguments:
    -h, --help          show this help message and exit

  Pluggable models are no longer available.

To describe the embedded::

  bin/rf_classifier.bash describe

Example::

  > bin/rf_classifier.bash describe

    Model ID:      cnn_lstm_v1_0
    Release Date:  Oct 5, 2022
    Cavity Labels: ['multiple', '1', '2', '3', '4', '5', '6', '7', '8']
    Fault Labels:  ['Controls Fault', 'E_Quench', 'Heat Riser Choke', 'Microphonics', 'Multi Cav turn off', 'Quench_100ms', 'Quench_3ms', 'Single Cav Turn off']
    Training Data: Fall 2019 - Summer 2022 (July 11, 2022)
    Brief:         Uses CNN/LSTM deep learning model to classify RF faults using waveform data extending slightly past the fault.


To get more detailed information about the model::

  bin/rf_classifier.bash list_models describe -v

Example::

  > bin/rf_classifier.bash describe -v

  Model ID:      cnn_lstm_v1_0
  Release Date:  Oct 5, 2022
  Cavity Labels: ['multiple', '1', '2', '3', '4', '5', '6', '7', '8']
  Fault Labels:  ['Controls Fault', 'E_Quench', 'Heat Riser Choke', 'Microphonics', 'Multi Cav turn off', 'Quench_100ms', 'Quench_3ms', 'Single Cav Turn off']
  Training Data: Fall 2019 - Summer 2022 (July 11, 2022)
  Brief:         Uses CNN/LSTM deep learning model to classify RF faults using waveform data extending slightly past the fault.

  Details:
    This model uses CNN/LSTM deep learning models to identify the faulted cavity and fault type of a C100 event based
    on the waveform data captured by harvester daemon.

    This model is based on work done by Chris Tennant, Lasitha Vidyaratne, Md. Monibor Rahman, Tom Powers, etc. and
    represents an improved model used to identify which cavity and fault type is associated with a C100 fault event.
    Any individual cavity can be identified as the offending cavity.  Any collection of multiple cavities faulting at
    the same time are given the generic label of 'multiple'.  The following fault types may be identified by the model:
    Controls Fault, E_Quench, Heat Riser Choke, Microphonics, Quench_100ms, Quench_3ms, Single Cav Turn off, and
    Multi-cav Turn off.  The fault model is no longer trained on Multi Cav turn off, as we use only the cavity model
    to identify that condition.

    Signals analyzed are the GMES, GASK, DETA2, and CRFP waveforms for all eight cavities.  The signals are cropped just
    after the fault, down sampled to 4096 samples, and standardized using a modified z-score with 0.001 fill for
    constant signals.

    The cavity model was first trained on data from Nov 2019 to Feb 2022, then we used transfer learning to train only
    on the data from May 2022 - July 2022.  The fault type model was trained on data from Nov 2019 - July 2022 without
    the use of transfer learning.

    Zone 0L04 continues to be excluded from analysis based on the recommendation of Tom Powers.

    Additional documentation is available in the package docs folder.

To analyze a fault event.  Note, the path should include the date and time componenets.::

  bin/rf_classifier.bash analyze /path/to/event/date/time/

Example::

    > bin/rf_classifier.bash analyze /usr/opsdata/waveforms/data/rf/1L25/2023_02_03/103934.1
    Cavity     Fault               Zone     Timestamp              Model                Cav-Conf Fault-Conf
    1          E_Quench            1L25     2023-02-03 10:39:34.1  cnn_lstm_v1_0        0.97     0.97


In the event of an issue with the data or other error, the output will reflect the issue.::

    >  bin/rf_classifier.bash analyze /usr/opsdata/waveforms/data/rf/1L26/2018_04_29/193409.3
    Zone     Timestamp              Error
    1L26     2018-04-29 19:34:09.3  ValueError('Invalid time range of [-307.15,102.4] found.  Does not include minimum range for fault data [-1534.0, 10.0]')

To analyze a fault event using a non-default model with JSON output.::

    bin/rf_classifier.bash analyze -o json /path/to/event/date/time

Example::

    > bin/rf_classifier.bash analyze -o json /usr/opsdata/waveforms/data/rf/1L25/2023_02_03/103934.1
    {"data": [{"location": "1L25", "timestamp": "2023-02-03 10:39:34.1", "cavity-label": "1", "cavity-confidence": 0.9669561982154846, "fault-label": "E_Quench", "fault-confidence": 0.9688522219657898, "model": "cnn_lstm_v1_0"}]}


