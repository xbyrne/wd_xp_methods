"""
create_fig_coaddedspectrum.py
=============================
Creates a figure showing the coadded spectrum of the `unknown' sources selected by tSNE.
"""

import sys

import check_polluted as cp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import preprocessors as pp

FIGURE_NUMBER = int(sys.argv[1])

fl = np.load("../data/interim/xp_sampled.npz")
ids = fl["ids"]
WLEN = fl["wlen"]
flux = fl["flux"]
normalised_flux = pp.divide_Gflux(flux, ids)

# tSNE unknown sources
fl = np.load("../data/processed/polluted_islands.npz")
tsne_pwds = np.concatenate((fl["cool_DZs"], fl["warm_DZs"]))
tsne_unknown_ids = np.array([id_ for id_ in tsne_pwds if cp.is_polluted(id_) == -1])

# Sources identified by just tSNE
garciazamora23 = pd.read_csv(
    "../data/external/previous_work/garciazamora23.csv", index_col=0
)
random_forest_pwds = garciazamora23.index[
    ["Z" in sp for sp in garciazamora23["SPPred"]]
].values

vincent24 = pd.read_csv("../data/external/previous_work/vincent24.csv", index_col=0)
gradient_tree_boosting_pwds = vincent24.index[vincent24["SpType"] == "DZ "].values

umap_pwds = pd.read_csv(
    "../data/external/previous_work/secret/umap_polluted_all.csv", index_col=0
)["GaiaEDR3"].values

som_pwds = np.load("../data/processed/som_DZs.npz")["ids"]

just_tsne_pwds = np.array(
    [
        id_
        for id_ in tsne_unknown_ids
        if id_ not in random_forest_pwds
        and id_ not in gradient_tree_boosting_pwds
        and id_ not in umap_pwds
        and id_ not in som_pwds
    ]
)


# Function to stack spectra
def stack_normalise_spectra(ids_to_stack):
    """
    Selects the XP spectra corresponding to `ids_to_stack`, and stacks them
    """
    spectra = normalised_flux[np.isin(ids, ids_to_stack)]
    stacked_spectra = np.mean(spectra, axis=0)
    # Arbitrarily rescale between 0 and 1
    scaled_stacked_spectra = (stacked_spectra - np.min(stacked_spectra)) / (
        np.max(stacked_spectra) - np.min(stacked_spectra)
    )
    return scaled_stacked_spectra


# Plot
fg, ax = plt.subplots(figsize=(8, 3))

# Ca lines
ax.axvline(393.4, color="k", ls="--", lw=2, c="r", alpha=0.3)
ax.axvline(396.8, color="k", ls="--", lw=2, c="r", alpha=0.3)
ax.annotate(r"Ca II", xy=(405, 1.31), fontsize=12, c="r")

# Spectra
ax.plot(WLEN, stack_normalise_spectra(tsne_unknown_ids), color="k")
ax.plot(WLEN, stack_normalise_spectra(just_tsne_pwds) + 0.4, color="b")

# Annotations
ax.annotate(
    "Selected " r"$\it{only}$ by $t$SNE",
    xy=(550, 1.1),
    c="b",
    fontsize=12,
)
ax.annotate(
    "Selected by " r"$t$SNE" "\n(and by other methods)",
    xy=(470, 0.25),
    c="k",
    fontsize=12,
)

ax.set_xlim(330, 780)
ax.tick_params(axis="x", labelsize=12, direction="in", size=5)
ax.set_xlabel("Wavelength [nm]", fontsize=14)

ax.set_yticks([])
ax.set_ylabel("Flux [arbitrary]", fontsize=14)

fg.savefig(
    f"../tex/figures/fig{FIGURE_NUMBER}_coaddedspectrum.png",
    dpi=300,
    bbox_inches="tight",
)
