from pysimlink.lib.model import Model
from pysimlink.utils.model_utils import print_all_params
import argparse

def main(args):
    model = Model(args.model_name, args.model_path, force_rebuild=True)

    model.reset()
    print_all_params(model)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('model_name')
    parser.add_argument('model_path')
    args = parser.parse_args()
    main(args)
