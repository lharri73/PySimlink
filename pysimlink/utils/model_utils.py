import os
from pysimlink.utils import annotation_utils as anno


def infer_defines(model_paths: "anno.ModelPaths"):
    """When defines.txt is not present, add the only required defines for pysimlink

    Args:
        model_paths: instance of ModelPaths object pointing to the root _model

    Returns:
        List of _model defines. These are added the CMakeLists.txt

    """
    ret = [f"MODEL={model_paths.root_model_name}"]
    return ret


def print_all_params(model: "anno.Model"):
    """
    Prints all parameters for the given model.

    Uses the ModelInfo object to print all model info about the root and each reference model
    Args:
        model: instance of the Model to print params of
    """
    params = model.get_params()
    for model_info in params:
        print(f"Parameters for _model at '{model_info.model_name}'")
        print("  _model parameters:")
        for param in model_info.model_params:
            print(f"    param: '{param.model_param}' | data_type: '{param.data_type}'")
        print("  block parameters:")
        for param in model_info.block_params:
            print(
                f"    Block: '{param.block_name}' | Parameters: '{param.block_param}' | data_type: '{param.data_type}'"
            )
        print("  signals:")
        for sig in model_info.signals:
            print(
                f"    Block: '{sig.block_name}' | Signal Name: '{sig.signal_name}' | data_type: '{sig.data_type}'"
            )
        print("-" * 80)


def get_other_in_dir(directory: str, known: str):
    """In a directory containing only two directories, get the name of the other we don't know

    Args:
        directory: path to the directory
        known: The file/folder known to exist in the directory

    Returns:
         the other directory/file in the directory
    """

    model_folders = set(os.listdir(directory))
    model_folders.discard(".DS_Store")
    assert (
        len(model_folders) == 2
    ), f"Directory '{directory}' contains more than 2 folders (not counting .DS_Store on Mac)"
    assert (
        known in model_folders
    ), f"File does not exist in {directory}. Should be one of {model_folders}"
    model_folders.remove(known)

    return model_folders.pop()
