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


def dim_reduce(data, method, preprocessor=lambda x: x, **kwargs):
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

    return reducer.fit_transform(preprocessor(data))


if __name__ == "__main__":

    print("Loading data...")
    fl = np.load("../data/interim/xp_coeffs.npz")
    ids = fl["ids"]
    xp_coeffs = fl["xp"]
    xp_coeffs = pp.divide_Gflux(xp_coeffs, ids)

    print("Performing dimensionality reduction...")
    print("UMAP...")
    umap_embedding = dim_reduce(xp_coeffs, "umap")  # ~45s

    print("tSNE...")
    tsne_embedding = dim_reduce(xp_coeffs, "tsne")  # ~4m

    print("Saving embeddings...")
    np.savez_compressed(
        "../data/processed/umap_xp.npz", ids=ids, embedding=umap_embedding
    )
    np.savez_compressed(
        "../data/processed/tsne_xp.npz", ids=ids, embedding=tsne_embedding
    )
