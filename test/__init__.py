from rdflib import plugin

from rdflib import serializer

plugin.register(
    "rdna",
    serializer.Serializer,
    "rdflib_rdna.rdna",
    "RDNASerializer",
)
