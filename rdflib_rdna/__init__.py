# -*- coding: utf-8 -*-
"""
"""
__all__ = [
    "__title__",
    "__summary__",
    "__uri__",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__",
]


__title__ = "rdflib-rdna"

__summary__ = (
    "An adaptation of RDFLib BerkeleyDB Store’s key-value approach,"
    "using SQlite's LSM as a back-end. Implemented by Graham Higgins, "
    "based on an original contribution by Drew Perttula. "
)

__uri__ = "https://github.com/RDFLib/rdflib-rdna"

__version__ = "1.0.0-alpha"

__author__ = "Graham Higgins"
__email__ = "gjhiggins@gmail.com"

__license__ = "BSD 3-clause"
__copyright__ = "Copyright 2021 {}".format(__author__)

from rdflib import plugin

from rdflib import store

plugin.register(
    "SQLiteLSM",
    store.Store,
    "rdflib_rdna.rdnastore",
    "SQLiteLSMStore",
)
