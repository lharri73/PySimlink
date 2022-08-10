class GenerationError(Exception):
    def __init__(self, *args):
        self.dump = args[0]
        self.cmake = args[1]

    def __str__(self):
        return 'Generating the CMakeLists for this model failed. This could be a c/c++/cmake setup issue, bad paths, or a bug! ' \
                f'Output from CMake generation is in {self.dump}'


class BuildError(Exception):
    def __init__(self, *args):
        self.dump = args[0]
        self.cmake = args[1]

    def __str(self):
        return 'Building the model failed. This could be a c/c++/cmake setup issue, bad paths, or a bug! ' \
                f'Output from the build process is in {self.dump}'
