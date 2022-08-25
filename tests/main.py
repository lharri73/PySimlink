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


class ModelTester(unittest.TestCase):
    def setUp(self) -> None:
        self.model_path = args.model_path
        self.model_name = args.model_name
        # with open(self.data_file, "rb") as f:
        #     self.data = pickle.load(args.data_file)


    def test_01_compile(self):
        try:
            self.model = Model(self.model_name, self.model_path)
        except (GenerationError, BuildError) as e:
            with open(e.dump, "r") as f:
                lines = f.read()
                print(lines)
            print("--------------------")
            print("Offending CMakeLists.txt: ")
            with open(e.cmake, "r") as f:
                lines = f.read()
                print(lines)
            raise e


    def test_02_force_compile(self):
        tic = time.time()
        self.model = Model(self.model_name, self.model_path, force_rebuild=True)
        self.assertGreater(time.time() - tic, 1.0)

    
    def test_03_no_compile(self):
        tic = time.time()
        self.model = Model(self.model_name, self.model_path)
        self.assertLess(time.time() - tic, 1.0)


    # def test_04_len(self):
    #     self.assertEqual(len(self.model), self.data['model_length'])


    @unittest.expectedFailure
    def test_05_step_no_reset(self):
        self.model = Model(self.model_name, self.model_path)
        self.model.step()


    def test_06_step(self):
        self.model = Model(self.model_name, self.model_path)
        self.model.reset()
        self.model.step()


    # def test_07_get_tfinal(self):
    #     self.model = Model(self.model_name, self.model_path)
    #     self.model.reset()
    #     self.assertEqual(self.model.tFinal, self.data['tfinal'])


    @unittest.expectedFailure
    def test_08_get_tfinal_no_reset(self):
        self.model = Model(self.model_name, self.model_path)
        self.model.tFinal

    
    def test_09_set_tfinal(self):
        self.model = Model(self.model_name, self.model_path)
        self.model.reset()
        old_tfinal = self.model.tFinal
        new_tfinal = old_tfinal
        while new_tfinal != old_tfinal:
            new_tfinal = np.random.randint(5, 100)
        self.model.set_tFinal(new_tfinal)
        self.assertEqual(self.model.tFinal, new_tfinal)


    @unittest.expectedFailure
    def test_10_set_neg_tfinal(self):
        self.model = Model(self.model_name, self.model_path)
        self.model.reset()
        self.model.set_tFinal(-1)

    
    # def test_11_get_step_size(self):
    #     self.model = Model(self.model_name, self.model_path)
    #     self.model.reset()
    #     self.assertEqual(self.model.setp_size, self.data['step_size'])

    
    @unittest.expectedFailure
    def test_12_get_step_size_no_reset(self):
        self.model = Model(self.model_name, self.model_path)
        self.model.step_size

    

if __name__ == "__main__":
    data_file = sys.argv.pop()
    model_name = sys.argv.pop()
    model_path = sys.argv.pop()
    args = Args(model_path, model_name, data_file)
    unittest.main()
