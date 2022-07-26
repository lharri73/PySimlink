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

    set_param(configs, 'SystemTargetFile', 'rsim.tlc');
    set_param(configs, 'GenerateMakefile', 'off');
    set_param(configs, 'GenCodeOnly', 'on');
    set_param(configs, 'RTWCAPIParams', 'on');
    set_param(configs, 'RTWCAPISignals', 'on');

    if mustProp
        Simulink.BlockDiagram.propagateConfigSet(model);
    end
    slbuild(model);
    buildFolder = RTW.getBuildDir(model).BuildDirectory;

    packNGo(buildFolder, 'packType', 'hierarchical', 'nestedZipFiles', false);

What's going on here? 

It's just changing a few settings in your model's config. These are the minimum
settings required for PySimlink, and should not affect your model's ability to
build (knock on wood)...

Here is what it's changing, in case you want to do it for yourself or are using
multiple config sets:

* Change the "System target file" under "Code Generation" to `rsim.tlc`
* On the same page, enable the `Generate code only` checkbox
* On the same page, disable the `Generate makefile` checkbox
* Under "Code Generation" -> "Interface", check the `signals` and `parameters`
  boxes
* If it's a configuration reference, propagate these changes
* Build the model (this generates the code)
* Pack all code required to compile the model into a handy little zip file
    * This step is packing code in the `...rsim_rtw` folder AND from your MATLAB
      install folder. It's just easier to run the `packNGo` command.

Step 2: Let PySimlink Handle The Rest
-------------------------------------
You 
