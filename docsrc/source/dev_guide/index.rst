################################
rf_classifier Developer Guide
################################

.. toctree::
    :caption: Contents

    Introduction <self>
    API <api/index>

================================
Overview
================================
The latest version of rf_classifier has been streamlined to only allow for a single embedded model.  Please refer to
the included API documentation when updating this embedded model.  Everything for the model should be contained under
the rf_classifier.model package following a similar format as is currently employed.

=========================
Documentation Tips
=========================
This project uses Sphinx, restructured text (reST), google's doc string format conventions, and a "Read The Docs" theme.  The resulting HTML documentation can be built locally for use within the certified software repository and is also uploaded https://jeffersonlab.github.io/rf_classifier via the gh-pages git branch.  This page explains the process of updating the documentation on github.io.  This process is automated for certified in the setup-certified.bash script.

In the past, GitHub pages work by using a special git branch to contain your documentation.  Currently, GitHub lets you create a special directory, docs/, on the master branch in the root of your project, that is parse to present your documentation on a github.io webpage.  Place all Sphinx documentation under /docsrc/ and create a /docs/ directory.  In the /docs/ directory create a .nojekyll file in /docs/.  This file tells GitHub that this is not a Jekyll-based documentation project (e.g., don't ignore files and directories starting with '_').::

  # If you haven't made your documentation yet, create the directory and do the sphinx-quickstart process
  mkdir /docsrc
  ...

  mkdir /docs
  touch /docs/.nojekyll


For convenience, add this new github /docsrc/Makefile if it doesn't already exist.  This creates the documentation and then copies it to the /docs/ folder.::

  vi /docsrc/Makefile
  git:
      @make html
      cp -r build/html/. ../docs

Now make any changes to your documentation source, then build the documentation using the github target.  Commit and push the changes backup to the GitHub remote.::

  cd docsource
  vi ...
  make github
  cd ..

  # Optionally inspect the updates
  firefox --no-remote docs/index.html

  git add docs
  git commit -m"<some message>"
  git push

Now check that the changes appear as desired on the GitHub Pages - https://jeffersonlab.github.io/rf_classifier.  If you're satisfied, you're done!