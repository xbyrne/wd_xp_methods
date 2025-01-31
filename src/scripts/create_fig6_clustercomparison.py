"""
create_fig6_clustercomparison.py
================================
Compares the XP spectra and effective temperatures of the two DZ clusters identified
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN

# =============================================================================
# Load the data

# tSNE embedding
fl = np.load("../data/processed/tsne_xp.npz")
ids = fl["ids"]
tsne_embedding = fl["embedding"]

# Sampled spectra
fl = np.load("../data/interim/xp_sampled.npz")
assert (fl["ids"] == ids).all()  # No need to reload
wlen = fl["wlen"]
flux = fl["flux"]

# Temperature data
gf21 = pd.read_csv("../data/interim/gf21_filtered.csv", index_col=0)


# =============================================================================
# Select DZs
def dbscan_label(embedding, **kwargs):
    """
    DBSCAN clustering on the embedding
    """
    dbscan = DBSCAN(**kwargs)
    dbscan.fit(embedding)
    return dbscan.labels_


labels = dbscan_label(tsne_embedding, eps=2, min_samples=30)

cluster4_ids = ids[labels == 4]
cluster6_ids = ids[labels == 6]
cluster4_flux = flux[np.isin(ids, cluster4_ids)]
cluster6_flux = flux[np.isin(ids, cluster6_ids)]
cluster4_TeffH = gf21.loc[cluster4_ids, "TeffH"]
cluster6_TeffH = gf21.loc[cluster6_ids, "TeffH"]

# =============================================================================
# Plot

fg, axs = plt.subplots(1, 2, figsize=(12, 4), gridspec_kw={"wspace": 0.05})

# Median spectra

ax = axs[0]
ax.plot(wlen, np.median(cluster4_flux, axis=0), "orange", lw=2, label="Cluster #4")
ax.plot(wlen, np.median(cluster6_flux, axis=0), "r", lw=2, label="Cluster #6")

ax.axvline(393.366, c="k", ls="--")
ax.axvline(396.847, c="k", ls="--", label="Ca II H&K")

ax.set_xlabel("Wavelength [nm]", fontsize=14)
ax.set_ylabel("Flux [arbitrary]", fontsize=14, x=0.1, y=0.5)
ax.set_title("Median spectra", fontsize=17)
ax.set_xlim(350, 700)
ax.legend(fontsize=14)

# Temperature distributions

BINS = np.arange(5.5, 13, 0.5)
ax = axs[1]
ax.hist(cluster4_TeffH / 1e3, bins=BINS, density=True, color="orange", alpha=0.6)
ax.hist(cluster6_TeffH / 1e3, bins=BINS, density=True, color="r", alpha=0.6)

ax.set_xlabel(r"$T_{\rm eff}$ [$10^3\,\text{K}$]", fontsize=14)
ax.set_title(r"$T_{\rm eff}$ distributions", fontsize=17)
ax.set_xlim(5.2, 12.8)


for ax in axs:
    ax.set_yticks([])
    ax.tick_params(
        axis="both",
        which="major",
        labelsize=12,
        direction="in",
        length=5,
        top=True,
        right=True,
    )

fg.savefig("../tex/figures/fig6_clustercomparison.png", dpi=300, bbox_inches="tight")
