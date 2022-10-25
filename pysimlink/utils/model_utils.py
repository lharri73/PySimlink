import os
import pickle
import time
from pysimlink.utils import annotation_utils as anno
from pysimlink.lib.model_types import DataType


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
        print(f"Parameters for model at '{model_info.model_name}'")
        print("  model parameters:")
        for param in model_info.model_params:
            print(f"    param: '{param.model_param}' | data_type: '{DataType(param.data_type)}'")
        print("  block parameters:")
        for param in model_info.block_params:
            print(
                f"    Block: '{param.block_name}' | Parameter: '{param.block_param}' | data_type: '{DataType(param.data_type)}'"
            )
        print("  signals:")
        for sig in model_info.signals:
            print(
                f"    Block: '{sig.block_name}' | Signal Name: '{sig.signal_name}' | data_type: '{DataType(sig.data_type)}'"
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


def with_read_lock(func: callable) -> callable:
    """Use as decorator (@with_lock) around object methods that need locking.

    Note: The object must have a self._lock property.
    Locking thus works on the object level (no two locked methods of the same
    object can be called asynchronously).

    Inspired by `Rllib <https://github.com/ray-project/ray/blob/4963dfaae0fbdbae4a5ad6188bc86986f1a9568a/rllib/utils/threading.py#L7>`_

    Args:
        func: The function to decorate/wrap.
    Returns:
        The wrapped (object-level locked) function.
    """

    def wrapper(self, *a, **k):
        try:
            with self._lock.read_lock():
                return func(self, *a, **k)
        except AttributeError as e:
            if "has no attribute '_lock'" in e.args[0]:
                raise AttributeError(
                    "Object {} must have a `self._lock` property (assigned "
                    "to a fasteners.InterProcessReaderWriterLock object in its "
                    "constructor)!".format(self)
                )
            raise e

    return wrapper


def mt_rebuild_check(model_paths: "anno.ModelPaths", force_rebuild: bool) -> bool:
    """
    Prevent the model from being rebuilt in every multithreading instance

    Args:
        model_paths (anno.ModelPaths): instance of the model paths object. Used to get the tmp_dir
        force_rebuild (bool): flag set by the user that forces the model to rebuild

    Returns:
         True if the model should rebuild because of the force_rebuild flag and has not already
    """
    if not force_rebuild:
        return False

    compile_info = os.path.join(model_paths.tmp_dir, "compile_info.pkl")
    if not os.path.exists(compile_info):
        return True

    with open(compile_info, "rb") as f:
        info = pickle.load(f)

    if info["parent"] == os.getppid():
        tdiff = time.time() - info["time"]

        # assume that it takes at least 1 second to start a separate instance of a program
        # If it takes less than 1 second, then we assume it is run within the same python
        # instance
        return tdiff > 1.0
    else:
        return True


def sanitize_model_name(model_name):
    return model_name.replace(" ", "").replace("-", "_").lower()
