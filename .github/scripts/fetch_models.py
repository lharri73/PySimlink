import argparse
import os
from urllib import request
import zipfile
import pickle

def extract_zip(file, dest):
    with zipfile.ZipFile(file, "r") as f:
        f.extractall(dest)
        file_list = f.namelist()
    return file_list

def get_model_name(file_path):
    with zipfile.ZipFile(os.path.join(file_path), "r") as zip_file:
        file_list = zip_file.namelist()
        for fle in file_list:
            if "_data.c" in fle:
                base = os.path.basename(fle)
                model_name = base.split("_data.c")[0]
                return model_name
        else:
            raise Exception(f"Could not find name of root model for {file_path}")


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
        file_list = extract_zip(os.path.join(args.dir, "zips", file), os.path.join(args.dir, "extract", file + "_e"))
        
        data_file = None
        zip_file = None
        for fle in file_list:
            if fle.split('.')[-1] == 'pkl':
                data_file = fle
            elif fle.split('.')[-1] == 'zip':
                zip_file = fle
        if zip_file is None or data_file is None:
            raise Exception("invalid zip file format. Should contain data file and model zip")
        model_name = get_model_name(os.path.join(args.dir, "extract", file + "_e", zip_file))
        
        models.append([
            model_name,
            os.path.join(args.dir, "extract", file + "_e", data_file),
            os.path.join(args.dir, "extract", file + "_e", zip_file)
        ])

    with open(os.path.join(args.dir, "manifest.pkl"), "wb") as f:
        pickle.dump(models, f)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dir")
    args = parser.parse_args()
    main(args)
