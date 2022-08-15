class GenerationError(Exception):
    """
    Exception raised when generating build files fails.

    Attributes:
        dump (str): stdout and stderr output of the **generation** process
        cmake (str): contents of the :file:`CMakeLists.txt` file
    """

    def __init__(self, *args):
        self.dump = args[0]
        self.cmake = args[1]

    def __str__(self):
        return 'Generating the CMakeLists for this model failed. This could be a c/c++/cmake setup issue, bad paths, or a bug! ' \
                f'Output from CMake generation is in {self.dump}'


class BuildError(Exception):
    """
    Exception raised when generating build files succeeded but compiling the model fails.

    Attributes:
        dump (str): stdout and stderr output of the **build** process
        cmake (str): contents of the :file:`CMakeLists.txt` file
    """

    def __init__(self, *args):
        self.dump = args[0]
        self.cmake = args[1]

    def __str(self):
        return 'Building the model failed. This could be a c/c++/cmake setup issue, bad paths, or a bug! ' \
                f'Output from the build process is in {self.dump}'
