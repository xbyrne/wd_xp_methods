"""
create_fig2_tsneembedding.py
===========================
Script to visualise the tSNE embedding of the Gaia XP spectra
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.cluster import DBSCAN

fl = np.load("../data/processed/tsne_xp.npz")
ids = fl["ids"]
tsne_embedding = fl["embedding"]

fl = np.load("../data/processed/umap_xp.npz")
umap_embedding = fl["embedding"]

isp = np.load("../data/interim/xp_coeffs.npz")["is_polluted"]

dbscan = DBSCAN(eps=2, min_samples=30)
dbscan.fit(tsne_embedding)

fg, axs = plt.subplot_mosaic(
    [["tsne_unlabelled", "tsne_isp"], ["tsne_clustered", "umap"], ["cbar", "cbar"]],
    figsize=(10, 10),
    gridspec_kw={"wspace": 0, "height_ratios": [1, 1, 0.05], "hspace": 0},
)

axs["tsne_unlabelled"].scatter(
    tsne_embedding[:, 0], tsne_embedding[:, 1], c="k", s=0.1, alpha=0.5
)

ax = axs["tsne_isp"]
# Known polluted
ax.scatter(
    tsne_embedding[isp == -1, 0],
    tsne_embedding[isp == -1, 1],
    c="k",
    s=1,
    alpha=0.1,
)
# Known non-polluted
ax.scatter(
    tsne_embedding[isp == 0, 0],
    tsne_embedding[isp == 0, 1],
    c="b",
    s=1,
    alpha=0.1,
)
# Unknown
ax.scatter(
    tsne_embedding[isp == 1, 0],
    tsne_embedding[isp == 1, 1],
    c="r",
    s=1,
)
ax.scatter([], [], c="r", s=20, label="KP")
ax.scatter([], [], c="b", s=20, alpha=0.5, label="KNP")
ax.scatter([], [], c="k", s=20, alpha=0.5, label="U")
ax.legend(loc="lower left", fontsize=12)

ax = axs["tsne_clustered"]
dcmp = plt.cm.viridis
cols = [
    dcmp(0),
    dcmp(0.1),
    dcmp(0.2),
    dcmp(0.3),
    "orange",
    dcmp(0.4),
    "r",
    dcmp(0.5),
    dcmp(0.6),
    dcmp(0.7),
    dcmp(0.8),
    "grey",
]

for i in np.unique(dbscan.labels_):
    ax.scatter(
        tsne_embedding[dbscan.labels_ == i, 0],
        tsne_embedding[dbscan.labels_ == i, 1],
        color=cols[i],
        s=0.1,
        alpha=0.5,
    )

cmap = mcolors.ListedColormap([cols[-1]] + cols[:-1])
cbar = plt.colorbar(
    plt.cm.ScalarMappable(cmap=cmap), cax=axs["cbar"], orientation="horizontal"
)
cbar.set_ticks(np.linspace(1 / len(cols) / 2, 1 - 1 / len(cols) / 2, len(cols)))
cbar.set_ticklabels(np.unique(dbscan.labels_), fontsize=12)
cbar.set_label(r"$t$SNE cluster label", fontsize=14)

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
        ax.text(0.025, 0.92, f"({chr(97+i)})", fontsize=16, transform=ax.transAxes)


fg.savefig("../tex/figures/fig2_tsneembedding.png", bbox_inches="tight", dpi=300)
