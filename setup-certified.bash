#!/bin/bash

SCRIPT_NAME=$(basename $0)
export PATH="/usr/csite/pubtools/python/3.6.9/bin:${PATH}"

if [[ ! -f "./setup-certified.bash" ]] ; then
    echo "This script must be executed from the directory that contains it"
    exit 1;
fi

usage () {
    echo "
Usage:
  $0 [build|test|install|compact]
  build
    Create documentation, setup venv, and install deps
  test
    Run tests
  install
    Remove all files that are not needed for execution
  compact
    Remove everything that cannot be regenerated by "build"

  NOTE: This script assumes it is being executed in it's directory.
"
}

build () {
    echo "building - building docs"
    cd docsrc
    make github
    cd -
}

test () {
    echo "testing - running unit tests"
    cd tests
    tester.bash
    cd -
}

# This is weird to my sensibilities, but we install by removing unnecessary components the git repo
install () {
    echo "installing - removing the docsrc/, docs/, .git/, tests/ directories and other unneeded files."
    rm -rf .git/
    rm -rf ./docs/
    rm -rf ./docsrc/
    rm -rf tests/
    rm requirements.txt
    rm requirements-certified
    rm README.md
}

compact () {
    echo "compacting - removing the docs directory contents and .git directory"
    if [ -d .git ] ; then
        rm -rf .git
    fi
    if [ -d ./docs ] ; then
        rm -rf ./docs/*
    fi
}

if [ $# -ne 1 ] ; then
    usage
    exit 1
fi

if [ ! -f "./$SCRIPT_NAME" ] ; then
    echo "Error: this script must be executed from within the base directory of the application."
    exit
fi

case $1 in
    "build") build; exit 0 ;;
     "test") test; exit 0;;
  "install") install; exit 0;;
  "compact") compact; exit 0;;
          *) echo "Unknown command: $1"; usage; exit 1;;
esac
