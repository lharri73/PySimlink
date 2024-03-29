import unittest
import sys
import pickle
import os
import time
import numpy as np
import shutil

from pysimlink import Model, GenerationError, BuildError


class ModelTester(unittest.TestCase):
    model_path = None
    model_name = None
    data_file = None
    data = None

    def test_01_compile(self):
        try:
            tic = time.time()
            model = Model(self.model_name, self.model_path)
            toc = time.time()
            cur_data = {"nominal": toc - tic}
            with open("data.pkl", "wb") as f:
                pickle.dump(cur_data, f)

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
        with open("data.pkl", "rb") as f:
            cur_data = pickle.load(f)
        time.sleep(1)
        tic = time.perf_counter()
        model = Model(self.model_name, self.model_path, force_rebuild=True)
        self.assertGreater(time.time() - tic, cur_data["nominal"] // 2)

    def test_03_no_compile(self):
        with open("data.pkl", "rb") as f:
            cur_data = pickle.load(f)
        tic = time.time()
        model = Model(self.model_name, self.model_path)
        self.assertLess(time.time() - tic, cur_data["nominal"] // 2)

    def test_04_len(self):
        model = Model(self.model_name, self.model_path)
        model.reset()
        self.assertEqual(len(model), self.data["model_length"])

    @unittest.expectedFailure
    def test_05_step_no_reset(self):
        model = Model(self.model_name, self.model_path)
        model.step()

    def test_06_step(self):
        model = Model(self.model_name, self.model_path)
        model.reset()
        model.step()

    def test_07_get_tfinal(self):
        model = Model(self.model_name, self.model_path)
        model.reset()
        self.assertEqual(model.tFinal, self.data["tFinal"])

    @unittest.expectedFailure
    def test_08_get_tfinal_no_reset(self):
        model = Model(self.model_name, self.model_path)
        model.tFinal

    def test_09_set_tfinal(self):
        model = Model(self.model_name, self.model_path)
        model.reset()
        old_tfinal = model.tFinal
        new_tfinal = old_tfinal
        while new_tfinal != old_tfinal:
            new_tfinal = np.random.randint(5, 100)
        model.set_tFinal(new_tfinal)
        self.assertEqual(model.tFinal, new_tfinal)

    @unittest.expectedFailure
    def test_10_set_neg_tfinal(self):
        model = Model(self.model_name, self.model_path)
        model.reset()
        model.set_tFinal(-1)

    def test_11_get_step_size(self):
        model = Model(self.model_name, self.model_path)
        model.reset()
        self.assertEqual(model.step_size, self.data["step_size"])

    @unittest.expectedFailure
    def test_12_get_step_size_no_reset(self):
        model = Model(self.model_name, self.model_path)
        model.step_size

    def test_99_cleanup(self):
        model = Model(self.model_name, self.model_path)
        if model is not None:
            # print("removing directories", model._model_paths.tmp_dir, model._model_paths.root_dir)
            shutil.rmtree(model._model_paths.tmp_dir, ignore_errors=True)
            shutil.rmtree(model._model_paths.root_dir, ignore_errors=True)


def make_test_cls(model_name, data_file, zip_file):
    with open(data_file, "rb") as f:
        data = pickle.load(f)
    tester = type(
        "ModelTester" + model_name,
        (ModelTester,),
        {"model_path": zip_file, "model_name": model_name, "data_file": data_file, "data": data},
    )
    return tester


def main(pth):
    with open(os.path.join(pth, "manifest.pkl"), "rb") as f:
        data = pickle.load(f)

    test_suite = unittest.TestSuite()
    for model_name, data_file, zip_file in data:
        tstCls = make_test_cls(model_name, data_file, zip_file)

        cur_cls = unittest.makeSuite(tstCls)
        test_suite.addTest(cur_cls)

    runner = unittest.TextTestRunner(failfast=True)
    ret = runner.run(test_suite)
    if ret.wasSuccessful():
        exit(0)
    exit(1)


if __name__ == "__main__":
    pth = sys.argv[-1]
    os.environ["PYSIMLINK_DEBUG"] = "TRUE"
    main(pth)
