import argparse
import os
from urllib import request
import zipfile
import pickle


def main(args):
    url = "https://github.com/lharri73/PySimlink-ci-models/raw/master/generated/"
    with request.urlopen(url + "manifest.txt") as f:
        files = f.readlines()
    with open(os.path.join(args.dir, "manifest.txt"), "wb") as f:
        f.writelines(files)
    files = list(map(lambda a: a.decode("utf-8").strip(), files))

    os.makedirs(os.path.join(args.dir, "zips"))
    for file in files:
        print(f"Fetching {file}")
        with request.urlopen(url + file) as f:
            zip_file = f.read()
        with open(os.path.join(args.dir, "zips", file), "wb") as f:
            f.write(zip_file)

    os.makedirs(os.path.join(args.dir, "extract"))
    models = []
    for file in files:
        print(f"Extracting {file}")
        with zipfile.ZipFile(os.path.join(args.dir, "zips", file), "r") as zip_file:
            zip_file.extractall(os.path.join(args.dir, "extract", file + "_e"))
            file_list = zip_file.namelist()
        for fle in file_list:
            if "_data.c" in fle:
                base = os.path.basename(fle)
                model_name = base.split("_data.c")[0]
                models.append(model_name)
                break
        else:
            raise Exception(f"Could not find name of root model for {file}")

    with open(os.path.join(args.dir, "manifest.pkl"), "wb") as f:
        pickle.dump(list(zip(files, models)), f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dir")
    args = parser.parse_args()
    main(args)
