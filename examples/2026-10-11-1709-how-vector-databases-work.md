---
title: "How Vector Databases Work"
date: 2026-10-11
topic: "How vector databases work"
score: 9
drafts: 2
flagged: false
model: claude-haiku-5-5
critic_model: claude-sonnet-5-5
---

# How Vector Databases Work

Traditional databases are built to find exact matches. You ask for every customer whose postcode is 10001, and the system returns the rows that match. Much of the world's data, including text, images, audio, and product descriptions, has no obvious structure for that kind of lookup. A vector database is designed for this problem. According to Machine Learning Mastery, the core idea is to convert unstructured data into embeddings, which are vectors that can be compared, so that items can be searched by similarity rather than exact value.

## Embeddings and similarity

An embedding works a little like coordinates on a map. Each item is represented as a list of numbers, and items with related meaning end up near one another in that numerical space. Two sentences about dogs will land close together, while a sentence about tax law will sit far away. An embedding has many dimensions, far more than the three we can easily picture, but the principle is the same at any size: distance reflects relatedness. A search query is embedded the same way, and the database looks for stored vectors closest to it.

## Approximate nearest neighbor search

The challenge is scale. Comparing a query against every stored vector gives exact results but becomes slow as the collection grows. Approximate nearest neighbor (ANN) search addresses this by trading a small amount of exactness for a large gain in speed. The results may not always be the mathematically closest matches, but they are close enough, and they arrive much sooner.

## HNSW

One well-known index structure is HNSW, which stands for Hierarchical Navigable Small World. The original paper describes it as a graph-based structure for incremental approximate K-nearest-neighbor search. A helpful way to picture it is a road network with express routes. The top layer of the graph has only a few long-range connections between widely spaced points, so a search can cover large distances quickly. Lower layers add denser connections among nearby points, letting the search narrow in on the best local matches. The paper describes this as navigable small-world graphs with a controllable hierarchy.

The paper's authors also claim that the method's search complexity scales logarithmically, which they present as a major improvement over earlier approaches. This is the authors' own claim. AI/TLDR says that HNSW and IVF can let vector databases search millions of embeddings in milliseconds, a performance claim that comes from the source itself.

## Metadata filtering

Real applications rarely search by similarity alone. A shopping site might want the most similar jackets that are also in stock and under a set price. These conditions are metadata filters, which apply to attributes stored alongside each vector. The AI Database Blog explains that metadata filters are evaluated alongside the vector search rather than as a separate step afterward. Filtering only after the search could leave very few usable results. To keep filtered queries fast, the same source describes payload indexes on metadata fields, and it mentions bitmap filtering as one filtering technique.

## Putting it together

A vector database stores embeddings, builds an index such as HNSW to navigate them, and stores metadata for filtering. When a query arrives, it is converted into a vector. The index guides the search toward nearby candidates, filters are applied, and the closest matches are returned. The result is a system that finds things by meaning rather than by exact wording.

## Sources

- Machine Learning Mastery, "Vector Databases Explained in 3 Levels of Difficulty" — https://machinelearningmastery.com/vector-databases-explained-in-3-levels-of-difficulty/
- arXiv:1603.09320, HNSW paper — https://arxiv.org/abs/1603.09320
- AI/TLDR, "Approximate Nearest Neighbors" — https://ai-tldr.dev/learn/embeddings-vector-databases/similarity-search-indexing/approximate-nearest-neighbors/
- The AI Database Blog, "Metadata Filtering Architecture" — https://theaidatabaseblog.com/learn/metadata-filtering-architecture/