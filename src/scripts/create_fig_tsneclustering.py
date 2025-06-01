"""
create_fig_tsneclustering.py
===========================
Script to visualise the clustering in the tSNE embedding.
"""

import sys

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import DBSCAN

FIGURE_NUMBER = int(sys.argv[1])

fl = np.load("../data/processed/tsne_xp.npz")
ids = fl["ids"]
tsne_embedding = fl["embedding"]

fl = np.load("../data/processed/umap_xp.npz")
umap_embedding = fl["embedding"]

dbscan = DBSCAN(eps=2, min_samples=30)
dbscan.fit(tsne_embedding)

fg, axs = plt.subplot_mosaic(
    [["tsne_clustered", "umap"], ["cbar", "cbar"]],
    figsize=(10, 5),
    gridspec_kw={"wspace": 0, "height_ratios": [1, 0.05], "hspace": 0},
)

ax = axs["tsne_clustered"]
dcmp = plt.cm.viridis
cols = [
    dcmp(0.08),
    dcmp(0.16),
    dcmp(0.24),
    dcmp(0.32),
    "orange",
    dcmp(0.4),
    "r",
    dcmp(0.48),
    dcmp(0.56),
    dcmp(0.64),
    dcmp(0.72),
    dcmp(0.0),
]

for i in np.unique(dbscan.labels_):
    ax.scatter(
        tsne_embedding[dbscan.labels_ == i, 0],
        tsne_embedding[dbscan.labels_ == i, 1],
        color=cols[i],
        s=0.1,
        alpha=0.5,
    )

cmap = mcolors.ListedColormap(
    [cols[4], cols[6], cols[-1]] + cols[0:4] + [cols[5]] + cols[7:-1]
)
cbar = plt.colorbar(
    plt.cm.ScalarMappable(cmap=cmap), cax=axs["cbar"], orientation="horizontal"
)
cbar.set_ticks([1 / 24, 3 / 24])
cbar.set_ticklabels(["Cool\nDZs", "Warm\nDZs"], fontsize=12)
cbar.set_label(r"DBSCAN clustering of $t$SNE embedding", fontsize=14, labelpad=-12)

ax = axs["umap"]
for i in np.unique(dbscan.labels_):
    ax.scatter(
        umap_embedding[dbscan.labels_ == i, 0],
        umap_embedding[dbscan.labels_ == i, 1],
        color=cols[i],
        s=0.1,
        alpha=0.5,
    )

for ax in axs.values():
    if ax != axs["cbar"]:
        ax.set_xticks([])
        ax.set_yticks([])

# (a), (b), (c), (d)
for i, ax in enumerate(axs.values()):
    if ax != axs["cbar"]:
        ax.text(0.025, 0.92, f"({chr(97 + i)})", fontsize=16, transform=ax.transAxes)


fg.savefig(
    f"../tex/figures/fig{FIGURE_NUMBER}_tsneclustering.png",
    bbox_inches="tight",
    dpi=300,
)
