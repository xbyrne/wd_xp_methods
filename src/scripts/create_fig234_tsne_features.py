"""
create_fig234_tsnefeatures.py
==============================
Creates further figures, identifying interesting features
in the tSNE embedding
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import check_polluted as cp

# =============================================================================
# Load data

fl = np.load("../data/processed/tsne_xp.npz")
ids = fl["ids"]  # (107 164,)
embedding = fl["embedding"]  # (107 164, 2)

gf21 = pd.read_csv("../data/interim/gf21_filtered.csv", index_col=0)


# =============================================================================
# Fig 2: DA sequence

# -----------------------------------------------------------------------------
# Load the colour data for the DAs

DA_ids = cp.gf21sdss.query('specClass == "DA"').index.values  # (18 927,)
DA_ids_in_sample = np.intersect1d(DA_ids, ids)  # (7 423,)
is_DA = np.isin(ids, DA_ids_in_sample)  # (107 164,), 7 423 True

DA_mags = gf21.loc[ids[is_DA], ["BPmag", "RPmag"]]  # (7 423, 2)
DA_BPRPs = (DA_mags["BPmag"] - DA_mags["RPmag"]).values  # (7 423,)

# -----------------------------------------------------------------------------
# Plot

fg, ax = plt.subplots(figsize=(6, 5))
ax.scatter(embedding[:, 0], embedding[:, 1], c="k", s=0.1, alpha=0.1)

is_DA = np.isin(ids, DA_ids_in_sample)  # (107 164,), 7 423 True
DAsc = ax.scatter(
    embedding[is_DA, 0], embedding[is_DA, 1], c=DA_BPRPs, cmap="inferno_r", s=4
)

cbar = plt.colorbar(DAsc, ax=ax, pad=0)
cbar.set_label(r"BP $ - $ RP", fontsize=14, labelpad=0)

ax.set_xticks([])
ax.set_yticks([])

fg.tight_layout()
fg.savefig("../tex/figures/fig2_DAsequence.png", dpi=300, bbox_inches="tight")

# =============================================================================
# Fig 3: DBs, DCs, DQs

# -----------------------------------------------------------------------------
# Select the DBs, DCs, DQs


def class_mask(class_str):
    "Creates a mask for objects in a given class, acc. GF+21"
    class_ids = cp.gf21sdss.query(f'specClass == "{class_str}"').index.values
    return np.isin(ids, np.intersect1d(gf21.index, class_ids))


isDB = class_mask("DB")
isDC = class_mask("DC")
isDQ = class_mask("DQ")

# -----------------------------------------------------------------------------
# Plot

DB_COLOUR = "b"
DC_COLOUR = "#1eff19"
DQ_COLOUR = "#2e8674"
DB_MARKER = "^"
DC_MARKER = "o"
DQ_MARKER = "D"

fg, ax = plt.subplots(figsize=(6, 6))

ax.scatter(embedding[:, 0], embedding[:, 1], c="k", s=0.1, alpha=0.1)

for mask, colour, marker in zip(
    [isDB, isDC, isDQ],
    [DB_COLOUR, DC_COLOUR, DQ_COLOUR],
    [DB_MARKER, DC_MARKER, DQ_MARKER],
):
    ax.scatter(
        embedding[mask, 0],
        embedding[mask, 1],
        c=colour,
        marker=marker,
        s=20,
    )

ax.set_xticks([])
ax.set_yticks([])


def hack_handle(c, m, s):
    "Hacks a legend handle for a scatter plot"
    return ax.scatter([], [], c=c, marker=m, s=s)


ax.legend(
    handles=[
        hack_handle(colour, marker, s)
        for colour, marker, s in zip(
            [DB_COLOUR, DC_COLOUR, DQ_COLOUR],
            [DB_MARKER, DC_MARKER, DQ_MARKER],
            [50, 50, 50],
        )
    ],
    labels=["DB", "DC", "DQ"],
    loc="upper left",
    fontsize=12,
)

fg.savefig("../tex/figures/fig3_DBCQ.png", dpi=300, bbox_inches="tight")

# =============================================================================
# Fig 4: MS stars and binaries

# -----------------------------------------------------------------------------
# Select the MS stars and binaries

isSTAR = class_mask("STAR")
isbinary = class_mask("DA_MS") | class_mask("DB_MS") | class_mask("DC_MS")
isCV = class_mask("CV")

# -----------------------------------------------------------------------------
# Plot

STAR_COLOUR = "k"
BINARY_COLOUR = "orange"
CV_COLOUR = "r"
STAR_MARKER = "*"
BINARY_MARKER = "*"
CV_MARKER = "x"

fg, ax = plt.subplots(figsize=(6, 6))
ax.scatter(embedding[:, 0], embedding[:, 1], c="k", s=0.1, alpha=0.1)

ax.scatter(
    embedding[isSTAR, 0],
    embedding[isSTAR, 1],
    c=STAR_COLOUR,
    marker=STAR_MARKER,
    s=50,
    edgecolors="none",
)
ax.scatter(
    embedding[isbinary, 0],
    embedding[isbinary, 1],
    c=BINARY_COLOUR,
    marker=BINARY_MARKER,
    s=50,
    edgecolors="none",
)
ax.scatter(
    embedding[isCV, 0], embedding[isCV, 1], c=CV_COLOUR, marker=CV_MARKER, s=30, lw=1
)

ax.set_xticks([])
ax.set_yticks([])

ax.legend(
    handles=[
        hack_handle(colour, marker, s)
        for colour, marker, s in zip(
            [STAR_COLOUR, BINARY_COLOUR, CV_COLOUR],
            [STAR_MARKER, BINARY_MARKER, CV_MARKER],
            [80, 80, 50],
        )
    ],
    labels=["MS star", "WD+MS", "CV"],
    fontsize=12,
    loc="upper left",
)

fg.savefig("../tex/figures/fig4_ms.png", dpi=300, bbox_inches="tight")
