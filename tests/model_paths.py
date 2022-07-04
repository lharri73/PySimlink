from pysimlink.utils.model_utils import ModelPaths
import argparse

def main(args):
    mp = ModelPaths(args.model_path, args.model_name, 'grt', 'rtw')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('model_name')
    parser.add_argument('model_path')
    args = parser.parse_args()
    main(args)
