from pysimlink import Model, print_all_params
import argparse
import numpy as np
from multiprocessing import Process
import os
import time


def runner(args):
    model = Model(args.model_name, args.model_path, force_rebuild=True)
    model.reset()

    for i in range(len(model)):
        model.step()
        print(f"here i: {i:5d} pid: {os.getpid():5d}")
        time.sleep(2)


def main(args):
    # procs = []
    # for i in range(10):
    #     this_proc = Process(target=runner, args=(args,))
    #     procs.append(this_proc)

    # list(map(lambda f: f.start(), procs))
    # list(map(lambda f: f.join(), procs))
    tic = time.time()
    model = Model(args.model_name, args.model_path, force_rebuild=True)
    toc = time.time()
    print(f"compiling took {toc-tic:.2f}s")
    model.reset()
    # print_all_params(model)
    model.get_signal("Blazer_MiL_Model/Subsystem3/Bus Creator", model_name="Blazer_MiL_Model", )

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("model_name")
    parser.add_argument("model_path")
    args = parser.parse_args()
    main(args)
    # tmp(args)
    # runner(args)
