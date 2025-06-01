"""
create_fig_tsneembedding.py
===========================
Script to visualise the tSNE embedding of the Gaia XP spectra.
"""

import sys

import check_polluted as cp
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

FIGURE_NUMBER = int(sys.argv[1])

fl = np.load("../data/processed/tsne_xp.npz")
ids = fl["ids"]
tsne_embedding = fl["embedding"]

isp = np.array([cp.is_polluted(id_) for id_ in ids])


fg, ax = plt.subplots(
    figsize=(6, 6),
    gridspec_kw={"wspace": 0, "hspace": 0},
)

# Unknown
ax.scatter(
    tsne_embedding[isp == -1, 0],
    tsne_embedding[isp == -1, 1],
    c="k",
    s=1,
    alpha=0.05,
)
# Known non-polluted
ax.scatter(
    tsne_embedding[isp == 0, 0],
    tsne_embedding[isp == 0, 1],
    c="r",
    s=1,
    alpha=0.1,
)
# Known polluted
ax.scatter(
    tsne_embedding[isp == 1, 0],
    tsne_embedding[isp == 1, 1],
    c="g",
    s=1,
)

# Highlighting polluted islands
ellipse = mpl.patches.Ellipse((37, -12), 24, 16, color="k", fill=False, lw=2)
ax.add_artist(ellipse)
ellipse = mpl.patches.Ellipse((-4, -39), 18, 12, color="k", fill=False, lw=2)
ax.add_artist(ellipse)
ax.annotate("Polluted islands", xy=(20, -63), fontsize=14)

for x1, y1, dx, dy in [
    (23, -55, -15, 10),
    (37, -55, 0, 29),
]:
    ax.arrow(
        x1,
        y1,
        dx,
        dy,
        color="k",
        alpha=1,
        lw=4,
        head_width=3,
        head_length=2,
    )

# Legend
ax.scatter([], [], c="g", s=20, label="Known polluted")
ax.scatter([], [], c="r", s=20, alpha=0.5, label="Known non-polluted")
ax.scatter([], [], c="k", s=20, alpha=0.5, label="Unknown")
ax.legend(loc="upper left", fontsize=12)

ax.set_xticks([])
ax.set_yticks([])
fg.savefig(
    f"../tex/figures/fig{FIGURE_NUMBER}_tsneembedding.png", bbox_inches="tight", dpi=300
)
