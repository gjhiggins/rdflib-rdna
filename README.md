# A RDFLib plugin providing RDF Dataset Normalization

## **NOTE: This plugin will only work with RDFLib >= 7.0**

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![Validation: install and test](https://github.com/gjhiggins/rdflib-rdna/actions/workflows/validate.yaml/badge.svg)](https://github.com/gjhiggins/rdflib-rdna/actions/workflows/validate.yaml) [![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause) [![activity](https://img.shields.io/github/commit-activity/m/gjhiggins/rdflib-rdna)](https://github.com/gjhiggins/rdflib-rdna/pulse) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rdflib) [![semver](https://img.shields.io/badge/semver-1.0.0--alpha-blue)](https://semver.org/)

Contributed by Graham Higgins, translated from the [Digital Bazaar URDNA2015 Javascript](https://github.com/digitalbazaar/rdf-canonize) implementation.

This plugin provides an NQuads serializer (labelled as “rdna”) which implements an algorithm for generating a normalized RDF dataset given an RDF dataset as input.

BNode identifiers in the input Dataset are replaced by sequential, deterministic BNode identifiers using a `C14n` prefix, e.g.
```
_:c14n0 <http://xmlns.com/foaf/0.1/name> "Harry" _:c14n1 .
```

## Installation options

### Install with pip from github repos

```bash
pip install git+https://github.com/gjhiggins/rdflib-rdna#egg=rdflib_rdna`
```

### Install by cloning github repos, then pip install

```bash
git clone https://github.com/gjhiggins/rdflib-rdna.git
cd rdflib-rdna
pip install .
# Optionally
pip install -r requirements.dev.txt
./run_tests.py
```

### Example usage:

```python
from rdflib import Dataset

data = """_:b4 <http://purl.org/dc/terms/publisher> "Harry" .
_:b3 <http://xmlns.com/foaf/0.1/name> "Harry" _:b4 .
"""

expected = """_:c14n0 <http://xmlns.com/foaf/0.1/name> "Harry" _:c14n1 .
_:c14n1 <http://purl.org/dc/terms/publisher> "Harry" .
"""

def test_rdna():
    # Instantiate a Dataset
    ds = Dataset()

    # Parse the N-Quads as usual
    ds.parse(data=data, format="nquads")

    # Serialize as canonical
    canonicalized = ds.serialize(format="rdna")

    assert canonicalized == expected

    # Closedown
    ds.close()
```
