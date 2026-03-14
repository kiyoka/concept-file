"""Cosine similarity search over .concept files."""

import math


def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def cosine_distance(a, b):
    """Compute cosine distance (1 - similarity) between two vectors."""
    return 1.0 - cosine_similarity(a, b)
