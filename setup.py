from setuptools import setup, find_packages
import os

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

setup(
    name="pysimlink",
    version="0.0.1",
    author="Landon Harris",
    author_email="lharri73@vols.utk.edu",
    description="Interface with Simulink models using Python",
    packages=find_packages(),
    install_requires=requirements,
    extras_require={"dev": ["pylint", "black", "sphinx_rtd_theme", "sphinx", "tqdm", "sphinx_toolbox"]},
    include_package_data=True,
    package_data={"pysimlink": ["c_files/include/*.hpp", "c_files/src/*.cpp"]},
    python_requires=">=3.6",
)
