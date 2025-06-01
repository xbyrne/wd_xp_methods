"""
create_fig_whytwoislands.py
============================
Plot a figure attempting to explain why the two islands are split.
"""

import sys

import matplotlib.pyplot as plt
import numpy as np

FIGURE_NUMBER = int(sys.argv[1])

# Load data
fl = np.load("../data/processed/polluted_islands.npz")
cool_DZs = fl["cool_DZs"]
warm_DZs = fl["warm_DZs"]


# Plotting
fg, axs = plt.subplots(1, 4, figsize=(12, 3), gridspec_kw={"wspace": 0})
FRACTION_OTHER_SOURCES = [0, 0.04, 0.10, 0.25]

for ax, fraction in zip(axs, FRACTION_OTHER_SOURCES):
    fl = np.load(
        f"../data/processed/tsne_xp_polluted_islands_plus_fraction{fraction:.2f}.npz"
    )
    partial_ids = fl["ids"]
    embedding = fl["embedding"]

    is_warm_DZ = np.isin(partial_ids, warm_DZs)
    is_cool_DZ = np.isin(partial_ids, cool_DZs)

    ax.scatter(
        embedding[~is_warm_DZ & ~is_cool_DZ, 0],
        embedding[~is_warm_DZ & ~is_cool_DZ, 1],
        c="k",
        s=1,
        alpha=0.1,
    )
    ax.scatter(
        embedding[is_cool_DZ, 0],
        embedding[is_cool_DZ, 1],
        c="orange",
        s=1,
    )
    ax.scatter(
        embedding[is_warm_DZ, 0],
        embedding[is_warm_DZ, 1],
        c="r",
        s=1,
    )
    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_title(rf"$f={fraction:.2f}$", fontsize=14, x=0.82, y=0)

axs[0].annotate("(a)", xy=(0.04, 0.88), xycoords="axes fraction", fontsize=16)
axs[1].annotate("(b)", xy=(0.13, 0.88), xycoords="axes fraction", fontsize=16)
axs[2].annotate("(c)", xy=(0.16, 0.89), xycoords="axes fraction", fontsize=16)
axs[3].annotate("(d)", xy=(0.04, 0.88), xycoords="axes fraction", fontsize=16)

fg.suptitle(
    r"$t$SNE(polluted candidates and a fraction $f$ of other sources)", fontsize=16
)

fg.savefig(
    f"../tex/figures/fig{FIGURE_NUMBER}_whytwoislands.png", dpi=300, bbox_inches="tight"
)
