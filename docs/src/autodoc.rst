.. _autodoc:

API
===

Model
-----
 
.. autoclass:: pysimlink.Model
  :members:
  :undoc-members:


Utility Functions
-----------------

.. autofunction:: pysimlink.print_all_params


Errors
------
These are the error's that are raised when the model fails to build.
Unlike a regular exception, they have two additional properties.

.. autoclass:: pysimlink.BuildError

.. autoclass:: pysimlink.GenerationError
