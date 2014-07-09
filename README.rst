======
README
======

This repository contains the source for a project involving data extraction and analysis from the Penn Arabic Treebank. The primary goal of the project is analysis and comparison of pro-drop and non-pro-drop subjects and their association with verbs. The ``parsetree`` module could be useful for any user desiring to build/traverse/search Penn Treebank data, however.

Repository author: Adam Beagle

*******************
Repository Contents
*******************

:docs/: Project-level documentation
:prodrop/: The Python package directory containing all core source
:scripts/: Various scripts not directly tied to the ``prodrop`` package
:treebank_data/: Treebank Data (as .parse files) are placed here to be used in the ``prodrop`` package. The repository contains only sample data.

*****
Usage
*****

See the docstrings at the top of ``prodrop/subjectverbanalysis.py`` and ``prodrop/parsetree.py``. An entry point of the project is located in ``prodrop/analyze_corpus.py``.

*****
Legal
*****

See ``docs/LICENSE.txt`` for license information.
