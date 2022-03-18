import pytest
from rdflib import Dataset, logger

data = """<http://example.org/alice> <http://purl.org/dc/terms/publisher> "Alice" .
<http://example.org/bob> <http://purl.org/dc/terms/publisher> "Bob" .
_:b4 <http://purl.org/dc/terms/publisher> "Harry" .
_:b1 <http://xmlns.com/foaf/0.1/mbox> <mailto:bob@oldcorp.example.org> <http://example.org/bob> .
_:b1 <http://xmlns.com/foaf/0.1/knows> _:b0 <http://example.org/bob> .
_:b1 <http://xmlns.com/foaf/0.1/name> "Bob" <http://example.org/bob> .
_:b2 <http://xmlns.com/foaf/0.1/mbox> <mailto:alice@work.example.org> <http://example.org/alice> .
_:b2 <http://xmlns.com/foaf/0.1/name> "Alice" <http://example.org/alice> .
_:b3 <http://xmlns.com/foaf/0.1/mbox> <mailto:harry@work.example.org> _:b4 .
_:b3 <http://xmlns.com/foaf/0.1/name> "Harry" _:b4 .
_:b3 <http://xmlns.com/foaf/0.1/knows> _:b1 _:b4 .
"""

expected = """<http://example.org/alice> <http://purl.org/dc/terms/publisher> "Alice" .
<http://example.org/bob> <http://purl.org/dc/terms/publisher> "Bob" .
_:c14n0 <http://xmlns.com/foaf/0.1/knows> _:c14n2 <http://example.org/bob> .
_:c14n0 <http://xmlns.com/foaf/0.1/mbox> <mailto:bob@oldcorp.example.org> <http://example.org/bob> .
_:c14n0 <http://xmlns.com/foaf/0.1/name> "Bob" <http://example.org/bob> .
_:c14n1 <http://xmlns.com/foaf/0.1/mbox> <mailto:alice@work.example.org> <http://example.org/alice> .
_:c14n1 <http://xmlns.com/foaf/0.1/name> "Alice" <http://example.org/alice> .
_:c14n3 <http://xmlns.com/foaf/0.1/knows> _:c14n0 _:c14n4 .
_:c14n3 <http://xmlns.com/foaf/0.1/mbox> <mailto:harry@work.example.org> _:c14n4 .
_:c14n3 <http://xmlns.com/foaf/0.1/name> "Harry" _:c14n4 .
_:c14n4 <http://purl.org/dc/terms/publisher> "Harry" .
"""


def test_bnode_contexts():

    ds = Dataset()

    ds.parse(data=data, format="nquads")

    canonicalized = ds.serialize(format="rdna")

    assert canonicalized == expected

    ds.close()
