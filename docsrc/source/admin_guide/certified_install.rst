.. _certified-install:

++++++++++++++++++++++++
Certified Install Guide
++++++++++++++++++++++++
.. highlight:: none

This guide is meant to describe the process used to install the software into the CEBAF Accelerator Certified Software
repository.

=====================
Versioned Tarball
=====================

The SQAM likes to work with a simple tarball of the source code for the version to be installed.  Download the repo from
github, checkout the version, create a gzipped tarball of the source.::

    cd /tmp
    git clone https://github.com/JeffersonLab/rf_classifier
    cd rf_classifier
    git tag -l
    git checkout <version_tag>
    rm -rf .git
    cd ..
    mv rf_classifier rf_classifier_v<version_number>
    tar -czf rf_classifier_v<version_number>.tar.gz rf_classifier_v<version_number>

Now email this version tarball to the SQAM aka Chris Slominski.

=====================================
SQAM Application Install Guide
=====================================

Download the tarball to somewhere temporary and unpack it.::

    cd /tmp/
    tar -xzf rf_classifier_v<version_number>.tar.gz
    cd rf_classifier_v<version_number>

Run the "build" setup step to generate documentation, etc.  Optionally run firefox to inspect.::

    ./setup-certified.bash build
    firefox docs/index.html &

Run the "test" setup step to test the base application.::

    ./setup-certified.bash test

Once you have your audit files and are ready to deploy, you will need to update the audit portions of the documentation.
The documentation expects to find audit files named diff<version>.txt (e.g., diff1.2.3.txt) in the directory named
"docsrc/audit".  Please make any simple edits related to release notes in docsrc/source/release_notes.rst.  Once done,
rerun "setup-certified.bash build" to update the documentation.::

    vi docsrc/audit/diff<version>.txt
    vi docsrc/source/release_notes.rst
    ./setup-certified.bash build
    firefox docs/release_notes.html &

Now perform the SQAMY duties of copying this documentation to the certified project area.  This means you need to copy
the entire contents of the docs directory to the projects' certified web directory.

When that is done, make a copy of this application in the application directory.  Then run the "install" setup step.::

   cp -r ../rf_classifier_v<version_number> /cs/certified/apps/rf_classifier/<version_number>/
   cd /cs/certified/apps/rf_classifier/<version_number>
   ./setup-certified.bash install

Now that the software is installed, you can run the compact step back in the temporary copy of the software.  Then create
the official source code tarball.::

    cd /tmp/rf_classifier_v<version_number>
    ./setup-certified.bash compact
    cd ../
    tar -czf rf_classifier_v<version_number>.tar.gz rf_classifier_v<version_number>


Finally, you will need to create links to any supported models.  If this is the first install, there aren't yet any
models, and you will need to continue in Model Install Guide below.  Remember, the links should include in their name
both the model name and model version.  To create a link to a model:::

    cd /cs/certified/apps/rf_classifier/<version>/models
    ln -s /usr/csite/certified/libexec/rf_classifier_models/<model_name>_v<model_version> .

==================================
SQAM Model Install Guide
==================================

**Note: these steps will need to be repeated for each supported architecture.**

Once the application has been installed, you will need to install a model application.  You should have received a
versioned tarball, similar to the main rf_classifier, containing the software to be installed.  Unpack this tarball
somewhere temporary.::

    cd /tmp/
    tar -xzf <model>_v<version>.tar.gz

The model will have a README.md file in it's root.  Follow the instructions in it for setting it up.  This will likely
include building an architecture dependent Python virtual environment, and run the test/test_model.py script after
activating that venv.  You will need to repeat this step for every supported architecture.

Once the model has been setup for the architecture, make the needed directories under the rf_classifer certified
application directory and copy over the new model.  You will need to repeat this step for every supported architecture.::

    cd /cs/certified/apps/rf_classifier
    mkdir -p models/<model_name>/<model_version>/<arch>
    cp -r /tmp/<model>_v<version>/* models/<model_name>/<model_version>/<arch>

Then create the architecture dependent certified libexec links.  You will need to do this step on every supported
architecture.::

    cd /usr/csite/certified/libexec
    mkdir rf_classifier_models
    cd rf_classifier_models
    ln -s /cs/certified/apps/rf_classifier/models/<model_name>/<model_version>/<arch> <model_name>_v<model_version>

Finally, link this model into a supporting version of rf_classifier.  You may need to speak with the developer to find
out which versions are supported.  **Note: this needs to be done for each supported architecture for the application.**::

    cd /cs/certified/apps/rf_classifier/<version>/models
    ln -s /usr/csite/certified/libexec/rf_classifier_models/<model_name>_v<model_version> .

Then test that this model is useable.  Run rf_classifiers tester script.  It should pickup the model's tests.  Also,
try to run the model.::

    cd ../
    tests/tester.bash
    bin/rf_classifier.bash list_models <model_name>_v<model_version>
    bin/rf_classifier.bash analyze -m <model_name>_v<model_version> /usr/opsdata/waveforms/data/rf/<zone>/<date>/<timestamp>/
