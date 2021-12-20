from setuptools import setup, find_packages

# read the contents of your README file
from os import path

this_directory = path.abspath(path.dirname(__file__))

with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


version = {}
with open("pynder/version.py") as fp:
    exec(fp.read(), version)

setup(
    name="pynder",  # How you named your package folder (MyLib)
    packages=find_packages(),
    python_requires="==3.8.10",
    version=version["__version__"],
    license="Apache 2.0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=["Programming Language :: Python :: 3.8"],
)
