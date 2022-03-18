# RDF Dataset Canonicalization

RDF describes a graph-based data model for making claims about the world and
provides the foundation for reasoning upon that graph of information. At
times, it becomes necessary to compare the differences between sets of
graphs, digitally sign them, or generate short identifiers for graphs via
hashing algorithms. This document outlines an algorithm for normalizing RDF
datasets such that these operations can be performed.

## A Standard RDF Dataset Canonicalization Algorithm

### Abstract

RDF  describes a graph-based data model for making claims
about the world and provides the foundation for reasoning upon that graph
of information. At times, it becomes necessary to compare the differences
between sets of graphs, digitally sign them, or generate short identifiers
for graphs via hashing algorithms. This document outlines an algorithm for
normalizing RDF datasets such that these operations can be
performed.

1. Introduction
When data scientists discuss canonicalization, they do so in the context of
achieving a particular set of goals. Since the same information may
sometimes be expressed in a variety of different ways, it often becomes
necessary to be able to transform each of these different ways into a
single, standard format. With a standard format, the differences between
two different sets of data can be easily determined, a
cryptographically-strong hash identifier can be generated for a particular
set of data, and a particular set of data may be digitally-signed for later
verification.
 
In particular, this specification is about normalizing RDF datasets, which are
collections of graphs. Since a directed graph can express the same
information in more than one way, it requires canonicalization to achieve the
aforementioned goals and any others that may arise via serendipity.
 
 Most RDF datasets can be normalized fairly quickly, in terms
 of algorithmic time complexity. However, those that contain nodes that do
 not have globally unique identifiers pose a greater challenge. Normalizing
 these datasets presents the graph isomorphism problem, a
 problem that is believed to be difficult to solve quickly. More formally,
 it is believed to be an NP-Intermediate problem, that is, neither known to
 be solvable in polynomial time nor NP-complete. Fortunately, existing real
 world data is rarely modeled in a way that manifests this problem and new
 data can be modeled to avoid it. In fact, software systems can detect a
 problematic dataset and may choose to assume it's an attempted denial of
 service attack, rather than a real input, and abort.

This document outlines an algorithm for generating a normalized RDF dataset
given an RDF dataset as input. The algorithm is called the
**RDF Dataset Canonicalization Algorithm** or **RDNA**.
 

Issue 2

### 1.1 Uses of Dataset Canonicalization
There are different use cases where graph or dataset canonicalization are important:

- Determining if one serialization is isomorphic to another.
- Digital signing of graphs (datasets) independent of serialization or format.
- Comparing two graphs (datasets) to find differences.
- Communicating change sets when remotely updating an RDF source.

A canonicalization algorithm is necessary but not necessarily sufficient to
handle many of these use cases. The use of blank nodes in RDF graphs and
datasets has a long history and creates inevitable complexities. Blank nodes
are used for different purposes:

- when a well known identifier for a node is not known, or the author of a
  document chooses not to unambiguously name that node,
- when a node is used to stitch together parts of a graph and the nodes
  themselves are not interesting (e.g. RDF Collections in RDF-MT,
- when someone is trying to create an intentionally difficult graph topology.

Furthermore, RDF semantics dictate that deserializing the same RDF document
results in the creation of unique blank nodes unless it can be determined
that on each occasion the blank node identifiers reference the same resource;
this is due to the fact that blank node identifiers are an aspect of a
concrete RDF syntax and are not intended to be persistent or portable.

Within the abstract RDF model, blank nodes do not have identifiers (although
some RDF store implementations may use stable identifiers and choose to make
them portable).

RDF does have a provision for allowing blank nodes to be published in an
externally-identifiable way through the use of Skolem IRIs, which allows
a given RDF store to replace the use of blank nodes in a concrete syntax
with IRIs that serve to repeatably identify that blank node within that
particular RDF store, however, this is not generally useful for talking
about the same graph in different RDF stores, or other concrete representations.
In any case, for a stable blank node identifier defined for one RDF store,
serialization is arbitrary and typically not relatable to the context within
which it is used.

This specification defines an algorithm for creating stable blank node
identifiers repeatably for different serializations possibly using individualized
blank node identifiers of the same RDF graph (dataset) by grounding each blank node
through the nodes to which it is connected, essentially creating *Skolem blank node identifiers*.

As a result, a graph signature can be obtained by hashing a canonical serialization
of the resulting normalized dataset, allowing for the isomorphism and digital signing
use cases. As blank node identifiers can be stable even with other changes to a graph
(dataset) in some cases it is possible to compute the difference between two graphs
(datasets) for example if changes are made only to ground triples or if new blank nodes
are introduced which do not create an automorphic confusion with other existing blank
nodes. If any information which would change the generated blank node identifier, a
resulting diff might indicate a greater set of changes than actually exists.

Editor's note: TimBL has a [design note](http://www.w3.org/DesignIssues/Diff) on problems with Diff
which should be referenced.

Editor's note: Jeremy Carroll has a [paper](http://www.hpl.hp.com/techreports/2003/HPL-2003-142.pdf) on signing RDF graphs.

## 1.2 How to Read this Document

This document is a detailed specification for an RDF dataset canonicalization algorithm.
The document is primarily intended for the following audiences:

- Software developers that want to implement an RDF dataset canonicalization algorithm.
- Masochists

To understand the basics in this specification you must be familiar with basic RDF concepts.
A working knowledge of graph theory and graph isomorphism is also recommended.


## 3. Terminology

### 3.1 General Terminology

`string`: A string is a sequence of zero or more Unicode characters.

`true` and `false`: Values that are used to express one of two possible boolean states.

`IRI`: An Internationalized Resource Identifier is a string that conforms to the syntax defined in [RFC3987](#bib-rfc3987).
    
`subject`: A subject as specified by [RDF11-CONCEPTS](#bib-rdf11-concepts).

`predicate`: A predicate as specified by [RDF11-CONCEPTS](#bib-rdf11-concepts).

`object`: An object as specified by [RDF11-CONCEPTS](#bib-rdf11-concepts).

`RDF triple`: A triple as specified by [RDF11-CONCEPTS](#bib-rdf11-concepts).

`RDF graph`: An RDF graph as specified by [RDF11-CONCEPTS](#bib-rdf11-concepts).

`graph name`: A graph name as specified by [RDF11-CONCEPTS](#bib-rdf11-concepts).

`quad`: A tuple composed of subject, predicate, object and graph name. This is a generalization of an RDF triple along with a graph name.

`RDF dataset`: A dataset as specified by [RDF11-CONCEPTS](#bib-rdf11-concepts). For the purposes of this specification, an RDF dataset is considered to be a set of quads

`blank node`: A blank node as specified by [RDF11-CONCEPTS](#bib-rdf11-concepts). In short, it is a node in a graph that is neither an IRI, nor a literal.

`blank node identifier`: A blank node identifier as specified by [RDF11-CONCEPTS](#bib-rdf11-concepts). In short, it is a string that begins with `_:` that is used as an identifier for a blank node. Blank node identifiers are typically implementation-specific local identifiers; this document specifies an algorithm for deterministically specifying them.

## 4. Canonicalization

Canonicalization is the process of transforming an input dataset to a normalized dataset.
That is, any two input datasets that contain the same information, regardless of
their arrangement, will be transformed into identical normalized dataset. The problem
requires directed graphs to be deterministically ordered into sets of nodes and edges.
This is easy to do when all of the nodes have globally-unique identifiers, but can be
difficult to do when some of the nodes do not. Any nodes without globally-unique
identifiers must be issued deterministic identifiers.

> > Strictly speaking, the normalized dataset must be serialized to be stable, as within
> > a dataset, blank node identifiers have no meaning. This specification defines a 
> > normalized dataset to include stable identifiers for blank nodes but practical 
> > uses of this will always generate a canonical serialization of such a dataset.
> > In time, there may be more than one canonicalization algorithm and, therefore,
> > for identification purposes, this algorithm is named the "Universal RDF Dataset
> > Canonicalization Algorithm 2015" or **RDNA**
> This statement is overly prescriptive and does not include normative language.
> This spec should describe the theoretical basis for graph canonicalization and
> describe behavior using normative statements. The explicit algorithms should
> follow as an informative appendix.

# 4.1 Canonicalization Algorithm Terms

`input dataset`:  The abstract RDF dataset that is provided as input to the algorithm.

`normalized dataset`: The immutable, abstract RDF dataset and set of normalized blank node identifiers that are produced as output by the algorithm. A normalized dataset is a restriction on an RDF dataset where all nodes are labeled, and blank nodes are labeled with blank node identifiers consistent with running this algorithm on a base RDF dataset. A concrete serialization of an normalized dataset MUST label all blank nodes using these stable blank node identifiers.

`identifier issuer`: An identifier issuer is used to issue new blank node identifier. It maintains a blank node identifier issuer state.

`hash`: The lowercase, hexadecimal representation of a message digest.

`hash algorithm`:  The hash algorithm used by RDNA, namely, SHA-256. 

## 4.2 Canonicalization State

When performing the steps required by the canonicalization algorithm, it is helpful
to track state in a data structure called the canonicalization state. The information
contained in the canonicalization state is described below.

`blank node to quads map`: A data structure that maps a blank node identifier
to the quads in which they appear in the input dataset.

`hash to blank nodes map`: A data structure that maps a hash to a list of
blank node identifiers.

`canonical issuer`: An identifier issuer, initialized with the prefix `_:c14n`
for issuing canonical blank node identifiers. 

> Issue
> Mapping all blank nodes to use this identifier spec means that an RDF dataset
> composed of two different RDF graphs will use different identifiers than that
> for the graphs taken independently. This may happen anyway, due to
> automorphisms or overlapping statements but an identifier based on the resulting
> hash along with an issue sequence number specific to that hash would stand a
> better chance of surviving such minor changes and allow the resulting
> information to be useful for RDF Diff. 


## 4.3 Blank Node Identifier Issuer State

During the canonicalization algorithm, it is sometimes necessary to issue new
identifiers to blank nodes. The Issue Identifier algorithm uses an identifier
issuer to accomplish this task. The information an identifier issuer needs to
keep track of is described below.

`identifier prefix`:  The identifier prefix is a string that is used at the
beginning of an blank node identifier. It should be initialized to a string
that is specified by the canonicalization algorithm. When generating a new
blank node identifier the prefix is concatenated with a identifier counter.
For example, `_:c14n` is a proper initial value for the identifier prefix
that would produce blank node identifiers like `_:c14n1`.

`identifier counter`: A counter that is appended to the identifier prefix
to create an blank node identifier. It is initialized to 0.

`issued identifiers list`: A list that tracks previously issued identifiers
in the order in which they were issued. It also tracks the existing
identifier that triggered the issuance to prevent issuing more than one
new identifier per existing identifier and to allow blank nodes to be
reassigned identifiers some time after issuance. 


## 4.4 Canonicalization Algorithm

The canonicalization algorithm converts an input dataset into a normalized
dataset. This algorithm will assign deterministic identifiers to any
blank nodes in the input dataset.

> Editor's note
> Documenting the algorithm is a WIP, various steps will become more
> detailed in time.
> 
> See the note for the “hash first degree quads algorithm”. We should
> either remove the loop based on `simple` here but indicate that the
> original design of the algorithm was to have such a loop, or leave
> it but inform implementers that it is safe to break after one iteration
> of the loop (again, indicating why). A future version of this algorithm
> should make the loop effectual.


### 4.4.2 Algorithm

1. Create the canonicalization state.
2. For every quad in input dataset:
    1. For each blank node that occurs in the quad, add a reference to the
       quad using the blank node identifier in the blank-node-to-quads map,
       creating a new entry if necessary.
    > Issue It seems that quads must be normalized, so that literals with
    > different syntactic representations but the same semantic representations
    > are merged, and that two graphs differing in the syntactic representation
    > of a literal will produce the same set of blank node identifiers.
3. Create a list of non-normalized blank node identifiers `non-normalized
   identifiers` and populate it using the keys from the blank-node-to-quads map.
4. Initialize `simple`, a boolean flag, to true.
5. While `simple` is true, issue canonical identifiers for blank nodes:
    1. Set `simple` to false.
    2. Clear hash-to-blank-nodes map.
    3. For each blank node identifier `identifier` in non-normalized identifiers:
        1. Create a hash, `hash`, according to the “Hash First Degree Quads”
           algorithm.
        2. Add `hash` and `identifier` to hash-to-blank-nodes map, creating a
           new entry if necessary.
    4. For each hash-to-identifier-list mapping in hash to blank nodes map,
       lexicographically-sorted by hash:
        1. If the length of identifier-list is greater than 1, continue to
           the next mapping.
        2. Use the “Issue Identifier” algorithm, passing `canonical issuer`
           and the single blank node identifier `identifier` in identifier-list,
           to issue a canonical replacement identifier for `identifier`.
        3. Remove `identifier` from non-normalized identifiers.
        4. Remove `hash` from the hash-to-blank-nodes-map.
        5. Set simple to true.
6. For each hash-to-identifier list mapping in hash-to-blank-nodes map,
   lexicographically-sorted by hash:
    1. Create hash path list where each item will be a result of running
       the “Hash N-Degree Quads” algorithm.
    2. For each blank node identifier `identifier` in identifier-list:
        1. If a canonical identifier has already been issued for `identifier`,
           continue to the next identifier.
        2. Create `temporary issuer`, an identifier issuer initialized with
           the prefix `_:b`.
        3. Use the “Issue Identifier” algorithm, passing `temporary issuer`
           and `identifier`, to issue a new temporary blank node identifier
           for `identifier`.
        4. Run the “Hash N-Degree Quads” algorithm, passing `temporary issuer`
           and append the result to the hash-path-list.
    3. For each result in the hash-path-list, lexicographically-sorted by
       the hash in result:
        1. For each blank node identifier, `existing identifier`, that was
           issued a temporary identifier by `identifier issuer` in `result`,
           issue a canonical identifier, in the same order, using the 
           “Issue Identifier” algorithm, passing `canonical issuer` and
           `existing identifier`. 
7. For each quad, `quad`, in input dataset:
    1. Create a copy, `quad copy`, of quad and replace any existing blank
       node identifiers using the canonical identifiers previously issued
       by `canonical issuer`.
    2. Add quad copy to the normalized dataset.
8. Return the normalized dataset.


## 4.5 Issue Identifier Algorithm

### 4.5.2 Algorithm

This algorithm issues a new blank node identifier for a given existing
blank node identifier. It also updates state information that tracks the
order in which new blank node identifiers were issued.

This algorithm takes an identifier issuer and an existing identifier as
inputs. The output is a new issued identifier. The steps of the
algorithm are:

1. If there is already an issued identifier for existing identifier in
   issued identifiers list, return it.
2. Generate issued identifier by concatenating identifier prefix with
   the string value of identifier counter.
3. Append an item to issued identifiers list that maps existing
   identifier to issued identifier.
4. Increment identifier counter.
5. Return issued identifier.

## 4.6 Hash First Degree Quads

> Editor's note
> The result of this algorithm for a particular blank node will always
> be the same. This is only true because there was a typo in the spec
> that has now been implemented by many implementations. The design of
> the algorithm was to use the assigned canonical blank node identifier,
> if available, instead of `_:a` or `_:z`, similar to how it is used
> in the related hash algorithm, but this text never made it into the
> spec before implementations moved forward. Therefore, the hashes here
> never change, making the loop based on the simple flag that calls this
> algorithm unnecessary; it needs to only run once. A future version
> of this algorithm should correct this mistake. 



## 4.7 Hash Related Blank Node


### 4.6.2 Algorithm

This algorithm takes the canonicalization state and a reference
blank node identifier as inputs.

1. Initialize `nquads` to an empty list. It will be used to store
   quads in N-Quads format.
2. Get the list of quads `quads` associated with the reference
   blank node identifier in the blank-node-to-quads map.
3. For each quad `quad` in quads:
    1. Serialize the quad in N-Quads format with the following
       special rule:
        1. If any component in `quad` is an blank node, then
           serialize it using a special identifier as follows:
            1. If the blank node's existing blank node identifier
               matches the reference blank node identifier then
               use the blank node identifier `_:a`, otherwise,
               use the blank node identifier `_:z`.
    > Issue: There exists a potential need to normalize literals to their
    > canonical representation here as well, if not done on the original
    > input dataset.
4. Sort `nquads` in lexicographical order.
4. Return the hash that results from passing the sorted, joined nquads
   through the hash algorithm.



## 4.7 Hash Related Blank Node

### 4.7.2 Algorithm

This algorithm creates a hash to identify how one blank node is related
to another. It takes the canonicalization state, a related blank node
identifier, `related`, a quad, an identifier issuer, `issuer`, and a
string position as inputs.

1. Set the identifier to use for `related`, preferring first the canonical
   identifier for related if issued, second the identifier issued by
   issuer if issued and last, if necessary, the result of the “Hash
   First Degree Quads” algorithm, passing `related`.
2. Initialize a string `input` to the value of `position`.
3. If `position` is not `g`, append `<` plus the value of the predicate
   in `quad` and `>` to `input`.
4. Append `identifier` to `input`.
5. Return the hash that results from passing `input` through the hash
   algorithm.



# # 4.8 Hash N-Degree Quads

> Editor's note: The relationship and difference between this algorithm
> and the “Hash First Degree Quads” algorithm should be better explained.
> There may also be better names for the two algorithms.
> Also the 'path' terminology could also be changed to better indicate
  what a 'path' is (a particular deterministic serialization for a
  subgraph/subdataset of nodes without globally-unique identifiers).

## 4.8.1 Overview

Usually, when trying to determine if two nodes in a graph are equivalent,
you simply compare their identifiers. However, what if the nodes don't have
identifiers? Then you must determine if the two nodes have equivalent
connections to equivalent nodes all throughout the whole graph. This is
called the “graph isomorphism problem”. This algorithm approaches this
problem by considering how one might draw a graph on paper. You can test
to see if two nodes are equivalent by drawing the graph twice. The first
time you draw the graph the first node is drawn in the center of the page.
If you can draw the graph a second time such that it looks just like the
first, except the second node is in the center of the page, then the nodes
are equivalent. This algorithm essentially defines a deterministic way to
draw a graph where, if you begin with a particular node, the graph will
always be drawn the same way. If two graphs are drawn the same way with
two different nodes, then the nodes are equivalent. A hash is used to
indicate a particular way that the graph has been drawn and can be used
to compare nodes.

This algorithm works in concert with the main Canonicalization algorithm
to produce a unique, deterministic identifier for a particular blank node.
This hash incorporates all of the information that is connected to the
blank node as well as how it is connected. It does this by creating
deterministic paths that emanate out from the blank node through any other
adjacent blank nodes.


## 4.8.2 Algorithm

> Issue: An additional input to this algorithm should be added that
> allows it to be optionally skipped and throw an error if any equivalent
> related hashes were produced that must be permuted during step 5.4.4.
> For practical uses of the algorithm, this step should never be encountered
> and could be turned off, disabling canonizing datasets that include a
> need to run it as a security measure.

The inputs to this algorithm are the canonicalization state, the identifier
for the blank node to recursively hash quads for, and path identifier `issuer`
which is an identifier issuer that issues temporary blank node identifiers.
The output from this algorithm will be a hash and the identifier issuer used
to help generate it.

1. Create a hash-to-related-blank-nodes map for storing hashes that identify
   related blank nodes.
2. Get a reference, `quads`, to the list of quads in the blank-node-to-quads
   map for the key `identifier`.
3. For each `quad` in quads:
   1. For each component in quad, where component is the subject, object or
      graph name and it is a blank node that is not identified by `identifier`:
      1. Set `hash` to the result of the “Hash Related Blank Node” algorithm,
         passing the blank node identifier for component as `related`, quad,
         path identifier issuer as `issuer`, and position as either s, o, or
         g based on whether component is a subject, object, graph name,
         respectively.
      2. Add a mapping of hash to the blank-node-identifier for `component`
         to `hash` to related-blank-nodes map, adding an entry as necessary.
4. Create an empty string, `data` to hash.
5. For each related hash-to-blank-node-list mapping in hash-to-related-blank-nodes
   map, sorted lexicographically by related hash:
   1. Append the related hash to the data to hash.
   2. Create a string `chosen path`.
   3. Create an `unset chosen issuer` variable.
   4. For each permutation of blank-node-list:
      1. Create a copy of issuer, `issuer copy`.
      2.  Create a string `path`.
      3.  Create recursion-list to store blank node identifiers that must
          be recursively processed by this algorithm.
      4.  For each related in permutation:
          1. If a canonical identifier has been issued for related, append
             it to `path`.
          2. Otherwise:
             1. If issuer copy has not issued an identifier for `related`,
                append `related` to recursion-list.
             2. Use the “Issue Identifier” algorithm, passing `issuer copy`
                and `related` and append the result to `path`.
          3. If `chosen path` is not empty and the length of path is greater
             than or equal to the length of `chosen path` and `path` is
             lexicographically greater than `chosen path` then skip to the
             next permutation.
      5. For each `related` in recursion-list:
         1. Set result to the result of recursively executing the “Hash
            N-Degree Quads” algorithm, passing `related` for `identifier` and 
            `issuer copy` for path identifier `issuer`.
         2. Use the “Issue Identifier” algorithm, passing `issuer copy` and
            `related` and append the result to `path`.
         3. Append `<`, the hash in result and `>` to `path`.
         4. Set `issuer copy` to the identifier issuer in `result`.
         5. If `chosen path` is not empty and the length of `path` is greater
            than or equal to the length of `chosen path` and path is
            lexicographically greater than `chosen path` then skip to the next
            permutation.
      6. If `chosen path` is empty or `path` is lexicographically less than
         `chosen path`, set `chosen path` to `path` and `chosen issuer` to
         `issuer copy`.
    5. Append `chosen path` to `data` to hash.
    6. Replace `issuer`, by reference, with `chosen issuer`.
6. Return `issuer` and the hash that results from passing data to hash through
   the hash algorithm.
