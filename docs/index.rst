.. Head Circumference Tool documentation master file, created by
   sphinx-quickstart on Thu Mar 16 00:34:47 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Head Circumference Tool's documentation!
===================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


How to generate documentation from scratch locally
==================================================

Follow this video https://www.youtube.com/watch?v=BWIrhgCAae0.

He uses src/docs/, but readthedocs.io requires that our documentation be in docs/.

pip install sphinx

pip install sphinx-rtd-theme

mkdir docs

cd docs

sphinx-quickstart (type n for the first question which asks about splitting source and build)

Make sure src/__init__.py exists.

sphinx-apidoc -o . ../src

Put the word modules in index.rst under toctree

At the top of conf.py, add the lines

import os

import sys

sys.path.insert(0, os.path.abspath(".."))

In the middle, extensions = ['sphinx.ext.todo', 'sphinx.ext.viewcode', 'sphinx.ext.autodoc']

Modify html_theme if you want.

make html
