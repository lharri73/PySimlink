Python + Simulink = PySimlink!
==============================
.. toctree::
   :maxdepth: 2
   :hidden:

   src/quickstart
   src/howto
   src/autodoc
   src/license

**PySimlink** is a python package that compiles Simulink codegen files (with additional
mixins) into a simple interface that you can interact with in Python! The impetus to
create this project stems from the frustration with how difficult it is to model dynamical
systems in pure Python. While there are tools that make this task possible, why reinvent the
wheel when Simulink is so well suited for the task.

**With this package, you can**:

* Read and set block parameters
* Read and set model parameters
* Read signal values
* Change the simulation stop time of your model
* Run a model in "accelerator mode"
* Run multiple instances of the same model

All without the MATLAB runtime!

**What PySimlink can't do:**

* Add or remove blocks to a model (the structure of the model is final once code is generated)
* Interact with models using variable step solvers
* Some signals and blocks are reduced/optimized during code generation. These are not accessible.

  * `virtual blocks <https://www.mathworks.com/help/simulink/ug/nonvirtual-and-virtual-blocks.html>`_
    are not compiled and cannot be accessed by PySimlink.
* Change the value of signals during simulation

  * Changing the value of a signal could cause a singularity in derivatives/integrals depending on the solver.
    This also would only affect the major time step and would be overwritten during the signal update of the next minor timestep.

    * See the :ref:`How-To guide <change signals>` for a workaround.


