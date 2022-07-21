import os
import re
from pysimlink.lib.model_paths import ModelPaths


def infer_defines(model_paths: ModelPaths):
    ret = [f"MODEL={model_paths.root_model_name}"]
    return ret


def print_all_params(model):
    """

    :param model:
    :return:
    """
    params = model.get_params()
    for model_info in params:
        print(f"Parameters for model at '{model_info.model_name}'")
        print("  model parameters:")
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
