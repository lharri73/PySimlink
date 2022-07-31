Quickstart
==========
If you already have the generated model code, skip to step 2. If you get the joy
of generating the model source, well start from the top. 

Step 1: Generate the Model's Code.
----------------------------------
This is easily the hardest part of the whole process. But we've tried to make it
simple for you. You just need to check a few settings and build the model. If
you're feeling bold, you can copy-paste a script to do it for you! 

Here's said script::

    model = 'HevP4ReferenceApplication';        % <-- The name of your model...change this
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

Here is what it's changing, in case you want to do it for yourself or are using
multiple config sets:
* On the solver page, uncheck the `Treat each discrete rate as a separate task` box
* On the same page, uncheck the `Allow tasks to execute concurrently on the target` box
* Change the "System target file" under "Code Generation" to `grt.tlc`
* On the same page, enable the `Generate code only` checkbox
* On the same page, enable the `Package code and artifacts` checkbox
* On the same page, disable the `Generate makefile` checkbox
* Under "Code Generation" -> "Interface", check the `signals`, `parameters`, `states`, and `root-level I/O`
  boxes
* On the same page, under the "Advanced parameters" section, uncheck the `Classic call interface`
* On the same page, under the "Advanced parameters" section, check the `Single output/update function`
* If it's a configuration reference, propagate these changes
* Build the model (this generates the code)


Step 2: Let PySimlink Handle The Rest
-------------------------------------
