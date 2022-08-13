Quickstart
==========
If you already have the generated model code, skip to step 2. If you get the joy
of generating the model source, well start from the top. 

Step 1: Generate the Model's Code.
----------------------------------
This is likely the hardest part of the whole process. But we've tried to make it
simple for you. You just need to check a few settings and build the model. If
you're feeling bold, you can copy-paste a script to do it for you! 

Here's said script:

.. code-block:: matlab

    model = 'MyAwesomeModel';        % <-- The name of your model...change this!
    configs = getActiveConfigSet(model);
    mustProp=false;
    if isa(configs, 'Simulink.ConfigSetRef')
        configs = eval(configs.SourceName);
        mustProp=true;
    end

    set_param(configs, 'ConcurrentTasks', 'off');
    set_param(configs, 'EnableMultiTasking', 'off');
    set_param(configs, 'SystemTargetFile', 'grt.tlc');
    set_param(configs, 'GenerateMakefile', 'off');
    set_param(configs, 'GenCodeOnly', 'on');
    set_param(configs, 'PackageGeneratedCodeAndArtifacts', 'on');
    set_param(configs, 'RTWCAPIParams', 'on');
    set_param(configs, 'RTWCAPISignals', 'on');
    set_param(configs, 'RTWCAPIRootIO', 'on');
    set_param(configs, 'RTWCAPIStates', 'on');
    set_param(configs, 'GRTInterface', 'off');
    set_param(configs, 'CombineOutputUpdateFcns', 'on');

    if mustProp
        Simulink.BlockDiagram.propagateConfigSet(model);
    end
    slbuild(model);

What's going on here?

It's just changing a few settings in your model's config. These are the minimum
settings required for PySimlink, and should not affect your model's ability to
build (knock on wood)...

.. collapse:: Here is what it's changing, in case you want to do it for yourself or are using
    multiple config sets

    * On the :guilabel:`solver` page, uncheck the :guilabel:`Treat each discrete rate as a separate task` box
    * On the same page, uncheck the :guilabel:`Allow tasks to execute concurrently on the target` box
    * Change the :menuselection:`Code Generation --> System target file` to :guilabel:`grt.tlc`
    * On the same page, enable the :guilabel:`Generate code only` checkbox
    * On the same page, enable the :guilabel:`Package code and artifacts` checkbox
    * On the same page, disable the :guilabel:`Generate makefile` checkbox
    * Under :menuselection:`Code Generation --> Interface`, check the :guilabel:`signals`, :guilabel:`parameters`, :guilabel:`states`, and :guilabel:`root-level I/O`
      boxes
    * On the same page, under the :guilabel:`Advanced parameters` section, uncheck the :guilabel:`Classic call interface`
    * On the same page, under the :guilabel:`Advanced parameters` section, check the :guilabel:`Single output/update function`
    * If it's a configuration reference, propagate these changes
    * Build the model (this generates the code)


Step 2: Let PySimlink Handle The Rest
-------------------------------------
At this point, you should have a copy of the model in the form of generated code.
