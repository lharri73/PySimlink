<h1 align="center">
<img src="https://github.com/lharri73/PySimlink/blob/master/refs/banner.svg?raw=true">
</h1>

![PyPI](https://img.shields.io/pypi/v/pysimlink)

**PySimlink** is a python package that automatically compiles Simulink codegen files 
into a simple interface that you can interact with in Python!

With this package, you can:
- Interact with the internals of your Simulink model
- Run the model in "accelerator mode"
- Send and receive data in the form of numpy arrays
- Run multiple instances of the same model

All without requiring a MATLAB runtime on the target machine! No C/C++ programming required!

To get started, you either need a copy of the generated model you want to simulate or, to generate
the code yourself, you need the Simulink Coder. There are some limitations, namely that your model *must* use a fixed step solver 
(a requirement of the grt target). 

Check out the [docs](https://lharri73.github.io/PySimlink/) to get started! 
