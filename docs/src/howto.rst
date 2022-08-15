How-To and Basic Usage Guide
============================

Install PySimlink
-----------------
PySimlink installs with pip, but requires compiler to build models. This compiler needs to be discoverable by the
cmake binary that's installed with pip.

While mingw is a valid compiler on Windows, it's much simpler to use the Visual Studio tools.

.. _compiler setup:

Setup
^^^^^

A couple of os-specific steps are required if you've never done any c/c++ development before. Don't worry though, this
doesn't mean you have to dig into the c++ code. We just need to be able to compile it.

+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Windows | Download `Visual Studio <https://github.com/MicrosoftDocs/cpp-docs/blob/main/docs/build/vscpp-step-0-installation.md>`_ (Only the "Desktop Development with C++" workload) [#f1]_ |
+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| OSX     | Install the `Command Line Tools for Xcode <https://developer.apple.com/download/all/>`_.                                                                                          |
+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Linux   | All you need is gcc, g++, ld, and make. How you get that is up to your distribution.                                                                                              |
+---------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. [#f1] You can also use WSL instead and install gcc & g++.

Install PySimlink with pip
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. code-block:: bash

    pip install pysimlink


Generate Code From Your Simulink Model
--------------------------------------
.. note:: To be able to generate code, you must have a license to
    the `Simulink Coder <https://www.mathworks.com/products/simulink-coder.html>`_.

PySimlink requires a set of model parameters be set before the code generation process.
This comes with a few limitations, the most important is that the model must run using a fixed-step solver.

.. _gen model params:

1. Update Model Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^
.. tip:: If you are using model references, try using `configuration references <https://www.mathworks.com/help/simulink/ug/referencing-configuration-sets.html?searchHighlight=configuration%20reference&s_tid=srchtitle_configuration%2520reference_1>`_
    so you don't have to change these settings in **each** model's configuration set.

PySimlink requires a few model settings to generate code in a format that it can interact with.

You can do this either using the script provided in the :ref:`Quickstart page <param set script>`
*or* manually by changing the parameters manually in the following steps.

First, open the model settings under the modelling tab.

.. figure:: /_static/imgs/model_settings.png
    :height: 85
    :align: center

    Model Settings located in the modelling Menu Bar.

Solver Settings
"""""""""""""""
On the :guilabel:`Solver` page, make sure you're using a :guilabel:`Fixed-step` solver. Also uncheck the
:guilabel:`Treat each discrete rate as a separate task` box. Finally, uncheck the :guilabel:`Allow tasks to execute concurrently on the target` box.

.. figure:: /_static/imgs/solver_settings.png
    :align: center
    :height: 500

    Solver settings

Code Generation Settings
""""""""""""""""""""""""

On the :guilabel:`Code Generation` page, use :file:`grt.tlc` as the System target file. Also check the :guilabel:`Generate code only` and
the :guilabel:`Package code and artifacts` boxes. This will generate a zip file with all of the code generated that you
can use with PySimlink. Since we're not building anything, uncheck the :guilabel:`Generate makefile` box.

.. figure:: /_static/imgs/codegen_settings.png
    :align: center
    :height: 500

    Code Generation Settings

Code Interface Settings
"""""""""""""""""""""""
On the :guilabel:`Code Generation -> Interface` page, check the :guilabel:`signals`, :guilabel:`parameters`, :guilabel:`states`,
and :guilabel:`root-level I/O` (even if you won't be interacting with some of them, PySimlink requires these functions to be defined).

Next, scroll down and click the :guilabel:`...` at the bottom of this page to reveal more Advanced parameters.

.. figure:: /_static/imgs/code_interface.png
    :align: center
    :height: 500

    Basic Code Generation Interface Settings

Under the :guilabel:`Advanced parameters` section, *uncheck* the :guilabel:`Classic call interface` box and check the
:guilabel:`Single output/update function` box.

.. figure:: /_static/imgs/code_interface_advanced.png
    :align: center
    :height: 500

    Advanced Code Generation Interface Settings

Done with model settings! If it's a model reference, you'll need to propagate these changes to each model.

2. Generate Code!
^^^^^^^^^^^^^^^^^
Now you can execute the code generation step. Open the Simulink Coder app and click the :guilabel:`Generate Code` button!

.. figure:: /_static/imgs/toolbar_1.png
    :height: 85
    :align: center

    Simulink Coder in the Simulink Apps Menu Bar.

.. figure:: /_static/imgs/gen_code.png
    :height: 85
    :align: center

    :guilabel:`Generate Code` button within Simulink Coder.

This will produce the :file:`my_awesome_model.zip` file that you can use with PySimlink. Unless you modified the
:guilabel:`Zip file name` parameter in the Code generation settings, this will also be the name of your root model.

Find the Name of Your Root Model Without Simulink
-------------------------------------------------
Let's say the file you've been given is called :file:`my_awesome_model.zip`. It's a good guess that the root model is
called "my_awesome_mode", but here's how you can double check without having to whip out Simulink.

Inside the archive, you'll find 2 folders (if you don't, then this was not generated by Simulink and PySimlink will
throw an error). One folder will contain :file:`extern`, :file:`rtw`, and :file:`simulink`. The other will contain two
folders: :file:`slprj` and :file:`[your_model_name]_grt_rtw`.

In short, it looks like this:

.. code-block::

    my_awesome_model.zip/
    ├─ [a]/
    │  ├─ extern/
    │  ├─ rtw/
    │  ├─ simulink/
    ├─ [b]/
    │  ├─ slprj/
    │  ├─ [your_model_name]_grt_rtw/

:file:`your_model_name` is the name of the root model.


Compile and Run a Model
-----------------------
You've been given a zip file with a generated model (or you've generated it yourself. Way to go!). Now you want to
run it in Python. It's as simple as importing PySimlink and calling :code:`print_all_params`

.. code-block:: python

    from pysimlink import Model, print_all_params

    model = Model("my_awesome_mode", "./my_awesome_model.zip")
    model.reset()
    print_all_params(model)


Once you've figured out what signals you need to read, you can call :code:`model.step()` to iterate over the model!

.. _change signals:

Change the Value of Signals
---------------------------
This feature is not directly supported by PySimlink. The reason why is kind of complex. In short, it would work for
the fixed-step discrete solver. But for a solver with minor timesteps, changing the value of a signal could cause a
singularity in an integrator, or might not even affect anything at all (if the signal is changed on the major time step
from PySimlink, then updated by the originating block at the next minor timestep (which PySimlink does not control),
then the change from PySimlink would have no affect).

How do we get around this? You'll have to tweak the model and generate it again... While this is not ideal, this keeps
us from violating solver during simulation.

Take this model, for example. And say you want to change the value of the highlighted signal during simulation.

.. figure:: /_static/imgs/signal_highlight.png
    :height: 290
    :align: center

    A garbage model with a signal whose value we want to change during simulation.

To be able to change the value, we need to terminate the signal and replace it with a constant. The resulting change
looks like this.

.. figure:: /_static/imgs/signal_highlight2.png
    :height: 290
    :align: center

    The same model adjusted so we can change the value of this signal during simulation.

Now, during simulation, we change the "Value" parameter of the block labeled "Constant". While this may not simulate
properly in Simulink, you can change this value at every timestep to get your desired behavior.

.. tip:: If you're making changes to your model like this just for code generation or for PySimlink and don't want to
    change its normal behavior, check out `Variant Subsystems <https://www.mathworks.com/help/simulink/ug/variant-subsystems.html>`_.
    You can have one subsystem for code generation and one for Simulink simulation.
