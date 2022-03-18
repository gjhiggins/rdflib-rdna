from collections import OrderedDict

import pytest
from rdflib.term import BNode

from rdflib_rdna import rdna


@pytest.fixture
def get_issuer():
    issuer = rdna.IdentifierIssuer()
    yield issuer
    del issuer


def test_rdna_identifierissuer_init(get_issuer):
    issuer = get_issuer
    assert isinstance(issuer._existing, OrderedDict)
    assert len(list(issuer._existing.keys())) == 0
    assert issuer.get_id() is not None

def test_rdna_identifierissuer_issue(get_issuer):
    issuer = get_issuer
    bnode1 = BNode()
    id1 = issuer.get_id(bnode1)
    assert issuer.get_id(bnode1) == id1
    assert id1 == '_:c14n0'
    assert issuer.has_id(bnode1) is True
    assert len(list(issuer._existing.keys())) == 1


def test_rdna_identifierissuer_clone(get_issuer):
    issuer = get_issuer
    bnode1 = BNode()
    id1 = issuer.get_id(bnode1)
    assert len(list(issuer._existing.keys())) == 1

    issuerclone = issuer.clone()
    assert len(list(issuerclone._existing.keys())) == 1

    assert issuerclone.get_id(bnode1) == id1


def test_rdna_identifierissuer_old_ids(get_issuer):
    issuer = get_issuer
    bnode1 = BNode()
    bnode2 = BNode()
    id1 = issuer.get_id(bnode1)
    id2 = issuer.get_id(bnode2)
    assert list(issuer.get_old_ids()) == [bnode1, bnode2]
