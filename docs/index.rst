.. PySimlink documentation master file, created by
   sphinx-quickstart on Mon Jul 18 20:21:35 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PySimlink's documentation!
=====================================

**PySimlink** is a python package that compiles Simulink codegen files (with additional
mixins) into a simple interface that you can interact with in Python! The impetus to
create this project stems from the frustration with how difficult it is to model dynamical
systems in pure Python. While there are tools that make this task possible, why reinvent the
wheel when Simulink is so well suited for the task.

With this package, you can interact with the internals of your model, run the model in
"accelerator mode", send and recieve data in the form on numpy arrays, all without requiring
a MATLAB runtime! All you need is Simulink Coder, and the ability to export your model to
a grt target.

.. note::
   This package is still under development, and its interface may not be complete.

.. toctree::
   :maxdepth: 2

   src/autodoc
   src/license

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`license <License>`

