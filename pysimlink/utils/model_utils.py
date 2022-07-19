import os
import re
from pysimlink.lib.model_paths import ModelPaths


def infer_defines(model_paths: ModelPaths):
    replacement_defines = os.path.join(model_paths.tmp_dir, "defines_override.txt")
    if not os.path.exists(replacement_defines):
        raise ValueError("Unable to determine model macro definitions. ")
    ret = [f"MODEL={model_paths.root_model_name}"]
    with open(
        os.path.join(model_paths.root_model_path, f"{model_paths.root_model_name}.h"),
        "r",
        encoding="utf-8",
    ) as f:
        contents = f.readlines()

    regex = re.compile(r"uint\d+_T TID\[(\d+)]")
    for line in contents:
        match = re.search(regex, line)
        if match:
            numst = match.group(1)
            break
    else:
        raise RuntimeError(
            f"Unable to infer number of states from simulink mode. Can't find TID in {model_paths.root_model_name}.h"
        )
    ret.append(f"NUMST={numst}")
    ret.append("ONESTEPFCN=1")
    ret.append("TERMFCN=1")
    return ret


def print_all_params(model):
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
