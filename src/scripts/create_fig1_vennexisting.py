"""
create_fig1_vennexisting.py
===========================
Script to create Venn diagrams to compare the samples of polluted WDs
identified by García-Zamora+23, Vincent+24, and Kao+24.
"""

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn3

import evaluate_existing_methods as eem

pd.options.mode.chained_assignment = None  # Turning off annoying .loc warning

# --------------------------
# Loading datasets

# García-Zamora+23
gz23 = pd.read_csv("../data/external/previous_work/garciazamora23.csv", index_col=0)

gz23_DZs = gz23.query('SPPred.str.contains("Z")')  # Select the DZs
gz23_DZs["is_polluted"] = -1  # Initialize the is_polluted column
for gid in gz23_DZs.index:  # Check if objects are known to be polluted
    gz23_DZs.loc[gid, "is_polluted"] = eem.check_whether_obj_polluted(gid)

# Vincent+24
vincent24 = pd.read_csv("../data/external/previous_work/vincent24.csv", index_col=0)
vincent24["SpType"] = vincent24["SpType"].apply(
    lambda x: str(x).strip()  # Remove annoying leading/trailing spaces
)
vincent24_DZs = vincent24.query('SpType == "DZ"')
vincent24_DZs["is_polluted"] = -1
for gid in vincent24_DZs.index:
    vincent24_DZs.loc[gid, "is_polluted"] = eem.check_whether_obj_polluted(gid)

# Kao+24
kao24_DZs = pd.read_csv(
    "../data/external/previous_work/secret/umap_polluted_all.csv", index_col=1
)
kao24_DZs = kao24_DZs[[]]  # Just need the index (Gaia IDs)
kao24_DZs["is_polluted"] = -1
for gid in kao24_DZs.index:
    kao24_DZs.loc[gid, "is_polluted"] = eem.check_whether_obj_polluted(gid)


# --------------------------
# Venn diagram
fg, axs = plt.subplots(1, 2, figsize=(8, 4), gridspec_kw={"wspace": 0})
venn3(
    subsets=(
        set(gz23_DZs.index.astype(str)),
        set(vincent24_DZs.index.astype(str)),
        set(kao24_DZs.index.astype(str)),
    ),
    set_labels=("", "", ""),
    ax=axs[0],
)
venn3(
    subsets=(
        set(gz23_DZs.query("is_polluted == -1").index.astype(str)),
        set(vincent24_DZs.query("is_polluted == -1").index.astype(str)),
        set(kao24_DZs.query("is_polluted == -1").index.astype(str)),
    ),
    set_labels=("", "", ""),
    ax=axs[1],
)
# Change font sizes for the labels
for ax in axs:
    for txt in ax.texts:
        txt.set_fontsize(14)
# Titles
axs[0].set_title("All identified", fontsize=20)
axs[1].set_title("Unknown pollution", fontsize=20, y=0.97)
# Hack a legend: make legend handles for three shaded circles
handles = []
for color in ["r", "g", "b"]:
    handles.append(
        plt.Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor=color,
            markersize=10,
            alpha=0.5,
        )
    )
axs[1].legend(
    handles,
    ["García-Zamora+23", "Vincent+24", "Kao+24"],
    loc="lower right",
    fontsize=12,
)

fg.savefig("../tex/figures/fig1_vennexisting.pdf", bbox_inches="tight")
