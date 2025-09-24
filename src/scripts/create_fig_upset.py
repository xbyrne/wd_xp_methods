"""
create_fig_upset.py
====================
Script to create the upset plot for the DZs identified by the different methods.
"""

import sys

import check_polluted as cp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import upsetplot

FIGURE_NUMBER = int(sys.argv[1])

# ============
# Loading data

# Random forests
garciazamora25 = pd.read_csv(
    "../data/external/previous_work/garciazamora25.csv", index_col=0
)
random_forest_DZs = garciazamora25.index[
    ["Z" in sp for sp in garciazamora25["SPPred"]]
].values

# Gradient boosted trees
vincent24 = pd.read_csv("../data/external/previous_work/vincent24.csv", index_col=0)
gradient_boosted_trees_DZs = vincent24.index[vincent24["SpType"] == "DZ "].values

# SOMs
fl = np.load("../data/processed/som_DZs.npz")
som_DZs = fl["ids"]

# UMAP
umap_DZs = pd.read_csv(
    "../data/external/previous_work/secret/umap_polluted_all.csv", index_col=0
)["GaiaEDR3"]

# tSNE
fl = np.load("../data/processed/polluted_islands.npz")
tsne_DZs = np.concatenate([fl["cool_DZs"], fl["warm_DZs"]])


# ============
# Creating objects for upsetplot

DZ_dict = {
    "RF": random_forest_DZs,
    "GTB": gradient_boosted_trees_DZs,
    "SOM*": som_DZs,
    "UMAP": umap_DZs,
    r"$t$SNE": tsne_DZs,
}

known_DZ_dict = {
    key: np.array([idd for idd in id_array if cp.is_polluted(idd) == 1])
    for key, id_array in DZ_dict.items()
}

upset_df = upsetplot.from_contents(DZ_dict)
upset_df["pollution_status"] = [
    "Known polluted" if cp.is_polluted(idd) == 1 else "All" for idd in upset_df.id
]

# ============
# Plotting

fg, ax = plt.subplots(figsize=(8, 4))

up = upsetplot.UpSet(
    upset_df,
    min_subset_size=15,
    sort_categories_by="input",
    intersection_plot_elements=0,
)
up.add_stacked_bars(by="pollution_status", colors=["k", "g"])
up.plot(fig=fg)
ax.axis("off")

totals_ax = fg.axes[3]
totals_ax.barh(
    known_DZ_dict.keys(),
    [len(known_DZ_dict[key]) for key in known_DZ_dict.keys()],
    color="g",
    height=0.54,  # Idk why this is the right height
)


# ============
# Restyling

# Improving legibility of overlap axis
overlap_ax = fg.axes[4]

overlap_ax.set_ylim(0, 230)
overlap_ax.set_yticks([0, 50, 100, 150, 200], minor=False)
overlap_ax.tick_params(axis="y", direction="in", which="both")

overlap_ax.annotate("(578)", xy=(0.54, 240), fontsize=8, annotation_clip=False)

# Fixing the legend
handles, labels = overlap_ax.get_legend_handles_labels()
overlap_ax.legend(
    handles[::-1],
    labels[::-1],
    loc="upper right",
    ncol=2,
)


# Improving legibility of ticks on totals axis
totals_ax.set_xticks([0, 500, 1000], minor=False)
totals_ax.tick_params(axis="x", direction="in", which="both", labelsize=8)
totals_ax.set_axisbelow(True)

# ============

fg.savefig(f"../tex/figures/fig{FIGURE_NUMBER}_upset.png", dpi=300, bbox_inches="tight")
