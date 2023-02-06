.. rf_classifier documentation master file, created by
   sphinx-quickstart on Wed Jul 31 11:48:40 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

+++++++++++++++++++++++++++++++++++++++++
Welcome to rf_classifier's documentation!
+++++++++++++++++++++++++++++++++++++++++

=========================================
Overview
=========================================
rf_classifier is a command line application for analyzing C100 waveform data generated at the time of a fault.  It
allows the user to determine (i.e., classify) which cavity faulted and which type of fault was experienced.  It does
this analysis through the use an embedded machine learning model that analyzes a set of waveform capture files.  The
model should also supply information about the confidence a user should place in these labels.  Interpreting these
confidence values can sometimes be more art than science.

Users and developers of this software should review the User Guide, Developer Guide, and API documentation
as needed, respectively for more information.

To get certified installation instructions, run './setup-certified.bash -h'.  Otherwise, see the project README.md file.

.. toctree::
    :caption: Contents
    :maxdepth: 1

    Introduction <self>
    User Guide <user_guide/index>
    Developer Guide <dev_guide/index>
    API Documentation <dev_guide/api/index>
    Links <links>



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
