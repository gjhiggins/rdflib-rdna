"""This runs the nquads tests for the W3C RDF Working Group's N-Quads
test suite."""
import shutil
import tempfile
from test.manifest import RDFN, RDFTest, read_manifest
from typing import Callable, Dict

import pytest
from rdflib import RDF, RDFS, Dataset, Graph, logger
from rdflib.term import BNode, Node, URIRef

from rdflib_rdna import rdna


def canonicalize(test):

    with open(test.action[7:], 'r') as fp:
        data = fp.read()

    with open(test.result[7:], 'r') as fp:
        result = fp.read()

    ds1 = Dataset()

    ds1.parse(data=data, format="nquads")

    canonicalized_dataset = ds1.serialize(format="rdna")

    assert canonicalized_dataset == result

    ds1.close()


testers: Dict[Node, Callable[[RDFTest], None]] = {
    RDFN.RdnaEvalTest: canonicalize,
}


@pytest.mark.parametrize(
    "rdf_test_uri, type, rdf_test",
    read_manifest("test/dataset-canonicalization/manifest-rdna.ttl"),
)
def test_rdna_manifest(rdf_test_uri: URIRef, type: Node, rdf_test: RDFTest):
    testers[type](rdf_test)
