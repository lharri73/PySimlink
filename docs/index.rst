.. PySimlink documentation master file, created by
   sphinx-quickstart on Mon Jul 18 20:21:35 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PySimlink's documentation!
=====================================
.. toctree::
   :maxdepth: 2
   :hidden:

   src/autodoc
   src/license

.. note::
   This package is still under development, and its interface may not be complete.

**PySimlink** is a python package that compiles Simulink codegen files (with additional
mixins) into a simple interface that you can interact with in Python! The impetus to
create this project stems from the frustration with how difficult it is to model dynamical
systems in pure Python. While there are tools that make this task possible, why reinvent the
wheel when Simulink is so well suited for the task.

With this package, you can change block and model parameters, read signal values,
run the model in "accelerator mode", and even run multiple instances of the same
model at once all without requiring a MATLAB runtime! All you need is Simulink Coder, and the ability to export your model to
a grt target.

Getting Started
================
There are three main steps to perform before you are able to run and interact
with your model.

#. Code Generation
#. Compile and Link
#. Import and Inspect

Code Generation
---------------
You must use the `grt.tlc` target in simulink coder, and your model **must build and run**
in simulink. This package is only tested with c targets. You must also enable the c_api
to allow PySimlink to interact with the model.

Compile and Link
----------------
This step is done for you, automatically. Although, you may be required to provide some
additional information during the first run. 

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`license <License>`

