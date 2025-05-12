"""
create_fig6_upset.py
====================
Script to create the upset plot for the DZs identified by the different methods
"""

import check_polluted as cp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import upsetplot

# ============
# Loading data

# Random forests
garciazamora23 = pd.read_csv(
    "../data/external/previous_work/garciazamora23.csv", index_col=0
)
random_forest_DZs = garciazamora23.index[
    ["Z" in sp for sp in garciazamora23["SPPred"]]
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
    "Known polluted" if cp.is_polluted(idd) == 1 else "All"
    for idd in upset_df.id
    # We want 'Total' to show up the total number of DZs; we're hacking the stackplot
]

# ============
# Plotting

fg, ax = plt.subplots(figsize=(8, 4))

up = upsetplot.UpSet(
    upset_df,
    min_subset_size=20,
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

# For some reason, the overlap plot legend has the colours the wrong way around
# Here we swap them around
overlap_ax = fg.axes[4]

# Improving legitibility of ticks on overlap axis
overlap_ax.set_yticks([0, 300, 600], minor=False)
overlap_ax.set_yticks([100, 200, 400, 500], minor=True)
overlap_ax.grid(axis="y", which="minor", alpha=0.3)
overlap_ax.tick_params(axis="y", direction="in", which="both")


# Improving legitibility of ticks on totals axis
totals_ax.set_xticks([0, 500, 1000], minor=False)
totals_ax.tick_params(axis="x", direction="in", which="both", labelsize=8)
totals_ax.set_axisbelow(True)

# ============

fg.savefig("../tex/figures/fig6_upset.png", dpi=300, bbox_inches="tight")
