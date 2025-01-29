"""
create_fig5_egMSCVspectra.py
============================
Shows a few example reconstructed XP spectra of MS stars and CVs
"""

import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# Selected IDs to show
STAR_IDS = [731743061507469568, 1304503239926166400, 3152255890729006848]
CV_IDS = [1289860214647954816, 1332378466733219456, 3873721404734233344]

# =============================================================================
# Load the spectra
fl = np.load("../data/interim/xp_sampled.npz")  # Sampled spectra
ids = fl["ids"]
wlen = fl["wlen"]
flux = fl["flux"]

# =============================================================================
# Plot

fg, axs = plt.subplots(2, 1, figsize=(6, 4), gridspec_kw={"hspace": 0}, sharex=True)

for ax, ids_ in zip(axs, [STAR_IDS, CV_IDS]):
    for i, idd in enumerate(ids_):
        ax.plot(wlen, flux[ids == idd][0] + i * 1e-17, lw=1, c="k")
        # Add some Balmer lines
        ax.axvline(656.3, c="r", ls=":", lw=0.5)
        ax.axvline(486.1, c="r", ls=":", lw=0.5)
        ax.axvline(434.0, c="r", ls=":", lw=0.5)

    ax.set_yticks([])
    ax.margins(x=0.01)

axs[0].set_title("MS stars", fontsize=14, x=0.97, y=0.78, ha="right")

ax = axs[1]
ax.set_title("CVs", fontsize=14, x=0.97, y=0.78, ha="right")
ax.set_xlabel("Wavelength [nm]", fontsize=14)
ax.set_ylabel("Flux [arbitrary]", fontsize=14, y=1)

# Annotate the Balmer lines
ax.annotate(r"H$\alpha$", xy=(620, 2.65e-17), c="r")
ax.annotate(r"H$\beta$", xy=(442, 2.65e-17), c="r")
ax.annotate(r"H$\gamma$", xy=(392, 2.65e-17), c="r")

fg.savefig("../tex/figures/fig5_starcvspectra.png", dpi=300, bbox_inches="tight")
