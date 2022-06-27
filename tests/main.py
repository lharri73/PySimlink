from pysimlink.compile import Compiler
import argparse

def main(args):
    comp = Compiler(args.model_name, args.model_path)
    comp.compile()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('model_name')
    parser.add_argument('model_path')
    args = parser.parse_args()
    main(args)
