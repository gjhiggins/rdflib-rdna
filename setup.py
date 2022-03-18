#!/usr/bin/env python

import codecs
import os
import re

from setuptools import find_packages, setup

kwargs = {}
kwargs["install_requires"] = [
    "setuptools",
    "rdflib>=6.0",
    "importlib-metadata; python_version < '3.8.0'",
]
kwargs["tests_require"] = [
    "pytest",
    "pytest-cov",
    "pytest-subtests",
]
kwargs["extras_require"] = {
    "tests": kwargs["tests_require"],
    "docs": [
        "sphinx < 5",
        "sphinxcontrib-apidoc",
        "myst-parser",
        "sphinxcontrib-kroki",
    ],
}


def find_version(filename):
    _version_re = re.compile(r'__version__ = "(.*)"')
    for line in open(filename):
        version_match = _version_re.match(line)
        if version_match:
            return version_match.group(1)


def open_local(paths, mode="r", encoding="utf8"):
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), *paths)
    return codecs.open(path, mode, encoding)


with open_local(["README.md"], encoding="utf-8") as readme:
    long_description = readme.read()

version = find_version("rdflib_rdna/__init__.py")

packages = find_packages(exclude=("examples*", "test*"))

if os.environ.get("READTHEDOCS", None):
    # if building docs for RTD
    # install examples, to get docstrings
    packages.append("examples")

setup(
    name="rdflib-rdna",
    version=version,
    description="rdflib extension adding RDNA as a serializer",
    author="RDFLib team",
    maintainer="Graham Higgins",
    maintainer_email="gjhiggins@gmail.com",
    url="https://github.com/RDFLib/rdflib-rdna",
    license="bsd-3-clause",
    platforms=["any"],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=packages,
    entry_points={
        "rdf.plugins.serializer": [
            "rdna = rdflib_rdna.rdna:RDNASerializer",
        ],
    },
    **kwargs,
)
