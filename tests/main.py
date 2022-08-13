from pysimlink import Model, print_all_params
import argparse
import numpy as np
from tqdm import tqdm


def main(args):
    model = Model(args.model_name, args.model_path)#, force_rebuild=True)

    model.reset()
    print_all_params(model)
    b = model.get_block_param("custom_matrix/Constant", param="Value")
    print(b.shape)
    print(b.strides)
    b = np.ascontiguousarray(b)
    print(b)
    # something = np.array([[[1,2],[3,4]],[[5,6],[7,8]]], dtype=np.float64)
    # print(something)
    # model.set_block_param("sfcndemo_matadd/Constant1", param="Value", value=something)
    #
    # print("getting value")
    # b = model.get_block_param("sfcndemo_matadd/Constant1", param="Value")
    # print(b)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_name")
    parser.add_argument("model_path")
    args = parser.parse_args()
    main(args)
