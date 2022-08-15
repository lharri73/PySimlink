from pysimlink import Model, print_all_params
import argparse
import numpy as np
from tqdm import tqdm


def main(args):
    model = Model(args.model_name, args.model_path)#, force_rebuild=True)
    model.reset()
    print_all_params(model)
    param = model.get_block_param("sfcndemo_matadd/Matrix param1", "Operand")
    print(param)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_name")
    parser.add_argument("model_path")
    args = parser.parse_args()
    main(args)
