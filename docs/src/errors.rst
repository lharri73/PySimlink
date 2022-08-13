Model Errors
======

Sometimes the build process doesn't go as smoothly. These are some errors you might come across, and how you can fix them.

Code generated with different sized ulong/long
----------------------------------------------
Different sized ulong/long::

    #error Code was generated for compiler with different sized ulong/long.
    Consider adjusting Test hardware word size settings on the Hardware
    Implementation pane to match your compiler word sizes as defined in limits.h
    of the compiler. Alternatively, you can select the Test hardware is the same
    as production hardware option and select the Enable portable word sizes option
    on the Code Generation > Verification pane for ERT based targets, which will
    disable the preprocessor word size checks.

Make sure that the "Test hardware is the same as production hardware" option is
checked in the model configuration. "Hardware Implementation" -> "Advanced Parameters"
