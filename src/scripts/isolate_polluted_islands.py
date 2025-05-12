"""
isolate_polluted_islands.py
===========================
Script to use DBSCAN to isolate the Gaia DR3 IDs of the polluted islands
"""

import numpy as np
from sklearn.cluster import DBSCAN

fl = np.load("../data/processed/tsne_xp.npz")
ids = fl["ids"]
tsne_embedding = fl["embedding"]

dbscan = DBSCAN(eps=2, min_samples=30)
dbscan.fit(tsne_embedding)

cool_DZs = ids[dbscan.labels_ == 4]
warm_DZs = ids[dbscan.labels_ == 6]

np.savez_compressed(
    "../data/processed/polluted_islands.npz",
    cool_DZs=cool_DZs,
    warm_DZs=warm_DZs,
)
