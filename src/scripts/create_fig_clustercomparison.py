"""
create_fig_clustercomparison.py
================================
Compares the effective temperatures of the two DZ clusters identified.
"""

import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

FIGURE_NUMBER = int(sys.argv[1])

# Loading data
gf21 = pd.read_csv("../data/interim/gf21_filtered_moredata.csv", index_col=0)

fl = np.load("../data/processed/polluted_islands.npz")
cool_DZs = fl["cool_DZs"]
warm_DZs = fl["warm_DZs"]

cool_TeffH = gf21.loc[cool_DZs].TeffH / 1e3
warm_TeffH = gf21.loc[warm_DZs].TeffH / 1e3

# Plotting
BINS = np.arange(5.5, 13, 0.5)

fg, ax = plt.subplots(figsize=(6, 3))

ax.hist(
    [cool_TeffH, warm_TeffH],
    color=["orange", "r"],
    stacked=True,
    bins=BINS,
    label=["'Cool' island", "'Warm' island"],
)

ax.set_xlabel(r"Fitted $T_\mathrm{eff}$ [$10^3~\text{K}$]", fontsize=14)
ax.xaxis.set_inverted(True)
ax.set_xticks(BINS[1::2])
ax.set_yticks([])
ax.tick_params(labelsize=12, length=4)
ax.legend(fontsize=12)

fg.savefig(
    f"../tex/figures/fig{FIGURE_NUMBER}_clustercomparison.png",
    dpi=300,
    bbox_inches="tight",
)
