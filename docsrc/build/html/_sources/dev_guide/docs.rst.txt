##############################
How To Generate Documentation
##############################

.. toctree::

=========================
Overview
=========================
This project uses Sphinx, restructured text (reST), google's doc string format conventions, and a "Read The Docs" theme.  The resulting HTML documentation can be built locally for use within the certified software repository and is also uploaded https://jeffersonlab.github.io/rf_classifier via the gh-pages git branch.  The admin guide discusses building the documentation locally, but this page explains the process of updating the documentation on github.io.

=========================
First steps
=========================

Here we make two local copies of the project.  One will contain the master branch for which we want to generate the documentation.  The other will contain the pared down gh-pages branch that contains only the HTML documentation.::

  cd /some/where/
  git clone https://github.com/JeffersonLab/rf_classifier rf_classifier
  git clone https://github.com/JeffersonLab/rf_classifier rf_classifier-docs

In the master branch directory, complete the software installation as described in the Admin Guide.  Shorthand procedure is as follows.::

  cd rf_classifier
  /usr/csite/pubtools/python/3.6/bin/python3 -m venv ./venv
  source venv/bin/activate.csh
  pip install -r requirements.txt
  tests/tester.bash

In the master branch directory, make the desired changes to the documentation, generate the HTML, and examine the output as needed.::

  cd docs
  make html
  firefox build/html/index.html

Commit and push back the final changes so the documentation sources are situated within the master branch on the remote server.::

  git commit
  git push

Switch gears to work with the gh-pages branch directory.  The first time this procedure was performed, we had to create an empty, orphaned branch (parallel branch not tied to the project/master branch).  Here is how that is accomplished.::

  cd /some/where/rf_classifier-docs
  git checkout --orphan gh-pages 

After creating the orphaned branch, add remote branch information so you can push to the remote server later.::

  vi .git/config
  ...
  [branch "gh-pages"]
      remote = origin
      merge = refs/heads/gh-pages

No matter what, you'll want to clear out the branch contents as they are either the old documentation or the full project.::

  # Do a dry run to ensure we aren't deleting something unexpected.
  # This should clear out the project files.
  git rm -rf --dry-run .
  git rm -rf .

Copy over the new documentation built in the master branch directory.::

  cp -r ../rf_classifier/docs/build/html/* .
  git add *

Create an empty .nojykell file to inform GitHub Pages that we aren't using their Jekyll format and all of our content should be treated as though it were part of a website.  Failing to include a .nojekyll will cause the _static directory containing CSS and JS files to be ignored by github.io.::

  touch .nojekyll

Commit the changes to gh-branch and push back to the origin (github.com).::

  git commit -m"I made some changes to the documentation!!"
  git push

Now check that the changes appear as desired on the GitHub Pages - https://jeffersonlab.github.io/rf_classifier.  If you're satisfied, you're done!
