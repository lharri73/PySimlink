from setuptools import setup, find_packages

with open("requirements.txt", "r") as f:
    reqs = f.read().splitlines()

with open("README.md", "r") as f:
    readme = f.read()

setup(
    name="pysimlink",
    version="1.2.1-dev2",
    author="Landon Harris",
    author_email="lharri73@vols.utk.edu",
    description="Compile, run, and interact with Simulink models natively in Python!",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=reqs,
    extras_require={
        "dev": [
            "pylint",
            "black",
            "sphinx_rtd_theme",
            "sphinx",
            "tqdm",
            "sphinx-toolbox",
            "sphinx-hoverxref",
            "readthedocs-sphinx-search",
        ]
    },
    include_package_data=True,
    python_requires=">=3.6",
    keywords=["Simulink"],
    license="GPLv3",
    classifiers=[
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Code Generators",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
    ],
    url="https://github.com/lharri73/PySimlink",
    project_urls={
        "Documentation": "https://lharri73.github.io/PySimlink/",
        "Source": "https://github.com/lharri73/PySimlink",
    },
)
