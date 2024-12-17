"""
umap_tsne_xp.py
===============
Performs dimensionality reduction on the Gaia XP coefficients.
Applies both UMAP and tSNE, saving the embeddings to separate npz files.
"""

import numpy as np
from umap import UMAP
from sklearn.manifold import TSNE

import preprocessors as pp


def dim_reduce(data, method, **kwargs):
    """
    Perform dimensionality reduction on the input data.
    `method` must be either 'umap' or 'tsne'.
    `preprocessor` should be a function that preprocesses the raw np array.
    **kwargs are passed to the respective dimensionality reduction method.
    """
    assert method in ["umap", "tsne"], 'Invalid method; must be "umap" or "tsne".'

    if method == "umap":
        reducer = UMAP(**kwargs)
    else:  # method == "tsne"
        reducer = TSNE(**kwargs)

    return reducer.fit_transform(data)


if __name__ == "__main__":

    print("Loading data...")
    fl = np.load("../data/interim/xp_coeffs.npz")
    ids = fl["ids"]
    xp = fl["xp"]
    pxp = pp.divide_Gflux(xp, ids)  # Normalise by G-band flux

    print("Performing dimensionality reduction...")
    print("UMAP...")
    umap_embedding = dim_reduce(pxp, "umap", n_neighbors=25, min_dist=0.05)  # ~45s
    print("Saving...")
    np.savez_compressed(
        "../data/processed/umap_xp.npz", ids=ids, embedding=umap_embedding
    )

    print("tSNE...")
    tsne_embedding = dim_reduce(pxp, "tsne", perplexity=50)  # ~4m
    print("Saving...")
    np.savez_compressed(
        "../data/processed/tsne_xp.npz", ids=ids, embedding=tsne_embedding
    )
