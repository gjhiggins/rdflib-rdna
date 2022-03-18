import os
import pytest
from rdflib import Dataset, logger

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


def test_rdna_rdflib_bnodes():
    # Instantiate a Dataset
    ds1 = Dataset()
    ds2 = Dataset()

    # Parse the N-Quads as usual
    ds1.parse(data=data, format="nquads")

    ds2.parse(data=ds1.serialize(format="nquads"), format="nquads")

    # Serialize as canonical
    canonicalized = ds2.serialize(format="rdna")

    assert canonicalized == expected


def test_rdna_timblcard():
    # Instantiate a Dataset

    with open(os.path.join(os.getcwd(), "test", "timbl-card.trig"), 'r') as fp:
        timbltrig = fp.read()

    with open(os.path.join(os.getcwd(), "test", "timbl-card-canonicalized.nquads"), 'r') as fp:
        expected = fp.read()
        fp.close()

    ds = Dataset()

    ds.parse(data=timbltrig, format="trig")
    canonicalized = ds.serialize(format="rdna")
    assert canonicalized == expected
