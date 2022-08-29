from dataclasses import dataclass
import unittest
import sys
import pickle
import time
import numpy as np

from pysimlink import Model, GenerationError, BuildError

@dataclass
class Args:
    model_path: str
    model_name: str
    data_file: str



    

if __name__ == "__main__":
    data_file = sys.argv.pop()
    model_name = sys.argv.pop()
    model_path = sys.argv.pop()
    # args = Args(model_path, model_name, data_file)
    unittest.main()
