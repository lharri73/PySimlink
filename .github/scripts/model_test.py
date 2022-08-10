import os
import argparse
import pickle
from pysimlink.lib.model import Model
from pysimlink.lib.exceptions import GenerationError, BuildError


def main(args):
    with open(os.path.join(args.dir, 'manifest.pkl'), 'rb') as f:
        models = pickle.load(f)

    for file, model in models:
        print(f"Checking {file}, {model}")
        if args.zip:
            path = os.path.join(args.dir, 'zips', file)
        else:
            path = os.path.join(args.dir, 'extract', file+'_e')
        try:
            cur_model = Model(model, path)
        except (GenerationError, BuildError) as e:
            print(e)
            with open(e.dump, 'r') as f:
                lines = f.read()
                print(lines)
            print('--------------------')
            print("Offending CMakeLists.txt: ")
            with open(e.cmake, 'r') as f:
                lines = f.read()
                print(lines)
            exit(1)
        cur_model.reset()
        for i in range(2):
            cur_model.step()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dir")
    parser.add_argument('--zip', default=False, action='store_true')
    args = parser.parse_args()
    main(args)
