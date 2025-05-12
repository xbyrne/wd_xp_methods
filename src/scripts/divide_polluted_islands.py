"""
divide_polluted_islands.py
==========================
Runs tSNE with the polluted islands and a fraction of the rest of the objects, to show
how it is the other islands which cause the split in the two islands.
"""

import numpy as np
import preprocessors as pp
from umap_tsne_xp import dim_reduce

# Load XP spectra
fl = np.load("../data/interim/xp_coeffs.npz")
ids = fl["ids"]
xp = fl["xp"]
pxp = pp.divide_Gflux(xp, ids)

# Load polluted candidates (acc. tSNE)
fl = np.load("../data/processed/polluted_islands.npz")
cool_DZs = fl["cool_DZs"]
warm_DZs = fl["warm_DZs"]
DZs = np.concatenate([cool_DZs, warm_DZs])

FRACTIONS_OTHER_SOURCES = [0, 0.04, 0.10, 0.25]
other_sources = np.array([source for source in ids if source not in DZs])

for fraction in FRACTIONS_OTHER_SOURCES:
    print(f"Running tSNE with {fraction:.2f} of other sources...")
    np.random.seed(42)
    # Select a fraction of the other sources
    n_other = int(fraction * len(other_sources))
    fraction_of_other_sources = np.random.choice(
        other_sources, size=n_other, replace=False
    )

    # Combine with the polluted islands
    selected_ids = np.concatenate([DZs, fraction_of_other_sources])
    selected_ids = ids[np.isin(ids, selected_ids)]  # Get in same order as in `ids`
    selected_pxps = pxp[np.isin(ids, selected_ids)]

    # Run tSNE on the subset
    embedding = dim_reduce(selected_pxps, "tsne", perplexity=50)

    # Save the results
    np.savez_compressed(
        f"../data/processed/tsne_xp_polluted_islands_plus_fraction{fraction:.2f}.npz",
        ids=selected_ids,
        embedding=embedding,
    )
